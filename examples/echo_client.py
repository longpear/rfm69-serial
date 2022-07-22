import time
from RFM69Serial import Rfm69SerialDevice

# Parameter set for physical boards
cs_pin = 10
int_pin = 8
device_addr = 3
server_addr = 2
network_id = 101
device_port = "/dev/ttyACM0"

dev = Rfm69SerialDevice(device_addr, network_id, cs_pin, int_pin, device_port)
if dev.is_device_connected():
    print("Serial device is online, RF module is ready!")
# dev.encrypt(key='a1b2c3d4e5f6g7h8')

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
