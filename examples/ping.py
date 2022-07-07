#!/usr/bin/env python3

import sys
import time
from RFM69Serial import Rfm69SerialDevice

# Parameter set for physical boards
cs_pin = 10
int_pin = 8
device_addr = 2
server_addr = 1
network_id = 101
device_port = "/dev/ttyACM0"

buf = 'ping'

dev = Rfm69SerialDevice(device_addr, network_id, cs_pin, int_pin, device_port)

print("Device connected!")
print("Input 's' for single burst")
print("Input 'a' for automatic ping (KBInterrupt to stop)")
print("------------------------------------------------")

try:
    while True:
        cmd = input("> ")

        if cmd == 'q':
            print("Stopped by user")
            dev.close()
            sys.exit(0)
        elif cmd == 's':
            t_start = time.perf_counter()
            dev.send_msg(server_addr, buf, ack_request=False)
            dev.begin_receive()
            while (time.perf_counter() - t_start) < 0.1:
                if dev.receive_done():
                    delay = (time.perf_counter() - t_start) * 1000
                    recv = dev.get_rx_data()
                    if recv.sender == server_addr:
                        print("Ping(ms) = ", round(delay-5))
                        break
            else:
                print("Time-out")

        elif cmd == 'a':
            while True:
                time.sleep(1)
                t_start = time.perf_counter()
                dev.send_msg(server_addr, buf, ack_request=False)
                dev.begin_receive()
                while (time.perf_counter() - t_start) < 0.5:
                    if dev.receive_done():
                        delay = (time.perf_counter() - t_start) * 1000
                        recv = dev.get_rx_data()
                        if recv.sender == server_addr:
                            print("Ping(ms) = ", round(delay - 5))
                            break
                else:
                    print("Time-out")

        else:
            print("Invalid command!")

except KeyboardInterrupt:
    print("Stopped by user")
    dev.close()
    sys.exit(0)

