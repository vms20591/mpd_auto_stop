from __future__ import print_function
import time
import threading
import subprocess
import re
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
import json
import signal
import sys
import argparse
from datetime import datetime, timedelta
try:
    # python 2
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    # python 3
    from http.server import BaseHTTPRequestHandler, HTTPServer

# utils
def xstr(text):
    try:
        text = str(text or "")
        text = text.strip()
        
        return text
    except Exception as exp:
        return ""

def xint(text, default=0):
    try:
        return int(xstr(text))
    except Exception as exp:
        return default

def xfloat(text, default=0.0):
    try:
        return float(xstr(text))
    except Exception as exp:
        return default

class Log(object):
    @staticmethod
    def print_ok(format, *args):
        format = xstr(format)

        print(format.format(*args))

# exceptions
class TimerExistsError(Exception): pass

class InvalidTimerStateError(Exception): pass

# timer
class TimerStatus(object):
    @staticmethod
    def started():
        return "started"

    @staticmethod
    def stopped():
        return "stopped"

class Timer(object):
    def __init__(self):
        self._duration_pattern = re.compile("^([0-9]*)(\.?)([0-9]+)([smh])$")
        self._status = TimerStatus.stopped()
        self._started = None
        self._duration = 0
        self._timer = None
        self._lock = threading.Lock()

    @property
    def status(self):
        return self._status

    @property
    def mpd_host(self):
        return self._mpd_host

    @mpd_host.setter
    def mpd_host(self, value):
        self._mpd_host = value

    @property
    def mpd_port(self):
        return self._mpd_port

    @mpd_port.setter
    def mpd_port(self, value):
        self._mpd_port = value

    def _worker(self):
        try:
            output = subprocess.check_output(["mpc", "--host={0}".format(self._mpd_host), "--port={0}".format(self._mpd_port), "pause"])

            Log.print_ok(output)
        except subprocess.CalledProcessError as exp:
            Log.print_ok("Error calling command: {0}", exp.message)
        finally:
            self.stop()

    def _parse_duration(self, duration):
        duration = xstr(duration)
        duration = duration.lower()
        match = self._duration_pattern.match(duration)
        
        if not match:
            raise ValueError("Invalid duration: " + duration)

        duration = xfloat("".join(match.groups()[:3]))
        
        unit = xstr(match.groups()[3])

        if unit == "m":
            duration = duration * 60
        
        if unit == "h":
            duration = duration * 60 * 60

        return duration

    def _stop_timer(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _get_remaining_time(self):
        now = datetime.now()
        timer_endtime = self._started + timedelta(seconds=self._duration)

        remaining_time = (timer_endtime - now).total_seconds()

        return remaining_time

    def get_status(self):
        result = {
            "status": self.status
        }

        if self.status == TimerStatus.started():
            result["remaining_time"] = "{0} seconds".format(self._get_remaining_time())
        
        return result

    def start(self, duration):
        with self._lock:
            if self.status == TimerStatus.started():
                now = datetime.now()
                timer_endtime = self._started + timedelta(seconds=self._duration)

                if timer_endtime < now:
                    self.stop()

                    Log.print_ok("Timer has already ended, but state is started")

                    raise InvalidTimerStateError("Timer has already ended, but state is started")

                remaining_time = (timer_endtime - now).total_seconds()

                return {
                    "remaining_time": "{0} seconds".format(remaining_time)
                }

            self._stop_timer()

            self._status = TimerStatus.started()
            self._started = datetime.now()
            self._duration = duration = self._parse_duration(duration)

            self._timer = threading.Timer(duration, self._worker)
            self._timer.start()

            Log.print_ok("Timer started with duration {0} seconds", duration)

            return {
                "remaining_time": "{0} seconds".format(self._get_remaining_time())
            }

    def stop(self):
        with self._lock:
            if self.status == TimerStatus.started():
                self._stop_timer()

                self._status = TimerStatus.stopped()
                self._started = None
                self._duration = 0

                Log.print_ok("Timer stopped")

        return {}

    def restart(self):
        with self._lock:
            if self.status == TimerStatus.started():
                self._stop_timer()

                self._started = datetime.now()

                self._timer = threading.Timer(self._duration, self._worker)
                self._timer.start()

                Log.print_ok("Timer restarted with duration {0} seconds", self._duration)

                return {
                    "remaining_time": "{0} seconds".format(self._get_remaining_time())
                }
            else:
                Log.print_ok("Can't restart a stopped timer")

                raise InvalidTimerStateError("Can't restart a stopped timer")

    def extend(self, duration):
        with self._lock:
            if self.status == TimerStatus.started():
                self._stop_timer()

                remaining_time = self._get_remaining_time()
                self._duration = duration = remaining_time + self._parse_duration(duration)

                self._timer = threading.Timer(duration, self._worker)
                self._timer.start()

                Log.print_ok("Timer extended with duration {0} seconds", duration)

                return {
                    "remaining_time": "{0} seconds".format(duration)
                }
            else:
                Log.print_ok("Can't extend a stopped timer")

                raise InvalidTimerStateError("Can't extend a stopped timer")

# server
class Route(object):
    def __init__(self, pattern, handler):
        self._pattern = pattern
        self._handler = handler

    @property
    def pattern(self):
        return self._pattern

    @property
    def handler(self):
        return self._handler

class TimerRequestHandler(BaseHTTPRequestHandler):
    routes = None

    def _get_routes(self):
        if not self.routes:
            self.routes = []
            self.routes.append(Route(re.compile('/?$'), self._index))
            self.routes.append(Route(re.compile('/timer$'), self._timer_status))
            self.routes.append(Route(re.compile('/timer/(?P<duration>[\.0-9a-zA-Z]+)/start$'), self._timer_start))
            self.routes.append(Route(re.compile('/timer/stop$'), self._timer_stop))
            self.routes.append(Route(re.compile('/timer/restart$'), self._timer_restart))
            self.routes.append(Route(re.compile('/timer/(?P<duration>[\.0-9a-zA-Z]+)/extend$'), self._timer_extend))
            self.routes.append(Route(re.compile('.*'), self._match_all))
        
        return self.routes

    def _match_route(self, path):
        for route in self._get_routes():
            match = route.pattern.match(path)

            if match:
                return (match, route)

    def do_GET(self):
        path = urlparse.urlparse(self.path).path
        (match, route) = self._match_route(path)

        (status, headers, result) = route.handler(match)

        for header in headers.items():
            self.send_header(header[0], header[1])

        self.send_response(status)
        self.end_headers()
        self.wfile.write(result.encode("utf8"))

        return
    
    def _index(self, match):
        content = r"""
        <html>
            <header>
                <title>MPD Auto Stop</title>
                <style>
                    body {
                        font-family: sans-serif, verdana;
                    }

                    pre {
                        margin-bottom: -10px;
                    }
                </style>
            </header>
            <body>
                <div>
                    <pre>,-.-.,---.,--.     ,---..   .--.--,---.    ,---.--.--,---.,---.</pre>
                    <pre>| | ||---'|   |    |---||   |  |  |   |    `---.  |  |   ||---'</pre>
                    <pre>| | ||    |   |    |   ||   |  |  |   |        |  |  |   ||    </pre>
                    <pre>` ' '`    `--'     `   '`---'  `  `---'    `---'  `  `---'`    </pre>
                </div>
                <br/>
                <div>
                    <div>The following actions are available,</div>
                    <ul>
                        <li>
                            Status - /timer
                        </li>
                        <li>
                            Start Timer - /timer/<time>/start. Ex: /timer/3600s/start, /timer/1h/start, /timer/60m/start
                        </li>
                        <li>
                            Stop Timer - /timer/stop
                        </li>
                        <li>
                            Reset Timer - /timer/reset
                        </li>
                        <li>
                            Extend Timer - /timer/<time>/extend. Ex: /timer/1800s/extend, /timer/0.5h/extend, /timer/30m/extend
                        </li>
                    </ul>
                </div>
            </body>
        </html>
        """

        headers = {
            "Content-Type": "text/html"
        }

        return (200, headers, content)

    def _timer_status(self, match):
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            result = timer.get_status()

            return (200, headers, json.dumps(result))
        except Exception as exp:
            result = {
                "error": exp.message
            }

            return (500, headers, json.dumps(result))

    def _timer_start(self, match):
        headers = {
            "Content-Type": "application/json"
        }

        try:
            duration = match.groupdict()["duration"]
            result = timer.start(duration)

            return (200, headers, json.dumps(result))
        except ValueError as exp:
            result = {
                "error": exp.message
            }

            return (400, headers, json.dumps(result))
        except InvalidTimerStateError as exp:
            result = {
                "error": exp.message
            }

            return (400, headers, json.dumps(result))
        except Exception as exp:
            result = {
                "error": exp.message
            }

            return (500, headers, json.dumps(result))

    def _timer_stop(self, match):
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            result = timer.stop()

            return (200, headers, json.dumps(result))
        except Exception as exp:
            result = {
                "error": exp.message
            }

            return (500, headers, json.dumps(result))

    def _timer_restart(self, match):
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            result = timer.restart()

            return (200, headers, json.dumps(result))
        except InvalidTimerStateError as exp:
            result = {
                "error": exp.message
            }

            return (400, headers, json.dumps(result))
        except Exception as exp:
            result = {
                "error": exp.message
            }

            return (500, headers, json.dumps(result))

    def _timer_extend(self, match):
        headers = {
            "Content-Type": "application/json"
        }

        try:
            duration = match.groupdict()["duration"]
            result = timer.extend(duration)

            return (200, headers, json.dumps(result))
        except ValueError as exp:
            result = {
                "error": exp.message
            }

            return (400, headers, json.dumps(result))
        except InvalidTimerStateError as exp:
            result = {
                "error": exp.message
            }

            return (400, headers, json.dumps(result))
        except Exception as exp:
            result = {
                "error": exp.message
            }

            return (500, headers, json.dumps(result))

    def _match_all(self, match):
        return (404, {}, "Not found")

# app
class App(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.stopped = 0

    def _signal_handler(self, signal_number, frame):
        Log.print_ok("Received signal {0}, stopping server...", signal_number)
        self.stopped = 1

    def _register_signals(self):
        signal.signal(signal.SIGTERM, self._signal_handler)

    def start(self):
        self.server = HTTPServer((self.host, self.port), TimerRequestHandler)
        self._register_signals()
        
        Log.print_ok("Starting server @ {0}:{1}, use <Ctrl-C> to stop", self.host, self.port)

        try:
            while not self.stopped:
                self.server._handle_request_noblock()
            
            Log.print_ok("Stopped...")
        except KeyboardInterrupt:
            self.server.server_close()
            Log.print_ok("Stopped...")

# arguments
def parse_args():
    parser = argparse.ArgumentParser(description="MPD Auto Stop - auto stopping Music Player Daemon, by setting up timers")
    parser.add_argument("-a", "--host", help="Host to run the server on [default: 0.0.0.0]", default="0.0.0.0")
    parser.add_argument("-p", "--port", help="Port to the server should listen on [default: 9090]", default=9090, type=int)
    parser.add_argument("-mh", "--mpd-host", help="Host where mpd runs [default: localhost]", default="localhost")
    parser.add_argument("-mp", "--mpd-port", help="Port where mpd listens on [default: 6600]", default=6600, type=int)

    return parser.parse_args()

# main
timer = Timer()

if __name__ == "__main__":
    args = parse_args()

    timer.mpd_host = args.mpd_host
    timer.mpd_port = args.mpd_port

    app = App(args.host, args.port)
    app.start()
