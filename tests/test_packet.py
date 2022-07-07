import unittest
from RFM69Serial import RFM69Packet


class TestRFM69Packet(unittest.TestCase):
    def setUp(self) -> None:
        # instantiate a packet object which is sent from fake sender @ address 10
        self.testPacket = RFM69Packet(10)
        self.testData = [0x68, 0x65, 0x6C, 0x6C, 0x6F, 0x20, 0x77, 0x6F, 0x72, 0x6C, 0x64]

    def test_packet(self):
        self.assertIsInstance(self.testPacket, RFM69Packet)
        self.assertEqual(10, self.testPacket.sender)
        self.testPacket.message = self.testData
        self.assertIsInstance(self.testPacket.message, list)
        self.assertEqual('hello world', self.testPacket.message_to_string())
