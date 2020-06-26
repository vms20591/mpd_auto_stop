```
,-.-.,---.,--.     ,---..   .--.--,---.    ,---.--.--,---.,---.
| | ||---'|   |    |---||   |  |  |   |    `---.  |  |   ||---'
| | ||    |   |    |   ||   |  |  |   |        |  |  |   ||    
` ' '`    `--'     `   '`---'  `  `---'    `---'  `  `---'` 
```

A pure python web utility for auto stopping *Music Player Daemon*, by setting up timers.

This is simple project that I wanted to use on my *Raspberrypi*, since I've connected it with my speakers via *AUX* and use it as a cheap bluetooth alternative.

---

## Requirements

* Python 2.7

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

**Note:** To run on different host & port, update `ExecStart` in service file. **Example:** `ExecStart=/usr/bin/mpd-auto-stop 0.0.0.0 5000`

## Usage

```
python mpd-auto-stop.py [host] [port]
```

**Note:** By default, `host` is `0.0.0.0`, `port` is `9090`

## Available APIs

* `/` - displays index page with available actions
* `/timer` - displays status of the timer. **Example:** `{"status": "stopped"}` or `{"status": "started", "remaining_time": "1000 seconds"}`
* `/timer/<duration>/start` - starts a timer to auto stop *Music Player Daemon*. **Example:** `/timer/1000s/start`, `/timer/1h/start`, `/timer/1.5h/start`, `/timer/60m/start`
* `/timer/<duration>/stop` - stops any existing timers.
* `/timer/<duration>/restart` - restarts any existing timers
* `/timer/<duration>/extend` - extends an existing timer. **Example:** `/timer/1000s/extend`, `/timer/1h/extend`, `/timer/1.5h/extend`, `/timer/60m/extend`
