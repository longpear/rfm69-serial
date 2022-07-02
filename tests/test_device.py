import time
import unittest
from RFM69Serial import Rfm69SerialDevice


class TestRfm69SerialDevice(unittest.TestCase):
    def setUp(self) -> None:
        self.test_device = Rfm69SerialDevice()

    def test_good_instance(self):
        self.assertIsInstance(self.test_device, Rfm69SerialDevice)

        # Test initial values
        self.assertEqual(1, self.test_device.device_address)
        self.assertEqual(101, self.test_device.network_id)

    def test_device_connected(self):
        self.assertTrue(self.test_device.is_device_connected())

    def test_roundtrip(self):
        """Sending a message and receive it back from the receiver

        This test combines multiple methods to perform some sort of loopback
        testing for communication purpose
        """

        test_string = "test"
        return_string = ''
        target_addr = 2

        self.test_device.send_msg(target_addr, test_string)
        t_start = time.perf_counter()
        self.test_device.begin_receive()
        while time.perf_counter() - t_start < 0.5:
            if self.test_device.receive_done():
                recv_data = self.test_device.get_rx_data()[1:]
                for item in recv_data:
                    return_string += chr(item)
                self.assertEqual(test_string, return_string)
                break
        else:
            print("Test Failed because of Time-out, pls check serial connection!")

    def test_get_rssi(self):
        rssi_value = self.test_device.get_rssi()
        self.assertIsInstance(rssi_value, int)
        print("Current RSSI = ", rssi_value)

    def test_frequency_setting(self):
        freq = self.test_device.get_frequency()
        print("Current frequency = ", freq)
        self.test_device.set_frequency(916000000)
        freq = self.test_device.get_frequency()
        print("New frequency = ", freq)

    def test_read_register(self):
        """This test confirms the validity of read_register() method

        In default system start-up by Arduino library, the register @address 0x38 specifies payload length,
        which is 66.
        Let's test the register value using read_register method
        """
        reg_addr = b'\x38'
        reg_value = self.test_device.read_register(reg_addr)
        self.assertEqual(66, ord(reg_value))

    def test_write_register(self):
        """This test confirms the validity of write_register() method

        In this test, we try to modify network ID which resides at register address 0x30
        Then, we read it back to confirm the correctness of write-register function
        """

        reg_addr = b'\x30'
        reg_value = b'\x36'
        self.test_device.write_register(reg_addr, reg_value)
        time.sleep(1)
        recv_value = self.test_device.read_register(reg_addr)
        self.assertEqual(reg_value, recv_value)


