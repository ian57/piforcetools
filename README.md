PiforceTools
============

Piforce Tools drives a Raspberry Pi with Adafruit LCD Plate and interfaces with debugmode's triforce tools to load a NetDIMM board with binaries for a Triforce, Naomi, or Chihiro arcade system.  
it is working with the adafruit LCD module 16x2 LCD Plate - http://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi, and chinese clone from DX http://www.dx.com/fr/p/rgb-negative-16-x-2-lcd-keypad-kit-for-raspberry-pi-black-297384#.Vw-fkHWLTRZ but you need to modify the file Adafruit_CharLCDPlate.py, at line 99 like this 
Code:

~~~~~~
0b00011111, # IODIRA R+G LEDs=outputs, buttons=inputs
~~~~~~

I'm modifying it to work with de piface module from http://www.kubii.fr/site-entier/229-piface-control-display-afficheur-lcd-3272496000179.html which uses SPI bus, IR remote control ans more buttons.
It uses also the pifacecad library.  The program is name pifacetools.py

## Banggood clone
For this LCDPlate clone 16x2_LCD_with_Keypad_and_Backlit_SKU:297384  you need to use the patched version od the Adafruit code : http://www.raspberrypiwiki.com/index.php/16x2_LCD_with_Keypad_and_Backlit_SKU:297384 and the archive http://www.raspberrypiwiki.com/index.php/File:16x2LCD-Adafruit-Raspberry-Pi-Python-Code.zip

When plugging the LCD plate on the Raspberry Pi you need to take care that the board does not touch or lay on the metallic cage of the usb connector or RJ 45 connector. If there is a contact, the i2c mcp module is not recognised anymore by the system and the module fails to work. I think a ground appears from the plate board to the pi board preventing the i2c to work.

## Usage

Left/Right buttons determine Game mode or Command mode respectively.  Up/Down navigate items within a mode.  Select button will select the item being displayed.  In Command mode, the following commands can be used:

1. Change Target - By default, you can send binaries to up to 4 nodes, configured at 192.168.1.2, 192.168.1.3, 192.168.1.4, 192.168.1.5.  Each time you select Change Target, the target will be changed.
2. Ping Netdimm - To test if the Netdimm is reachable via a ping.  

## Getting Started

You will need the following items to use Piforce Tools:

1. A Raspberry Pi - http://www.raspberrypi.org/ 
2. An SD Card (Minimum 4GB, but I recommend at 8GB or higher)
3. An assembled Adafruit 16x2 LCD Plate - http://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi
4. A Naomi, Triforce, or Chihiro arcade system.
5. A Netdimm with a zero-key security PIC installed.  I cannot provide links for this, but a modicum of Google-fu will get you what you need.  The netdimm will need to be configured in static mode with an IP address of 192.168.1.2, netmask of 255.255.255.0, and gateway of 192.168.1.1.
6. A crossover cable

## Installation

Now you are finally ready to install Piforce Tools.

1. Downlad the piforce tools SD card image: http://downloads.travistyoj.com/piforcetools.img.zip
2. Extract .img file, and use imager tool to write it to your SD card.  If you are using Windows, look for Win32DiskImager.  If you are using Linux or Mac OS, you will use the command line tool dd.  Imaging an SD card is easy, but here is some more information - http://elinux.org/ArchLinux_Install_Guide
3. Use a partition manager tool like Partition Wizard to move the Ext4 partition to the end of the card, and resize the FAT partition to use all unallocated space: http://www.partitionwizard.com/free-partition-manager.html
4. Load up ROMs in the "roms" directory.

## Troubleshooting
I provide this script and image without warranty, and its not feasible to provide support to everyone, but I want to at least provide some troubleshooting steps 

* **LCD powers on, but no text is displayed.** Make sure you adjust the contrast of the LCD Plate.  
* **LCD does not power on** This could be several different things.  First make sure the LCD Plate is assembled correctly by following the usage instructions on Adafruit's product page.  Run the python script provided there and confirm the LCD Plate works.  Double check your solder work.  Depending on your revision of your Raspberry Pi, you may need to change any lines of the Piforce Tools script to specify the bus number when instantiating the LCD Plate object.  For example, change lcd = Adafruit_CharLCDPlate() to lcd = Adafruit_CharLCDPlate(busnum = 0) for a Rev 1 Pi.
* **NO GAMES FOUND! message is displayed** Make sure your roms are in the /home/pi/roms directory and that the filenames match those specified in the piforcetools.py script. 
* **I keep getting Connect Failed! when I try to send a game** Make sure your target device has been configured to be at 192.168.1.2.

## Credit

This could not be done without debugmode's triforce tools script.  All the heavy lifting was done by him, I just made an easy to use interface for his work.  Also shoutout to darksoft for his killer Atomiswave conversions.
