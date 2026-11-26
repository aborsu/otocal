# otocal — handoff for Claude Code

E-ink family calendar on a Raspberry Pi Zero W (hostname `otocal`, user `otocal`), built with an 11-year-old.
Code lives in `~/otocal` (git, pushed to a private GitHub repo). Identifiers and comments are in French.
**Keep the code simple** — explicit requirement from the owner. Prefer small, readable changes over abstractions.

## Hardware

- Waveshare 12.48" e-Paper Module **(B)** (black/white/red, 1304x984), driver in
  `~/12.48inch-e-paper/RaspberryPi/python/lib` (`epd12in48b`). It bit-bangs SPI on GPIO via lgpio:
  **kernel SPI must stay disabled** (`raspi-config nonint do_spi 1`), otherwise `xGpioHandleRequest: Invalid argument`.
  The lib was patched: `time.clock()` -> `time.perf_counter()`. A full refresh takes ~130 s on the Zero.
  The driver's BUSY wait has no timeout and can hang forever if the panel doesn't answer.
- PiSugar 3 (1200 mAh) on the back of the Pi via pogo pins. I2C addresses 0x57 (MCU) and 0x68 (RTC).
  `pisugar-server` is restricted to `--tcp 127.0.0.1:8423 --uds /tmp/pisugar-server.sock`
  (web UI and ws removed) in `/etc/default/pisugar-server`.
- The Pi Zero has no RTC of its own: at boot the clock is whatever was saved at shutdown, then jumps.

## Files in ~/otocal

| File | Role |
| --- | --- |
| `cycle.py` | Whole wake cycle, run by `otocal.service` at boot (as root) |
| `evenements.py` | `charger_evenements()` — CalDAV fetch from Nextcloud, window = Monday of current week + 28 days; initials per calendar, skips `Personnel`, dedup, birthdays red, multi-day `Famille` events = holidays |
| `dessin.py` | `dessiner()` -> (black, red) 1-bit images; `python3 dessin.py` writes `apercu.png` preview |
| `afficher.py` | Draw + send to the panel (needs `sudo`) |
| `meteo.py` | Open-Meteo (Brussels) + hand-drawn weather icons |
| `phrase.py` + `phrases.txt` | Joke of the day, shuffled deck persisted in `.pioche_blagues.json` |
| `barre_batterie.py` | Battery gauge, red below 20 % |
| `pisugar.py` | `commande(cmd)` over TCP 127.0.0.1:8423, `batterie()` |
| `reveil.py` | `regler_reveil()` — next of 06:00 / 11:30 / 18:00, `rtc_alarm_set <iso> 127` (single alarm, repeats daily; date part of `rtc_alarm_time` is filler `2000-01-01`) |
| `otocal.service` | Copy of `/etc/systemd/system/otocal.service` (oneshot, After=network-online, pisugar-server) |

Nextcloud credentials: `/home/otocal/.config/otocal/nextcloud.env` (absolute path because the cycle runs as root). Never commit it.

## Cycle behaviour (cycle.py)

1. Time sync from PiSugar RTC (`rtc_rtc2pi`)
2. Log battery, draw (12 retries for network), display
3. Set next alarm (the owner added a retry loop every ~1.5 min — **read the current file before editing**)
4. Power off, unless: `~/otocal/RESTER_ALLUME` exists, or battery charging, or the alarm could not be set (stays on rather than sleeping forever)

## Open problems — please fix

1. **Reset RTC trusted as real time.** On Nov 26 the battery had run flat; the PiSugar RTC reset to its default
   (`2020-01-22 ~01:00`) and `rtc_rtc2pi` set the Pi to January. The events window was computed with that date,
   NTP fixed the clock during the network calls, and the grid was then drawn with the correct date:
   right days, no events.
   Fix: new `horloge.py` with `mettre_a_l_heure(journal)` — wait up to ~90 s for
   `timedatectl show -p NTPSynchronized --value` == `yes`, then `rtc_pi2rtc`; without network, use `rtc_rtc2pi`
   only if the RTC year is >= 2026. In `cycle.py`, replace step 1 with it and skip drawing if the time is unknown.
2. **Date read twice.** `dessiner()` calls `charger_evenements()` before reading `date.today()`.
   Read the date once at the start of `dessiner()` and pass it to `charger_evenements()`.
3. **Intermittent I2C failures lasting hours** (`I2C not connected`, `os error 5` / `os error 121`) on Nov 20, 24 and 25,
   while `i2cdetect -y 1` still shows 0x57/0x68 and direct `i2cget` reads succeed. Restarting `pisugar-server` did not help;
   a reboot fixed it immediately (Nov 24). Each failure keeps the Pi awake and drains the battery.
   Fix: if the PiSugar is unreachable at startup, reboot once and retry, with a persistent counter
   (e.g. `/var/lib/otocal/reboots`, reset after a successful cycle) so it can never loop.
   Hardware side (owner): re-seat the PiSugar, check pogo pins; check whether
   `dtparam=i2c_arm_baudrate=50000` is in `/boot/firmware/config.txt`.
4. Optional: timeout around the panel's BUSY wait so a hung display can't block the alarm/poweroff steps.

## Workflow

- Preview first: `python3 dessin.py` then on the Mac `scp otocal@otocal.local:otocal/apercu.png ~/Desktop/`.
- Test the full cycle with the escape hatch: `touch ~/otocal/RESTER_ALLUME && sudo python3 cycle.py`.
- Logs: `journalctl -u otocal -b`, `journalctl -u pisugar-server -b`, `journalctl --list-boots`.
- PiSugar state: `cd ~/otocal && python3 pisugar.py`.
- Before leaving it on battery: `python3 reveil.py` must print `rtc_alarm_set: done`, then `rm -f ~/otocal/RESTER_ALLUME && sudo poweroff`.
- Commit after each change: `git add . && git commit -m "..." && git push`.
