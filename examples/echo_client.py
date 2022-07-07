import time
from RFM69Serial import Rfm69SerialDevice

# Parameter set for physical boards
cs_pin = 7
int_pin = 0
device_addr = 2
server_addr = 1
network_id = 101
device_port = "/dev/ttyACM0"

dev = Rfm69SerialDevice(device_addr, network_id, cs_pin, int_pin, device_port)
print("Echo client program")
print("Client Address = ", device_addr)
print("Server address = ", server_addr)
print("--------------------")

try:
    while True:
        msg = input("> ")
        dev.send_msg(server_addr, msg, ack_request=False)
        t_start = time.perf_counter()
        dev.begin_receive()
        while time.perf_counter() - t_start < 1:
            if dev.receive_done():
                recv = dev.get_rx_data()
                if recv.sender == device_addr:
                    print("echoed: ", recv.message_to_string())


except KeyboardInterrupt:
    dev.sleep()
    dev.close()
    print("Stopped by user!")
