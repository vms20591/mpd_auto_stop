# MPD Auto Stop

``` text
,-.-.,---.,--.     ,---..   .--.--,---.    ,---.--.--,---.,---.
| | ||---'|   |    |---||   |  |  |   |    `---.  |  |   ||---'
| | ||    |   |    |   ||   |  |  |   |        |  |  |   ||
` ' '`    `--'     `   '`---'  `  `---'    `---'  `  `---'`
```

A pure python web utility for auto stopping *Music Player Daemon*, by setting up timers.

This is simple project that I wanted to use on my *Raspberrypi*, since I've connected it with my speakers via *AUX* and use it as a cheap bluetooth alternative.

---

## Requirements

* `Python 2.7+` (tested with `v2.7.13`) or `Python 3.5+` (tested with `v3.5.3`)
* `mpc` (issues the actual commands to `mpd`)

## Installation

Copy or simlink `mpd-auto-stop.py` to a location that's on your `PATH`.

## systemd installation (optional) (GNU/Linux)

### system

* Copy `mpd-auto-start.service.sample` to `/etc/systemd/system/mpd-auto-start.service`
* **enable** - `sudo systemctl enable mpd-auto-start`
* **start** - `sudo systemctl start mpd-auto-start`
* **stop** - `sudo systemctl stop mpd-auto-start`

### user

* Copy `mpd-auto-start.service.sample` to `/etc/systemd/user/mpd-auto-start.service`
* **enable** - `systemctl --user enable mpd-auto-start`
* **start** - `systemctl --user start mpd-auto-start`
* **stop** - `systemctl --user stop mpd-auto-start`

**Note:** To run on different host & port, update `ExecStart` in service file. **Example:** `ExecStart=/usr/bin/mpd-auto-stop --host 0.0.0.0 --port 5000`. Refer to usage section for more details.

## Usage

```text
usage: python mpd-auto-stop.py [-h] [-a HOST] [-p PORT] [-mh MPD_HOST] [-mp MPD_PORT]

MPD Auto Stop - auto stopping Music Player Daemon, by setting up timers

optional arguments:
  -h, --help            show this help message and exit
  -a HOST, --host HOST  Host to run the server on [default: 0.0.0.0]
  -p PORT, --port PORT  Port to the server should listen on [default: 9090]
  -mh MPD_HOST, --mpd-host MPD_HOST
                        Host where mpd runs [default: localhost]
  -mp MPD_PORT, --mpd-port MPD_PORT
                        Port where mpd listens on [default: 6600]
```

## Example

``` text
python mpd-auto-stop.py --host 127.0.0.1 --port 10000 --mpd-host 192.168.0.10 --mpd-port 16600
```

## Available APIs

* `/` - displays index page with available actions
* `/timer` - displays status of the timer. **Example:** `{"status": "stopped"}` or `{"status": "started", "remaining_time": "1000 seconds"}`
* `/timer/<duration>/start` - starts a timer to auto stop *Music Player Daemon*. **Example:** `/timer/1000s/start`, `/timer/1h/start`, `/timer/1.5h/start`, `/timer/60m/start`
* `/timer/<duration>/stop` - stops any existing timers.
* `/timer/<duration>/restart` - restarts any existing timers
* `/timer/<duration>/extend` - extends an existing timer. **Example:** `/timer/1000s/extend`, `/timer/1h/extend`, `/timer/1.5h/extend`, `/timer/60m/extend`
