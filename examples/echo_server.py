#!/usr/bin/env python3

"""
##### RFM69 ECHO SERVER #####
This Python script implements a simple echo server using RFM69 Serial bridge.

"""

import time
from RFM69Serial import Rfm69SerialDevice

# Parameter set for physical boards
cs_pin = 7
int_pin = 0
device_addr = 1
network_id = 101
device_port = "/dev/ttyACM0"

dev = Rfm69SerialDevice(device_addr, network_id, cs_pin, int_pin, device_port)
print("Echo server program")
print("Server Address = ", device_addr)
print("Network ID = ", network_id)
print("--------------------")

msg_counter = 0

try:
    dev.begin_receive()
    while True:
        if dev.receive_done():
            msg_counter += 1
            recv = dev.get_rx_data()
            print(f"Message [{msg_counter}]: Sender ID = {recv.sender} | Msg = {recv.message_to_string()} ")
            time.sleep(0.2)
            dev.send_msg(recv.sender, recv.message_to_string())
            dev.begin_receive()

except KeyboardInterrupt:
    dev.sleep()
    dev.close()
    print("Stopped by user!")
