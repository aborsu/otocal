# otocal

E-ink family calendar on a Raspberry Pi Zero W, built with an 11-year-old.
**Keep the code simple** (owner's explicit requirement): small, readable changes, no abstractions.
**New code, comments, log messages, commands and Makefile targets are in English** (owner's rule).
Existing code is in French; text shown on the e-ink screen stays French.

Open problems and full hardware notes: see `HANDOFF.md` (untracked).

## Where things run

- Edit on the Mac (`~/src/otocal`, source of truth). Code runs on the Pi: `ssh otocal`, repo in `~/otocal`.
- The Mac has no deps (PIL, caldav, dotenv, epd driver); never try to run the code locally.
- Pi: Python 3.13, Debian packages (`python3-pil`, `python3-caldav`...). No pip installs.
- `sudo` on the Pi needs a password: anything needing root (`cycle.py`, `afficher.py`, `systemctl`)
  must be run by the owner. Give them the exact command.
- Paths in the code are absolute (`/home/otocal/otocal/...`) because the cycle runs as root.
- Nextcloud credentials: `/home/otocal/.config/otocal/nextcloud.env` on the Pi. Never read into logs or commit.

## Make targets (from the Mac)

| Command | What it does |
| --- | --- |
| `make sync` | rsync code to the Pi (no commit) |
| `make preview` | send + `python3 dessin.py` on the Pi + fetch `apercu.png` (read it to check). Uses up one joke from the deck |
| `make logs` | `otocal` + `pisugar-server` logs for the current boot |
| `make status` | battery, charging, RTC time, NTP sync, escape hatch |
| `make alarm` | set the next alarm (must print `rtc_alarm_set: done`) |
| `make deploy` | `git push`, then reset the Pi to `origin/main` |

Commit on the Mac, then `make deploy`. Don't commit on the Pi.

## Hardware gotchas

- Waveshare 12.48" (B) panel, 1304x984 black/white/red, driver `epd12in48b` in
  `~/12.48inch-e-paper/RaspberryPi/python/lib`. Kernel SPI must stay disabled. Full refresh about 130 s.
  BUSY wait has no timeout.
- PiSugar 3: `pisugar-server` on TCP 127.0.0.1:8423 (`pisugar.py`). Intermittent I2C failures happen.
- No RTC on the Pi: the clock is wrong until the PiSugar RTC or NTP fixes it. The PiSugar RTC resets to 2020 when the battery runs flat.
- Escape hatch: `~/otocal/RESTER_ALLUME` keeps the Pi on after a cycle. Remove it before leaving it on battery.
- Full cycle test (owner, on the Pi): `touch ~/otocal/RESTER_ALLUME && sudo python3 cycle.py`.
