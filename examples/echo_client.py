#!/usr/bin/env python3

"""
##### RFM69 ECHO CLIENT SCRIPT #####
This program takes input from user, then sends it to server side through RFM69 network.
The program expects the same message echoed from the server, then displays the messase and signal strength.
"""

import time
from RFM69Serial import Rfm69SerialDevice

# Parameter set for physical boards
cs_pin = 7  # Arduino MKRZERO Client
int_pin = 0
device_addr = 2
server_addr = 1
network_id = 101
device_port = "/dev/ttyACM0"    # `ls /dev` to find out your device port

# instantiate serial device object
dev = Rfm69SerialDevice(device_addr, network_id, cs_pin, int_pin, device_port)
if dev.is_device_connected():
    print("Serial device is online, RF module is ready!")

dev.encrypt(key='a1b2c3d4e5f6g7h8')     # Comment out to disable encryption feature

# Main program
print("Echo client program")
print("Client Address = ", device_addr)
print("Server address = ", server_addr)
print("--------------------")

try:
    while True:
        msg = input("> ")
        if not dev.send_msg(server_addr, msg, ack_request=False):
            print("Sent failed!")

        t_start = time.perf_counter()
        dev.begin_receive()
        while time.perf_counter() - t_start < 1:
            if dev.receive_done():
                recv = dev.get_rx_data()
                if recv.sender == server_addr:
                    print("echoed: ", recv.message_to_string())
                    print("RSSI = ", dev.get_rssi())


except KeyboardInterrupt:
    dev.sleep()
    dev.close()
    print("Stopped by user!")
