# Author Emil Lantz

# Main läge, kör clock()

# Om pin 27 jordas, Starta stopwatch(), vänta 3 sekunder sen kolla condition

# Jordas pin GPIO-27, return till clock()

from gpiozero import *
from gpiozero.pins.mock import MockFactory
from datetime import datetime
import time
import spidev

#TODO Skriv om alla print till 7SD's

#Device.pin_factory = MockFactory()
# All numbers are GPIO-pin numbers, not 
load = LED(20)
reset = LED(21)
yellow_button = Button(27)
#Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000

'''
NBCD-coding for 7-bit-displays.

00000001: Middle
00000010: Left top
00000100: Left bottom
00001000: Bottom
00010000: Right bottom
00100000: Right top
01000000: Top

10000000: Semicolon (Denna är troligtvis direktkopplad till dot-leddarna)

These values combine as a single 8 bit binary value to represent 
numbers on the 7-segment-displays. e.g. the value of 0 is 01111110,
meaning all segments except the middle and points are lit.
'''
digits = [
    0b01111110, #0
    0b00110000, #1
    0b01101101, #2
    0b01111001, #3
    0b00110011, #4
    0b01011011, #5
    0b01011111, #6
    0b01110000, #7
    0b01111111, #8
    0b01111011, #9
]

semicolon = 0b10000000 #Semicolons

# Default values for load & reset
load = 0
reset = 1
print(yellow_button.value)

# Returns current time as int HH, MM, SS
def clock():
    currentTime = datetime.now()
    hours = int(currentTime.strftime("%H"))
    minutes = int(currentTime.strftime("%M"))
    seconds = int(currentTime.strftime("%S"))
    return(hours, minutes, seconds)

# TODO skriv om så att detta returnerar intrepresentation på formen MM:SS:MS
def stopwatch():
    zero = time.time()
    while True:
        #Minimum time set to 2 seconds to avoid exiting the function due to holding the button.
        print(round(time.time() - zero, 2))

        # Sleep for 0.005s as that is half the minimum interval stopwatch will show. 
        # More accuracy is redundant and will only slow the raspberry down.
        time.sleep(0.005)
        if(time.time() - zero > 2 and yellow_button.value == 0):
            return

def digitToDisplays(a):
    for i in range(6):
        spi.xfer2(a)
    pass

i = 0
while True:
    time.sleep(2) #0.01
    hms = clock()
    clockValues = [hms[0] // 10, hms[0] % 10, hms[1] // 10, hms[1] % 10, hms[2] // 10, hms[2] % 10]
    
    dig = 0
    for n in clockValues:
        if(dig % 4 == 1):
            digits[n] = digits[n] | semicolon
        digitToDisplays(digits[n])
        dig += 1

        print(digits[n])
    if yellow_button.value == 1:
        stopwatch()