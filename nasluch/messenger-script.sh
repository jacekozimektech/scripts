#!/bin/sh

/bin/sh -c "nc -ulk 127.0.0.1 9981 | python3 -u /home/jacek/projects/scripts/nasluch/bot_osp.py | ts '[%Y-%m-%d %H:%M:%S]' 2>/dev/null | tee -a /home/jacek/nasluch/mess_bot.log"
