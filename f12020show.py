#!/usr/bin/env python3
"""
Show F1 2020 racing simulation game telemetry on 8x8 RGB LED display.

Runs on a Raspberry Pi with the Pimoroni Unicorn hat (8x8 RGB LED). No
soldering. Just plug the Unicorn hat into the Raspberry Pi board. I am
using a Raspberry Pi 2 but any Pi from 2-4 should work. It should also
work on a Pi Zero W. The code has been tested on F1 2020 running on a
Playstation 4 but should work with Xbox One and PC since they all support
the UDP telemetry API.

The unofficial F1 2020 API is documented here.
    https://f1-2020-telemetry.readthedocs.io/en/latest/telemetry-specification.html#telemetry-specification

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
from struct import unpack_from, calcsize
from enum import IntEnum
import unicornhat as Led_matrix

F1_UDP_PORT = 20777

class ePacketType(IntEnum):
    """ Enum for packet type. """
#Contains all motion data for player's car - only sent while player is in control
    eMotion = 0,
#Data about the session - track, time left
    eSession = 1,
#Data about all the lap times of cars in the session
    eLapData = 2,
#Various notable events that happen during a session
    eEvent = 3,
#List of participants in the session, mostly relevant for multiplayer
    eParticipants = 4,
#Packet detailing car setups for cars in the race
    eCarSetups = 5,
#Telemetry data for all cars
    eCarTelemetry = 6,
#Status data for all cars such as damage
    eCarStatus = 7,
#Final classification confirmation at the end of a race
    eFinalClassification = 8,
#Information about players in a multiplayer lobby
    eLobbyInformation = 9

# struct PacketHeader
# {
#     uint16_t  m_packetFormat;            // 2020
#     uint8_t   m_gameMajorVersion;        // Game major version - "X.00"
#     uint8_t   m_gameMinorVersion;        // Game minor version - "1.XX"
#     uint8_t   m_packetVersion;           // Version of this packet type, all start from 1
#     uint8_t   m_packetId;                // Identifier for the packet type, see below
#     uint64_t  m_sessionUID;              // Unique identifier for the session
#     float     m_sessionTime;             // Session timestamp
#     uint32_t  m_frameIdentifier;         // Identifier for the frame the data was retrieved on
#     uint8_t   m_playerCarIndex;          // Index of player's car in the array
#     uint8_t   m_secondaryPlayerCarIndex; // Index of secondary player's car in the array (splitscreen)
#                                          // 255 if no second player
# };


# struct CarTelemetryData
# {
#     uint16_t  m_speed;                      // Speed of car in kilometres per hour
#     float     m_throttle;                   // Amount of throttle applied (0.0 to 1.0)
#     float     m_steer;                      // Steering (-1.0 (full lock left) to 1.0 (full lock right))
#     float     m_brake;                      // Amount of brake applied (0.0 to 1.0)
#     uint8_t   m_clutch;                     // Amount of clutch applied (0 to 100)
#     int8_t    m_gear;                       // Gear selected (1-8, N=0, R=-1)
#     uint16_t  m_engineRPM;                  // Engine RPM
#     uint8_t   m_drs;                        // 0 = off, 1 = on
#     uint8_t   m_revLightsPercent;           // Rev lights indicator (percentage)
#     uint16_t  m_brakesTemperature[4];       // Brakes temperature (celsius)
#     uint8_t   m_tyresSurfaceTemperature[4]; // Tyres surface temperature (celsius)
#     uint8_t   m_tyresInnerTemperature[4];   // Tyres inner temperature (celsius)
#     uint16_t  m_engineTemperature;          // Engine temperature (celsius)
#     float     m_tyresPressure[4];           // Tyres pressure (PSI)
#     uint8_t   m_surfaceType[4];             // Driving surface, see appendices
# };
#
# struct PacketCarTelemetryData
# {
#     PacketHeader     m_header;             // Header
#
#     CarTelemetryData m_carTelemetryData[22];
#
#     uint32_t         m_buttonStatus;        // Bit flags specifying which buttons are being pressed
#                                             // currently - see appendices
#     uint8_t          m_mfdPanelIndex;       // Index of MFD panel open - 255 = MFD closed
#                                             // Single player, race – 0 = Car setup, 1 = Pits
#                                             // 2 = Damage, 3 =  Engine, 4 = Temperatures
#                                             // May vary depending on game mode
#     uint8_t          m_mfdPanelIndexSecondaryPlayer;   // See above
#     int8_t           m_suggestedGear;       // Suggested gear for the player (1-8)
#                                             // 0 if no gear suggested
# };

class eCarTelemetryData(IntEnum):
    m_speed = 0,
    m_throttle = 1,
    m_steer = 2,
    m_brake = 3,
    m_clutch = 4,
    m_gear = 5,
    m_engineRPM = 6,
    m_drs = 7,
    m_revLightsPercent = 8,
    m_brakesTemperature1 = 9,
    m_brakesTemperature2 = 10,
    m_brakesTemperature3 = 11,
    m_brakesTemperature4 = 12,
    m_tyresSurfaceTemperature1 = 13,
    m_tyresSurfaceTemperature2 = 14,
    m_tyresSurfaceTemperature3 = 15,
    m_tyresSurfaceTemperature4 = 16,
    m_tyresInnerTemperature1 = 17,
    m_tyresInnerTemperature2 = 18,
    m_tyresInnerTemperature3 = 19,
    m_tyresInnerTemperature4 = 20,
    m_engineTemperature = 21,
    m_tyresPressure1 = 22,
    m_tyresPressure2 = 23,
    m_tyresPressure3 = 24,
    m_tyresPressure4 = 25,
    m_surfaceType1 = 26,
    m_surfaceType2 = 27,
    m_surfaceType3 = 28,
    m_surfaceType4 = 29,


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

def draw_rev(rev_lights):
    """ Draw the rev (RPM %) indicator on the left most column and top most row. """
    rpm_indicator_stop = round((rev_lights / 100.0) * len(RPM_LEDS))
    for l in range(len(RPM_LEDS)):
        led = RPM_LEDS[l]
        if l < rpm_indicator_stop:
            Led_matrix.set_pixel(led["col"], led["row"], led["red"], led["green"], led["blue"])
        else:
            Led_matrix.set_pixel(led["col"], led["row"], 0, 0, 0)

def main():
    """
    Listen on the F1 2020 UDP port for telemetry packets and
    update the 8x8 LED matrix.
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port. Listen on all interfaces.
    server_address = ('0.0.0.0', F1_UDP_PORT)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

    Led_matrix.set_layout(Led_matrix.AUTO)
    Led_matrix.rotation(0)
    Led_matrix.brightness(0.75)
    packet_header_format = '<HBBBBQfIBB'
    car_telemetry_format = '<HfffBbHBB4H4B4BH4f4B'

    while True:
        data, address = sock.recvfrom(4096)

        if len(data) >= calcsize(packet_header_format):
            m_packetFormat, m_gameMajorVersion, m_gameMinorVersion, \
                m_packetVersion, m_packetId, m_sessionUID, m_sessionTime, \
                m_frameIdentifier, m_playerCarIndex, \
                m_secondaryPlayerCarIndex = unpack_from(packet_header_format, data)
            #print('m_packetFormat', m_packetFormat)
            #print('m_packetId', m_packetId)
            #print('m_playerCarIndex', m_playerCarIndex)
            if m_packetFormat == 2020 and m_packetId == ePacketType.eCarTelemetry:
                offset = calcsize(packet_header_format) + \
                        (calcsize(car_telemetry_format) * m_playerCarIndex)
                fields = unpack_from(car_telemetry_format, data, offset)

                current_gear = fields[eCarTelemetryData.m_gear]
                print('m_gear', current_gear, GEAR_NAMES[current_gear])
                draw_gear(current_gear)

                rev_lights = fields[eCarTelemetryData.m_revLightsPercent]
                print('rev_lights', rev_lights)
                draw_rev(rev_lights)
                Led_matrix.show()


if __name__ == '__main__':
    main()
