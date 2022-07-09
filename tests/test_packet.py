import unittest
from RFM69Serial import RFM69Packet


class TestRFM69Packet(unittest.TestCase):
    def setUp(self) -> None:
        # instantiate a packet object which is sent from fake sender @ address 10
        self.testPacket = RFM69Packet(10)
        self.testData = [b'\x68', b'\x65', b'\x6C', b'\x6C', b'\x6F', b'\x20', b'\x77', b'\x6F', b'\x72', b'\x6C',
                         b'\x64']

    def test_packet(self):
        self.assertIsInstance(self.testPacket, RFM69Packet)
        self.assertEqual(10, self.testPacket.sender)
        self.testPacket.message = self.testData
        self.assertIsInstance(self.testPacket.message, list)
        self.assertEqual('hello world', self.testPacket.message_to_string())
