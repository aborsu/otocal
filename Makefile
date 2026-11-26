# Shortcuts to work from the Mac. The code runs on the Pi (ssh otocal).
PI = otocal
EXCLUDE = --exclude .git --exclude __pycache__ --exclude apercu.png --exclude .pioche_blagues.json \
          --exclude RESTER_ALLUME --exclude '*.bak' --exclude HANDOFF.md --exclude CLAUDE.md \
          --exclude .claude --exclude Makefile

.PHONY: sync preview logs status alarm deploy

# Copy the code from the Mac to the Pi (no commit)
sync:
	rsync -a $(EXCLUDE) ./ $(PI):otocal/

# Draw on the Pi and fetch the image (note: uses up one joke from the deck)
preview: sync
	ssh $(PI) 'cd otocal && python3 dessin.py'
	scp -q $(PI):otocal/apercu.png apercu.png
	@echo "-> apercu.png"

# Logs since the last boot
logs:
	ssh $(PI) 'journalctl -u otocal -b --no-pager; journalctl -u pisugar-server -b --no-pager | tail -20'

# Battery, charging, RTC time, NTP sync, escape hatch
status:
	ssh $(PI) 'cd otocal && python3 pisugar.py; python3 -c "from pisugar import commande; print(commande(\"get battery_v\"))"; date; timedatectl show -p NTPSynchronized; ls RESTER_ALLUME 2>/dev/null'

# Set the next wake-up alarm (must print rtc_alarm_set: done)
alarm: sync
	ssh $(PI) 'cd otocal && python3 reveil.py'

# After commit + push on the Mac: put the Pi exactly on origin/main
deploy:
	git push
	ssh $(PI) 'cd otocal && git fetch -q && git reset -q --hard origin/main && git log --oneline -1'
