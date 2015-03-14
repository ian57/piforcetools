#!/usr/bin/python
# Written by TravistyOJ (AKA Capaneus)

import os, collections, signal, sys, subprocess, socket
import triforcetools
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from time import *
#time, sleep

ips = ["192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5"] # Add or remove as many endpoints as you want
#rom_dir = "/boot/roms/"  # Set absolute path of rom files ending with trailing /
rom_dir = "/home/pi/roms/"  # Set absolute path of rom files ending with trailing /
commands = ["Ping Netdimm", "Change Target"]

# Define a signal handler to turn off LCD before shutting down
def handler(signum = None, frame = None):
    lcd = Adafruit_CharLCDPlate()
    lcd.clear()
    lcd.stop()
    sys.exit(0)
signal.signal(signal.SIGTERM , handler)

# Determine hardware revision and initialize LCD
revision = "unknown"
cpuinfo = open("/proc/cpuinfo", "r")
for line in cpuinfo:
    item = line.split(':', 1)
    if item[0].strip() == "Revision":
        revision = item[1].strip()
if revision.startswith('a'):
    lcd = Adafruit_CharLCDPlate(busnum = 1)
else:
    lcd = Adafruit_CharLCDPlate()

col = (('Red' , lcd.RED) , ('Yellow', lcd.YELLOW), ('Green' , lcd.GREEN),
           ('Teal', lcd.TEAL), ('Blue'  , lcd.BLUE)  , ('Violet', lcd.VIOLET),
            ('On'    , lcd.ON))

lcd.backlight(lcd.YELLOW)
lcd.begin(16, 2)
lcd.message(" Piforce Tools\n   Ver. 1.4")
for c in col:
   lcd.backlight(c[1])
   sleep(0.5)

#sleep(2)

# Try to import game list script, if it fails, signal error on LCD
try:
    from gamelist import games
except (SyntaxError, ImportError) as e:
    lcd.clear()
    lcd.backlight(lcd.RED)
    lcd.message("Game List Error!\n  Check Syntax")
    sleep(5)
    games = {}

# Purge game dictionary of game files that can't be found
missing_games = []
for key, value in games.iteritems():
    if not os.path.isfile(rom_dir+value):
        missing_games.append(key)
for missing_game in missing_games:
    del games[missing_game]

pressedButtons = []
curr_ip = 0
lcd.clear()
if len(games) is 0:
    lcd.message("NO GAMES FOUND!")
    lcd.backlight(lcd.RED)
    sleep(1)
    iterator  = iter(commands)
    selection = iterator.next()
    mode = "commands"
    lcd.clear()
    lcd.message(selection)
else:
    iterator  = iter(collections.OrderedDict(sorted(games.items(), key=lambda t: t[0])))
    selection = iterator.next()
    mode = "games"
    lcd.message(selection)
lcd.backlight(lcd.YELLOW)
lcdOFF=0
start_time = time()
while True:
    if lcdOFF==0:
       lcd.backlight(lcd.YELLOW)
       #lcd.display()
    waited = time() - start_time
    if ((waited > 15) and (lcdOFF==0)) :
       #print "tries to lcdOff"
       lcd.backlight(lcd.OFF)
       #lcd.noDisplay()
       lcdOFF=1
    # Handle SELECT
    if lcd.buttonPressed(lcd.SELECT):
        start_time = time()
        if lcd.SELECT not in pressedButtons:
            pressedButtons.append(lcd.SELECT)
            if lcdOFF==1:
                lcdOFF=0
                start_time = time()
                lcd.backlight(lcd.YELLOW)
                lcd.display()
                continue

            lcd.backlight(lcd.BLUE)	
            if selection is "Change Target":
                curr_ip += 1
                if curr_ip >= len(ips):
                    curr_ip = 0
                lcd.message("\n"+ips[curr_ip])
            elif selection is "Ping Netdimm":
                lcd.clear()
                lcd.message("Pinging\n"+ips[curr_ip])
                lcd.backlight(lcd.GREEN)
                response = os.system("ping -c 1 "+ips[curr_ip])
                lcd.clear()
                if response == 0:
                    lcd.message("SUCCESS!")
                    lcd.backlight(lcd.YELLOW)
                else:
                    lcd.message("Netdimm is\nunreachable!")
                    lcd.backlight(lcd.RED)
                sleep(2)
                lcd.clear()
                lcd.message(selection)
                lcd.backlight(lcd.YELLOW)
            else:
                lcd.clear()
                lcd.message("Connecting...")
                lcd.backlight(lcd.VIOLET)
                try:
                    triforcetools.connect(ips[curr_ip], 10703)
                except:
                    lcd.clear()
                    lcd.message("Error:\nConnect Failed")
                    lcd.backlight(lcd.RED)
                    sleep(1)
                    lcd.clear()
                    lcd.message(selection)
                    continue

                lcd.clear()
                lcd.backlight(lcd.BLUE)
                lcd.message("Sending...")
                lcd.setCursor(10, 0)
                lcd.ToggleBlink()

                triforcetools.HOST_SetMode(0, 1)
                triforcetools.SECURITY_SetKeycode("\x00" * 8)
                triforcetools.DIMM_UploadFile(rom_dir+games[selection])
                triforcetools.HOST_Restart()
                triforcetools.TIME_SetLimit(10*60*1000)
                triforcetools.disconnect()

                lcd.ToggleBlink()
                lcd.clear()
                lcd.message("Transfer\nComplete!")
                lcd.backlight(lcd.YELLOW)
                sleep(5)
                lcd.clear()
                lcd.message(selection)
    elif lcd.SELECT in pressedButtons:
        pressedButtons.remove(lcd.SELECT)

    # Handle LEFT
    if lcd.buttonPressed(lcd.LEFT):
        start_time = time()
        if lcd.LEFT not in pressedButtons and len(games) > 0:
            pressedButtons.append(lcd.LEFT)
            mode      = "games"
            iterator  = iter(collections.OrderedDict(sorted(games.items(), key=lambda t: t[0])))
            selection = iterator.next()
            previous  = None
            lcd.clear()
            lcd.message("Games")
            lcd.backlight(lcd.YELLOW)
            sleep(1)
            lcd.clear()
            lcd.message(selection)            
    elif lcd.LEFT in pressedButtons:
        pressedButtons.remove(lcd.LEFT)

    # Handle RIGHT
    if lcd.buttonPressed(lcd.RIGHT):
        start_time = time()
        if lcd.RIGHT not in pressedButtons:
            pressedButtons.append(lcd.RIGHT)
            mode      = "commands"
            iterator  = iter(commands)
            selection = iterator.next()
            previous  = None
            lcd.clear()
            lcd.message("Commands")
            lcd.backlight(lcd.YELLOW)
            sleep(1)
            lcd.clear()
            lcd.message(selection)
    elif lcd.RIGHT in pressedButtons:
        pressedButtons.remove(lcd.RIGHT)

    # Handle UP
    if lcd.buttonPressed(lcd.UP):
        start_time = time()
        if lcd.UP not in pressedButtons and previous != None:
            pressedButtons.append(lcd.UP)
            if mode is "games":
                iterator = iter(collections.OrderedDict(sorted(games.items(), key=lambda t: t[0])))
            else:
                iterator = iter(commands)
            needle = iterator.next()
            selection = previous
            previous = needle
            while selection != needle and selection != previous:
                previous = needle
                try:
                    needle = iterator.next()
                except StopIteration:
                    break
            lcd.clear()
            lcd.message(selection)                
    elif lcd.UP in pressedButtons:
        pressedButtons.remove(lcd.UP)

    # Handle DOWN
    if lcd.buttonPressed(lcd.DOWN):
        start_time = time()
        if lcd.DOWN not in pressedButtons:
            pressedButtons.append(lcd.DOWN)            
            previous = selection
            try:
                selection = iterator.next()
            except StopIteration:
                if mode is "games":
                    iterator = iter(collections.OrderedDict(sorted(games.items(), key=lambda t: t[0])))
                else:
                    iterator = iter(commands)
                selection = iterator.next()
            lcd.clear()
            lcd.message(selection)
    elif lcd.DOWN in pressedButtons:
        pressedButtons.remove(lcd.DOWN)
