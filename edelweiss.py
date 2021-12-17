# coding=utf-8
# Author Emil Lantz
# Based on original C script by Erik Månsson & Hannes Björk

# Main läge, kör clock()

# Om pin 27 jordas, Starta stopwatch(), vänta 3 sekunder sen kolla condition

# Jordas pin GPIO-27, return till clock()

from gpiozero import LED, Button
from datetime import datetime
import time
import spidev

#TODO Dokumentera koden bättre

# All numbers are GPIO-pin numbers, not pinout.
load = LED(20)
reset = LED(21)
timerButton = Button(4)
#Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000

'''
BCD-coding for 7-bit-displays.

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

# Takes single digits from array in main loop and returns the BCD-code for each digit 
# to be passed into the SPI
def clockToCode(n):
    returnValues = []
    for nbr in n:
        if(nbr < 10):
           returnValues.append(digits[nbr])
    return returnValues

# Default values for load & reset
load.off()
reset.on()

# Returns current time as int[] HH, MM, SS
def clock():
    currentTime = datetime.now()
    hours = int(currentTime.strftime("%H"))
    minutes = int(currentTime.strftime("%M"))
    seconds = int(currentTime.strftime("%S"))
    return(hours, minutes, seconds)

def stopwatch():
    zero = time.time()
    while True:
        mins = int((time.time() - zero) // 60)
        sec = int((time.time() - zero) // 1 % 60)
        ms = int(round((time.time() - zero) % 1, 2) * 100)
        time.sleep(0.001)
        clockValues = [mins // 10, mins % 10, sec // 10, sec % 10, ms // 10, ms % 10]
        displayCode = clockToCode(clockValues)
        digitToDisplays(displayCode)
        #Minimum time set to 2 seconds to avoid exiting the function due to holding the button.
        if(time.time() - zero > 2 and timerButton.is_pressed):
            displayTime(displayCode)
            return

#Ge lite timerfeeling när funktionen är slut
def displayTime(currentTimeCode):
    a = 0b0000000
    empty = [a]*6
    for i in range(4):
        digitToDisplays(currentTimeCode)
        time.sleep(1.1)
        digitToDisplays(empty)
        time.sleep(0.4)

def digitToDisplays(a):
    spi.writebytes(a)
    load.on()
    time.sleep(0.001)
    load.off()
    time.sleep(0.001)

# Main loop. All extension-functions should return here. 
while True:
    time.sleep(0.001) #0.01
    hms = clock()
    clockValues = [hms[0] // 10, hms[0] % 10, hms[1] // 10, hms[1] % 10, hms[2] // 10, hms[2] % 10]
    displayCode = clockToCode(clockValues)
    for n in range(6):
        if(n % 4 == 1 and hms[2] % 2 == 0):
            displayCode[n] = displayCode[n] | semicolon
    digitToDisplays(displayCode)

    if timerButton.is_pressed:
        stopwatch()