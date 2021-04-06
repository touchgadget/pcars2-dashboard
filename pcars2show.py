#!/usr/bin/env python3
"""
Show Project Cars 2 (PCars2)racing simulation game telemetry on 8x8
RGB LED display.

Runs on a Raspberry Pi with the Pimoroni Unicorn hat (8x8 RGB LED). No
soldering. Just plug the Unicorn hat into the Raspberry Pi board. I am
using a Raspberry Pi 2 but any Pi from 2-4 should work. It should also
work on a Pi Zero W. The code has been tested on PCars2 running on a
Playstation 4 but should work with Xbox One and PC since they all support
the UDP telemetry API.

The PCars2 API is documented here.
    https://www.projectcarsgame.com/two/project-cars-2-api/

This program is based on the Patch 5 version. Be sure to look at the
Shared Memory version even though it only works on the Windows version
of the game. The Shared Memory header file has many more comments than
the UDP version.

The Unicorn LED hat is here.
    https://shop.pimoroni.com/products/unicorn-hat

Pimoroni gear is sold in the US by Adafruit and probably others.

The Unicorn hat Python library is here.
    https://github.com/pimoroni/unicorn-hat


MIT License

Copyright (c) 2021 touchgadgetdev@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


import socket
from struct import unpack
from enum import IntEnum
import unicornhat as Led_matrix

PCARS2_UDP_PORT = 5606

# enum EUDPStreamerPacketHandlerType
# {
#   eCarPhysics = 0,
#   eRaceDefinition = 1,
#   eParticipants = 2,
#   eTimings = 3,
#   eGameState = 4,
#   eWeatherState = 5, // not sent at the moment, information can be found in the game state packet
#   eVehicleNames = 6, // not sent at the moment
#   eTimeStats = 7,
#   eParticipantVehicleNames = 8
# };

class ePacketType(IntEnum):
    """ Enum for packet type. """
    eCarPhysics = 0
    eRaceDefinition = 1
    eParticipants = 2
    eTimings = 3
    eGameState = 4
    eWeatherState = 5 # not sent at the moment, information can be found in the game state packet
    eVehicleNames = 6 # not sent at the moment
    eTimeStats = 7
    eParticipantVehicleNames = 8

# struct PacketBase
# {
#   unsigned int    mPacketNumber;          //0 counter reflecting all the packets that have been sent during the game run
#   unsigned int    mCategoryPacketNumber;  //4 counter of the packet groups belonging to the given category
#   unsigned char   mPartialPacketIndex;    //8 If the data from this class had to be sent in several packets, the index number
#   unsigned char   mPartialPacketNumber;   //9 If the data from this class had to be sent in several packets, the total number
#   unsigned char   mPacketType;            //10 what is the type of this packet (see EUDPStreamerPacketHanlderType for details)
#   unsigned char   mPacketVersion;         //11 what is the version of protocol for this handler, to be bumped with data structure change
# };

class eCarPhysicsFields(IntEnum):
    """ Enum for fields in the car physics packets. """
    mPacketNumber = 0
    mCategoryPacketNumber = 1
    mPartialPacketIndex = 2
    mPartialPacketNumber = 3
    mPacketType = 4
    mPacketVersion = 5
    sViewedParticipantIndex = 6
    sUnfilteredThrottle = 7
    sUnfilteredBrake = 8
    sUnfilteredSteering = 9
    sUnfilteredClutch = 10
    sCarFlags = 11
    sOilTempCelsius = 12
    sOilPressureKPa = 13
    sWaterTempCelsius = 14
    sWaterPressureKpa = 15
    sFuelPressureKpa = 16
    sFuelCapacity = 17
    sBrake = 18
    sThrottle = 19
    sClutch = 20
    sFuelLevel = 21
    sSpeed = 22
    sRpm = 23
    sMaxRpm = 24
    sSteering = 25
    sGearNumGears = 26
    sBoostAmount = 27
    sCrashState = 28
    sOdometerKM = 29
    sOrientation1 = 30
    sOrientation2 = 31
    sOrientation3 = 32
    sLocalVelocity1 = 33
    sLocalVelocity2 = 34
    sLocalVelocity3 = 35
    sWorldVelocity1 = 36
    sWorldVelocity2 = 37
    sWorldVelocity3 = 38
    sAngularVelocity1 = 39
    sAngularVelocity2 = 40
    sAngularVelocity3 = 41
    sLocalAcceleration1 = 42
    sLocalAcceleration2 = 43
    sLocalAcceleration3 = 44
    sWorldAcceleration1 = 45
    sWorldAcceleration2 = 46
    sWorldAcceleration3 = 47
    sExtentsCentre1 = 48
    sExtentsCentre2 = 49
    sExtentsCentre3 = 50
    sTyreFlags1 = 51
    sTyreFlags2 = 52
    sTyreFlags3 = 53
    sTyreFlags4 = 54
    sTerrain1 = 55
    sTerrain2 = 56
    sTerrain3 = 57
    sTerrain4 = 58
    sTyreY1 = 59
    sTyreY2 = 60
    sTyreY3 = 61
    sTyreY4 = 62
    sTyreRPS1 = 63
    sTyreRPS2 = 64
    sTyreRPS3 = 65
    sTyreRPS4 = 66
    sTyreTemp1 = 67
    sTyreTemp2 = 68
    sTyreTemp3 = 69
    sTyreTemp4 = 70
    sTyreHeightAboveGround1 = 71
    sTyreHeightAboveGround2 = 72
    sTyreHeightAboveGround3 = 73
    sTyreHeightAboveGround4 = 74
    sTyreWear1 = 75
    sTyreWear2 = 76
    sTyreWear3 = 77
    sTyreWear4 = 78
    sBrakeDamage1 = 79
    sBrakeDamage2 = 80
    sBrakeDamage3 = 81
    sBrakeDamage4 = 82
    sSuspensionDamage1 = 83
    sSuspensionDamage2 = 84
    sSuspensionDamage3 = 85
    sSuspensionDamage4 = 86
    sBrakeTempCelsius1 = 87
    sBrakeTempCelsius2 = 88
    sBrakeTempCelsius3 = 89
    sBrakeTempCelsius4 = 90
    sTyreTreadTemp1 = 91
    sTyreTreadTemp2 = 92
    sTyreTreadTemp3 = 93
    sTyreTreadTemp4 = 94
    sTyreLayerTemp1 = 95
    sTyreLayerTemp2 = 96
    sTyreLayerTemp3 = 97
    sTyreLayerTemp4 = 98
    sTyreCarcassTemp1 = 99
    sTyreCarcassTemp2 = 100
    sTyreCarcassTemp3 = 101
    sTyreCarcassTemp4 = 102
    sTyreRimTemp1 = 103
    sTyreRimTemp2 = 104
    sTyreRimTemp3 = 105
    sTyreRimTemp4 = 106
    sTyreInternalAirTemp1 = 107
    sTyreInternalAirTemp2 = 108
    sTyreInternalAirTemp3 = 109
    sTyreInternalAirTemp4 = 110
    sTyreTempLeft1 = 111
    sTyreTempLeft2 = 112
    sTyreTempLeft3 = 113
    sTyreTempLeft4 = 114
    sTyreTempCenter1 = 115
    sTyreTempCenter2 = 116
    sTyreTempCenter3 = 117
    sTyreTempCenter4 = 118
    sTyreTempRight1 = 119
    sTyreTempRight2 = 120
    sTyreTempRight3 = 121
    sTyreTempRight4 = 122
    sWheelLocalPositionY1 = 123
    sWheelLocalPositionY2 = 124
    sWheelLocalPositionY3 = 125
    sWheelLocalPositionY4 = 126
    sRideHeight1 = 127
    sRideHeight2 = 128
    sRideHeight3 = 129
    sRideHeight4 = 130
    sSuspensionTravel1 = 131
    sSuspensionTravel2 = 132
    sSuspensionTravel3 = 133
    sSuspensionTravel4 = 134
    sSuspensionVelocity1 = 135
    sSuspensionVelocity2 = 136
    sSuspensionVelocity3 = 137
    sSuspensionVelocity4 = 138
    sSuspensionRideHeight1 = 139
    sSuspensionRideHeight2 = 140
    sSuspensionRideHeight3 = 141
    sSuspensionRideHeight4 = 142
    sAirPressure1 = 143
    sAirPressure2 = 144
    sAirPressure3 = 145
    sAirPressure4 = 146
    sEngineSpeed = 147
    sEngineTorque = 148
    sWings1 = 149
    sWings2 = 150
    sHandBrake = 151
    sAeroDamage = 152
    sEngineDamage = 153
    sJoyPad0 = 154
    sDPad = 155
    sTyreCompound1 = 156
    sTyreCompound2 = 157
    sTyreCompound3 = 158
    sTyreCompound4 = 159
    sTurboBoostPressure = 160
    sFullPosition1 = 161
    sFullPosition2 = 162
    sFullPosition3 = 163
    sBrakeBias = 164
    sTickCount = 165

# Bitmaps for the gear such as N for neutral, R for reverse, etc.
GEAR_BITS = [
    [   # N = Neutral
        0b00000000,
        0b00000000,
        0b00100001,
        0b00110001,
        0b00101001,
        0b00100101,
        0b00100011,
        0b00100001,
    ],
    [   # 1 = First gear
        0b00000000,
        0b00000000,
        0b00000010,
        0b00000110,
        0b00000010,
        0b00000010,
        0b00000010,
        0b00001111,
    ],
    [   # 2
        0b00000000,
        0b00000000,
        0b00000110,
        0b00001001,
        0b00000001,
        0b00000010,
        0b00000100,
        0b00001111,
    ],
    [   # 3
        0b00000000,
        0b00000000,
        0b00000110,
        0b00001001,
        0b00000010,
        0b00000001,
        0b00001001,
        0b00000110,
    ],
    [   # 4
        0b00000000,
        0b00000000,
        0b00000110,
        0b00001010,
        0b00001111,
        0b00000010,
        0b00000010,
        0b00001111,
    ],
    [   # 5
        0b00000000,
        0b00000000,
        0b00001111,
        0b00001000,
        0b00001110,
        0b00000001,
        0b00001001,
        0b00000110,
    ],
    [   # 6
        0b00000000,
        0b00000000,
        0b00000110,
        0b00001001,
        0b00001110,
        0b00001001,
        0b00001001,
        0b00000110,
    ],
    [   # 7
        0b00000000,
        0b00000000,
        0b00001111,
        0b00000010,
        0b00000100,
        0b00000100,
        0b00001000,
        0b00001000,
    ],
    [   # 8
        0b00000000,
        0b00000000,
        0b00000110,
        0b00001001,
        0b00000110,
        0b00001001,
        0b00001001,
        0b00000110,
    ],
    [   # 9
        0b00000000,
        0b00000000,
        0b00000110,
        0b00001001,
        0b00000111,
        0b00000010,
        0b00000100,
        0b00001000,
    ],
    [   # 10
        0b00000000,
        0b00000000,
        0b00100110,
        0b00101001,
        0b00101001,
        0b00101001,
        0b00101001,
        0b00100110,
    ],
    [   # 11
        0b00000000,
        0b00000000,
        0b00010010,
        0b00110110,
        0b00010010,
        0b00010010,
        0b00010010,
        0b00111111,
    ],
    [   # 12
        0b00000000,
        0b00000000,
        0b00100110,
        0b00101001,
        0b00100001,
        0b00100010,
        0b00100100,
        0b00101111,
    ],
    [   # 13
        0b00000000,
        0b00000000,
        0b00100110,
        0b00101001,
        0b00100010,
        0b00100001,
        0b00101001,
        0b00100110,
    ],
    [   # 14
        0b00000000,
        0b00000000,
        0b00100110,
        0b00101010,
        0b00101111,
        0b00100010,
        0b00100010,
        0b00101111,
    ],
    [   # 15 = Reverse
        0b00000000,
        0b00000000,
        0b00111100,
        0b00100010,
        0b00111100,
        0b00101000,
        0b00100100,
        0b00100010,
    ],
]

GEAR_NAMES = ['N', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', 'R']

WIDTH, HEIGHT = Led_matrix.get_shape()

def draw_gear(gear_index):
    """ Draw the gear on the 8x8 display. """
    bitmap = GEAR_BITS[gear_index]
    for h in range(HEIGHT):
        for w in range(WIDTH):
            if bitmap[h] & (1<<(7-w)):
                Led_matrix.set_pixel(w, h, 255, 0, 255)
            else:
                Led_matrix.set_pixel(w, h, 0, 0, 0)

# The rev (RPM %) indicator starts at the bottom left corner (row=7,col=0)and
# ends at the top right corner (row=0,col=7). The color shifts from green
# to red to blue.
RPM_LEDS = [
    {"row": 7, "col": 0, "red":0, "green":255, "blue": 0},
    {"row": 6, "col": 0, "red":0, "green":255, "blue": 0},
    {"row": 5, "col": 0, "red":0, "green":255, "blue": 0},
    {"row": 4, "col": 0, "red":0, "green":255, "blue": 0},
    {"row": 3, "col": 0, "red":0, "green":255, "blue": 0},
    {"row": 2, "col": 0, "red":255, "green":0, "blue": 0},
    {"row": 1, "col": 0, "red":255, "green":0, "blue": 0},
    {"row": 1, "col": 1, "red":255, "green":0, "blue": 0},
    {"row": 0, "col": 1, "red":255, "green":0, "blue": 0},
    {"row": 0, "col": 2, "red":255, "green":0, "blue": 0},
    {"row": 0, "col": 3, "red":0, "green":0, "blue": 255},
    {"row": 0, "col": 4, "red":0, "green":0, "blue": 255},
    {"row": 0, "col": 5, "red":0, "green":0, "blue": 255},
    {"row": 0, "col": 6, "red":0, "green":0, "blue": 255},
    {"row": 0, "col": 7, "red":0, "green":0, "blue": 255},
]

def draw_rev(rpm, maxrpm):
    """ Draw the rev (RPM %) indicator on the left most column and top most row. """
    rpm_indicator_stop = round((rpm / maxrpm) * len(RPM_LEDS))
    for l in range(len(RPM_LEDS)):
        led = RPM_LEDS[l]
        if l < rpm_indicator_stop:
            Led_matrix.set_pixel(led["col"], led["row"], led["red"], led["green"], led["blue"])
        else:
            Led_matrix.set_pixel(led["col"], led["row"], 0, 0, 0)

def main():
    """
    Listen on the PCars2 UDP port for telemetry packets and
    update the 8x8 LED matrix.
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port. Listen on all interfaces.
    server_address = ('0.0.0.0', PCARS2_UDP_PORT)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

    Led_matrix.set_layout(Led_matrix.AUTO)
    Led_matrix.rotation(0)
    Led_matrix.brightness(0.75)

    while True:
        print('\nwaiting to receive message')
        data, address = sock.recvfrom(4096)

        print('received {} bytes from {}'.format(
            len(data), address))

        if len(data) >= 12:
            mPacketNumber, mCategoryPacketNumber, mPartialPacketIndex, \
                    mPartialPacketNumber, mPacketType, mPacketVersion = \
                    unpack('<IIBBBB', data[:12])
            print('mPacketType', mPacketType)
            if mPacketType == ePacketType.eCarPhysics:
                fields = unpack('<IIBBBBbBBbBBhHhHHBBBBffHHbBBBf3f3f3f3f3f3f3f4B4B4f4f4B4f4B4B4B4h4H4H4H4H4H4H4H4H4f4f4f4f4H4Hff2BBBBIB40c40c40c40cf3fBI', data)

                current_gear = fields[eCarPhysicsFields.sGearNumGears] & 0x0F
                print('sGear', current_gear, GEAR_NAMES[current_gear])
                draw_gear(current_gear)

                sRpm = fields[eCarPhysicsFields.sRpm]
                print('sRpm', sRpm)
                sMaxRpm = fields[eCarPhysicsFields.sMaxRpm]
                print('sMaxRpm', sMaxRpm)
                draw_rev(sRpm, sMaxRpm)
                Led_matrix.show()

#               print('sFuelCapacity(liters)', fields[eCarPhysicsFields.sFuelCapacity])
#               print('sFuelLevel', fields[eCarPhysicsFields.sFuelLevel])
#               print('Fuel(liters)', fields[eCarPhysicsFields.sFuelCapacity]\
#                       * fields[eCarPhysicsFields.sFuelLevel])
#               print('Fuel(gallons)', fields[eCarPhysicsFields.sFuelCapacity]\
#                       * fields[eCarPhysicsFields.sFuelLevel] * 0.2641729)

#               speed = fields[eCarPhysicsFields.sSpeed]
#               speed_kph = speed * 3.6
#               speed_mph = speed_kph * 0.62137
#               print('sSpeed(meters/sec)', speed, 'KPH', speed_kph, 'MPH', speed_mph)

if __name__ == '__main__':
    main()
