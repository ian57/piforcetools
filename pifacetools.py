#!/usr/bin/python3
# Written by TravistyOJ (AKA Capaneus)
# Modified for PiFace by Ian57

import os, collections, signal, sys, subprocess, socket
import triforcetools
import pifacecad
from time import sleep

ips = ["192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5"] # Add or remove as many endpoints as you want
rom_dir = "/boot/roms/"  # Set absolute path of rom files ending with trailing /
commands = ["Ping Netdimm", "Change Target"]

PLAY_SYMBOL = pifacecad.LCDBitmap(
    [0x10, 0x18, 0x1c, 0x1e, 0x1c, 0x18, 0x10, 0x0])
PAUSE_SYMBOL = pifacecad.LCDBitmap(
    [0x0, 0x1b, 0x1b, 0x1b, 0x1b, 0x1b, 0x0, 0x0])
INFO_SYMBOL = pifacecad.LCDBitmap(
    [0x6, 0x6, 0x0, 0x1e, 0xe, 0xe, 0xe, 0x1f])
MUSIC_SYMBOL = pifacecad.LCDBitmap(
    [0x2, 0x3, 0x2, 0x2, 0xe, 0x1e, 0xc, 0x0])

PLAY_SYMBOL_INDEX = 0
PAUSE_SYMBOL_INDEX = 1
INFO_SYMBOL_INDEX = 2
MUSIC_SYMBOL_INDEX = 3


# Define a signal handler to turn off LCD before shutting down
def handler(signum = None, frame = None):
    cad = pifacecad.PiFaceCAD()
    cad.lcd.clear()
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
    cad = pifacecad.PiFaceCAD(0,bus=1)
else:
    cad = pifacecad.PiFaceCAD()
cad.lcd.backlight_on()
cad.lcd.cursor_off()
cad.lcd.blink_off() 
cad.lcd.set_cursor(0,0)
cad.lcd.write(" Piface Tools\n   Ver. 1.4")
sleep(2)

# Try to import game list script, if it fails, signal error on LCD
try:
    from gamelist import games
    cad.lcd.clear()
    cad.lcd.set_cursor(0,0)
    cad.lcd.write(" Importing Games List")
    sleep(2)

except (SyntaxError, ImportError) as e:
    #lcd.clear()
    cad.lcd.clear()
    cad.lcd.write("Game List Error!\n  Check Syntax")
    sleep(5)
    games = {}

# Purge game dictionary of game files that can't be found
missing_games = []
for key, value in games.items():
    if not os.path.isfile(rom_dir+value):
        missing_games.append(key)
for missing_game in missing_games:
    del games[missing_game]

pressedButtons = []
curr_ip = 0
cad.lcd.clear()
if len(games) is 0:
    cad.lcd.write("NO GAMES FOUND!")
    sleep(1)
    iterator  = iter(commands)
#    for i in iterator:
#        print(i)
    selection = next(iterator)
    mode = "commands"
    cad.lcd.clear()
    cad.lcd.write(selection)
else:
    iterator  = iter(collections.OrderedDict(sorted(games.items(), key=lambda t: t[0])))
    selection = next(iterator)
    mode = "games"
    cad.lcd.write(selection)

previous  = None

def manage_switch_pressed(event):
    global selection 
    global games 
    global previous
    global iterator
    global mode
    event.chip.lcd.set_cursor(16, 1)
	
    if event.pin_num == 0: #left
        event.chip.lcd.write(str(event.pin_num))
        if event.pin_num not in pressedButtons and len(games) > 0:
            pressedButtons.append(event.pin_num)
            mode      = "games"
            iterator  = iter(collections.OrderedDict(sorted(games.items(), key=lambda t: t[0])))
            selection = next(iterator)
            previous  = None
            cad.lcd.clear()
            cad.lcd.write("Games")
            sleep(1)
            cad.lcd.clear()
            cad.lcd.write(selection)            
        elif event.pin_num in pressedButtons:
            pressedButtons.remove(event.pin_num)


    elif event.pin_num == 1: #right
        event.chip.lcd.write(str(event.pin_num))
        if event.pin_num not in pressedButtons:
            pressedButtons.append(event.pin_num)
            mode      = "commands"
            iterator  = iter(commands)
            selection = next(iterator)
            previous  = None
            cad.lcd.clear()
            cad.lcd.write("Commands")
            sleep(1)
            cad.lcd.clear()
            cad.lcd.write(selection)
        elif event.pin_num in pressedButtons:
            pressedButtons.remove(event.pin_num)


    elif event.pin_num == 2: #up
        event.chip.lcd.write(str(event.pin_num))
        if event.pin_num not in pressedButtons and previous != None:
            pressedButtons.append(event.pin_num)
            if mode is "games":
                iterator = iter(collections.OrderedDict(sorted(games.items(), key=lambda t: t[0])))
            else:
                iterator = iter(commands)
            needle = next(iterator)
            selection = previous
            previous = needle
            while selection != needle and selection != previous:
                previous = needle
                try:
                    needle = next(iterator)
                except StopIteration:
                    break
            cad.lcd.clear()
            cad.lcd.write(selection)                
        elif event.pin_num in pressedButtons:
            pressedButtons.remove(event.pin_num)

    elif event.pin_num == 3: #down
        event.chip.lcd.write(str(event.pin_num))
        if event.pin_num not in pressedButtons:
            pressedButtons.append(event.pin_num)            
            previous = selection
            try:
                selection = next(iterator)
            except StopIteration:
                if mode is "games":
                    iterator = iter(collections.OrderedDict(sorted(games.items(), key=lambda t: t[0])))
                else:
                    iterator = iter(commands)
                selection = next(iterator)
            cad.lcd.clear()
            cad.lcd.write(selection)
        elif event.pin_num in pressedButtons:
            pressedButtons.remove(event.pin_num)

    elif event.pin_num == 4: #select
        event.chip.lcd.write(str(event.pin_num))
        if event.pin_num not in pressedButtons:
            pressedButtons.append(event.pin_num)
            if selection is "Change Target":
                curr_ip += 1
                if curr_ip >= len(ips):
                    curr_ip = 0
                cad.lcd.write("\n"+ips[curr_ip])
            elif selection is "Ping Netdimm":
                cad.lcd.clear()
                cad.lcd.write("Pinging\n"+ips[curr_ip])
                response = os.system("ping -c 1 "+ips[curr_ip])
                cad.lcd.clear()
                if response == 0:
                    cad.lcd.write("SUCCESS!")
                else:
                    cad.lcd.write("Netdimm is\nunreachable!")
                sleep(2)
                cad.lcd.clear()
                cad.lcd.write(selection)
            else:
                cad.lcd.clear()
                cad.lcd.write("Connecting...")
                try:
                    triforcetools.connect(ips[curr_ip], 10703)
                except:
                    cad.lcd.clear()
                    cad.lcd.write("Error:\nConnect Failed")
                    sleep(1)
                    cad.lcd.clear()
                    cad.lcd.write(selection)
                    continue
                cad.lcd.clear()
                cad.lcd.write("Sending...")
                cad.lcd.set_cursor(10, 0)
                cad.lcd.blink_on();
                triforcetools.HOST_SetMode(0, 1)
                triforcetools.SECURITY_SetKeycode("\x00" * 8)
                triforcetools.DIMM_UploadFile(rom_dir+games[selection])
                triforcetools.HOST_Restart()
                triforcetools.TIME_SetLimit(10*60*1000)
                triforcetools.disconnect()
                cad.lcd.blink_off()
                cad.lcd.clear()
                cad.lcd.write("Transfer\nComplete!")
                sleep(5)
                cad.lcd.clear()
                cad.lcd.write(selection)
    elif event.pin_num in pressedButtons:
        pressedButtons.remove(event.pin_num)

    elif event.pin_num == 5:
        event.chip.lcd.write(str(event.pin_num))
    elif event.pin_num == 6:
        event.chip.lcd.write(str(event.pin_num))
    elif event.pin_num == 7:
        event.chip.lcd.write(str(event.pin_num))
    elif event.pin_num == 8:
        event.chip.lcd.write(str(event.pin_num))


# wait for button presses
switchlistener = pifacecad.SwitchEventListener(chip=cad)
for i in range(8):
        switchlistener.register(i, pifacecad.IODIR_FALLING_EDGE, manage_switch_pressed)
switchlistener.activate()

'''
while True:

    # Handle SELECT
    if lcd.buttonPressed(lcd.SELECT):
        if lcd.SELECT not in pressedButtons:
            pressedButtons.append(lcd.SELECT)
            if selection is "Change Target":
                curr_ip += 1
                if curr_ip >= len(ips):
                    curr_ip = 0
                lcd.message("\n"+ips[curr_ip])
            elif selection is "Ping Netdimm":
                lcd.clear()
                lcd.message("Pinging\n"+ips[curr_ip])
                response = os.system("ping -c 1 "+ips[curr_ip])
                lcd.clear()
                if response == 0:
                    lcd.message("SUCCESS!")
                else:
                    lcd.message("Netdimm is\nunreachable!")
                sleep(2)
                lcd.clear()
                lcd.message(selection)
            else:
                lcd.clear()
                lcd.message("Connecting...")

                try:
                    triforcetools.connect(ips[curr_ip], 10703)
                except:
                    lcd.clear()
                    lcd.message("Error:\nConnect Failed")
                    sleep(1)
                    lcd.clear()
                    lcd.message(selection)
                    continue

                lcd.clear()
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
                sleep(5)
                lcd.clear()
                lcd.message(selection)
    elif lcd.SELECT in pressedButtons:
        pressedButtons.remove(lcd.SELECT)

    # Handle LEFT
    if lcd.buttonPressed(lcd.LEFT):
        if lcd.LEFT not in pressedButtons and len(games) > 0:
            pressedButtons.append(lcd.LEFT)
            mode      = "games"
            iterator  = iter(collections.OrderedDict(sorted(games.items(), key=lambda t: t[0])))
            selection = iterator.next()
            previous  = None
            lcd.clear()
            lcd.message("Games")
            sleep(1)
            lcd.clear()
            lcd.message(selection)            
    elif lcd.LEFT in pressedButtons:
        pressedButtons.remove(lcd.LEFT)

    # Handle RIGHT
    if lcd.buttonPressed(lcd.RIGHT):
        if lcd.RIGHT not in pressedButtons:
            pressedButtons.append(lcd.RIGHT)
            mode      = "commands"
            iterator  = iter(commands)
            selection = iterator.next()
            previous  = None
            lcd.clear()
            lcd.message("Commands")
            sleep(1)
            lcd.clear()
            lcd.message(selection)
    elif lcd.RIGHT in pressedButtons:
        pressedButtons.remove(lcd.RIGHT)

    # Handle UP
    if lcd.buttonPressed(lcd.UP):
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
'''
