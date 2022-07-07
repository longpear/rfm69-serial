// **********************************************************************************
//            !!!!     RFM69 USB SERIAL BRIDGE DEVICE  !!!!
//
// This program is modified from LowPowerLab's RFM69 example to implement a Serial bridge
// between RFM69 device and PC Linux (with no SPI connection).
// The dataflow is as shown below:
// PC (usb uart/serial) <--> (serial) Arduino Board (SPI master) <--> (SPI slave) RFM69 Module
// **********************************************************************************

#include <RFM69.h>
#include "RFM69registers.h"

//*********************************************************************************************
//************ IMPORTANT SETTINGS - YOU MUST CHANGE/CONFIGURE TO FIT YOUR HARDWARE ************
//*********************************************************************************************
// Address IDs are 10bit, meaning usable ID range is 1..1023
// Address 0 is special (broadcast), messages to address 0 are received by all *listening* nodes (ie. active RX mode)
// Gateway ID should be kept at ID=1 for simplicity, although this is not a hard constraint
//*********************************************************************************************
#define NODEID        1    // keep UNIQUE for each node on same network
#define NETWORKID     101  // keep IDENTICAL on all nodes that talk to each other

//*********************************************************************************************
// Frequency should be set to match the radio module hardware tuned frequency,
// otherwise if say a "433mhz" module is set to work at 915, it will work but very badly.
// Moteinos and RF modules from LowPowerLab are marked with a colored dot to help identify their tuned frequency band,
// see this link for details: https://lowpowerlab.com/guide/moteino/transceivers/
// The below examples are predefined "center" frequencies for the radio's tuned "ISM frequency band".
// You can always set the frequency anywhere in the "frequency band", ex. the 915mhz ISM band is 902..928mhz.
//*********************************************************************************************

#define FREQUENCY     RF69_915MHZ
//#define FREQUENCY_EXACT 916000000 // you may define an exact frequency/channel in Hz
//#define ENCRYPTKEY    "sampleEncryptKey" //exactly the same 16 characters/bytes on all nodes!
#define IS_RFM69HW_HCW  //uncomment only for RFM69HW/HCW! Leave out if you have RFM69W/CW!

// Default fictional chip select and interrupt pins
// Actual pins is decided by Python object instantiation.
#define CS_PIN  0
#define INT_PIN 1

// Global Variables
const char ok_code = 'y';
const char ko_code = 'n';

uint8_t SERIAL_MSG[64];

RFM69 radio {CS_PIN, INT_PIN, false};

// Prototype
void begin_receive();
void requestHandler( uint8_t );


// ***** SETUP *****

void setup() {
  // For Arduino boards, Serial initialization may be necessary.
  // For Teensyduino, it is ignored!
  //Serial.begin(9600);
}

// ***** MAIN LOOP *****

void loop() {
  // Polling continuously for Serial requests
  int byteCounter = 0;

  while (Serial.available()) {
    //delayMicroseconds(500); // Hardware delay buffer if Serial port is too slow.
    SERIAL_MSG[byteCounter] = (uint8_t)Serial.read();
    byteCounter += 1;
  }

  if (byteCounter != 0) {
    requestHandler(SERIAL_MSG[1]);
  } // end if
} // end loop


// ***** Utility functions *****

// make receiveBegin() public method by copying it here
void begin_receive() {
  radio.DATALEN = 0;
  radio.SENDERID = 0;
  radio.TARGETID = 0;
  radio.PAYLOADLEN = 0;
  radio.ACK_REQUESTED = 0;
  radio.ACK_RECEIVED = 0;
  radio.RSSI = 0;

  if (radio.readReg(REG_IRQFLAGS2) & RF_IRQFLAGS2_PAYLOADREADY)
    radio.writeReg(REG_PACKETCONFIG2, (radio.readReg(REG_PACKETCONFIG2) & 0xFB) | RF_PACKET2_RXRESTART); // avoid RX deadlocks
  radio.writeReg(REG_DIOMAPPING1, RF_DIOMAPPING1_DIO0_01); // set DIO0 to "PAYLOADREADY" in receive mode
  radio.setMode(RF69_MODE_RX);
}

// request handler
void requestHandler(uint8_t opcode) {
  bool ACK_Requested = false;
  int16_t rssi_v = 0;
  char encrypt_key[16];

  uint8_t msg[60];

  switch (opcode) {
    
    case 0x00: {
      // SERIAL_MSG[2] = device address
      // SERIAL_MSG[3] = network ID
      // SERIAL_MSG[4] = chip select pin
      // SERIAL_MSG[5] = interrupt pin
      radio.setCS((uint8_t)SERIAL_MSG[4]);
      radio.setIrq((uint8_t)SERIAL_MSG[5]);
      if (radio.initialize(FREQUENCY, (uint8_t)SERIAL_MSG[2], (uint8_t)SERIAL_MSG[3])) {
#ifdef IS_RFM69HW_HCW
        radio.setHighPower(); //must include this only for RFM69HW/HCW!
#endif
        Serial.write(ok_code);
      }
      else
        Serial.write(ko_code);
      break;
    }
    
    case 0x01: {
      // SERIAL_MSG[2] = device address
      radio.setAddress(SERIAL_MSG[2]);
      Serial.write(ok_code);
      break;
    }

    case 0x02: {
      // SERIAL_MSG[2] = network ID
      radio.setNetwork(SERIAL_MSG[2]);
      Serial.write(ok_code);
      break;
    }

    case 0x03: {
      // SERIAL_MSG[2] = target ID
      // SERIAL_MSG[3] = ACK Requested?
      // SERIAL_MSG[4] = msg length (max 64)
      // SERIAL_MSG[5 -> msg_length] = msg
      for (int i = 0; i < SERIAL_MSG[4]; i++)
        msg[i] = SERIAL_MSG[i+5];

      ACK_Requested = (SERIAL_MSG[3] == 0) ? false : true;

      radio.send(SERIAL_MSG[2], msg, SERIAL_MSG[4], ACK_Requested);
      Serial.write(ok_code);
      break;
    }

    case 0x04: {
      // SERIAL_MSG[2] = target ID
      // SERIAL_MSG[3] = no of retries (max 255)
      // SERIAL_MSG[4] = time out (max 255 ms)
      // SERIAL_MSG[5] = msg length (max 64)
      // SERIAL_MSG[6 -> msg_length] = msg
      for (int i = 0; i < SERIAL_MSG[4]; i++)
        msg[i] = SERIAL_MSG[i+6];

      if (radio.sendWithRetry(SERIAL_MSG[2], msg, SERIAL_MSG[5], SERIAL_MSG[3], SERIAL_MSG[4]))
        Serial.write(ok_code);
      else
        Serial.write(ko_code);
      break;
    }

    case 0x05: {
      begin_receive();
      Serial.write(ok_code);
      break;
    }

    case 0x06: {
      if (radio.receiveDone())
        Serial.write(ok_code);
      else
        Serial.write(ko_code);
      break;
    }

    case 0x07: {
      // SERIAL_MSG[2] = target ID
      if (radio.ACKReceived(SERIAL_MSG[2]))
        Serial.write(ok_code);
      else
        Serial.write(ko_code);
      break;
    }

    case 0x08: {
      if (radio.ACKRequested())
        Serial.write(ok_code);
      else
        Serial.write(ko_code);
      break;
    }

    case 0x09: {
      // SERIAL_MSG[2] = msg_length (max 64)
      // SERIAL_MSG[3 -> msg_length] = msg
      for (int i = 0; i < SERIAL_MSG[2]; i++)
        msg[i] = SERIAL_MSG[i+3];
      radio.sendACK(msg, SERIAL_MSG[2]);
      Serial.write(ok_code);
      break;
    }

    case 0x0A: {
      // return 3 right most bytes of frequency (uint32_t)
      // require readReg()
      uint8_t REG_frfmsb = radio.readReg(REG_FRFMSB);
      uint8_t REG_frfmid = radio.readReg(REG_FRFMID);
      uint8_t REG_frflsb = radio.readReg(REG_FRFLSB);
      Serial.write(ok_code);
      Serial.write(REG_frfmsb);
      Serial.write(REG_frfmid);
      Serial.write(REG_frflsb);
      break;
    }

    case 0x0B: {
      // This opcode just decorates setFrequency() function only, nothing else
      // SERIAL_MSG[2] = LSB Carrier Frequency
      // SERIAL_MSG[3] = Lower Middle Byte Carrier Frequency
      // SERIAL_MSG[4] = Upper Middle Byte Carrier Frequency
      // SERIAL_MSG[5] = MSB Carrier Frequency
      uint32_t freq = ((SERIAL_MSG[5] << 24) | (SERIAL_MSG[4] << 16) | (SERIAL_MSG[3] << 8) | SERIAL_MSG[2]);
      radio.setFrequency(freq);
      Serial.write(ok_code);
      break;
    }

    case 0x0C: {
      // SERIAL_MSG[2] = enable encryption ?
      // SERIAL_MSG[3 -> 18] = key if enabled
      for (int i = 0; i < 16; i++)
        encrypt_key[i] = (char)SERIAL_MSG[i+3];

      if (SERIAL_MSG[2] == 0)
        radio.encrypt(0);
      else
        radio.encrypt(encrypt_key);
      Serial.write(ok_code);
      break;
    }

    case 0x0D: {
      // SERIAL_MSG[2] = CS pin
      radio.setCS((uint8_t)SERIAL_MSG[2]);
      Serial.write(ok_code);
      break;
    }

    case 0x0E: {
      // SERIAL_MSG[2] = INT0 pin
      radio.setIrq((uint8_t)SERIAL_MSG[2]);
      Serial.write(ok_code);
      break;
    }

    case 0x0F: {
      // SERIAL_MSG[2] = forceTrigger ?
      rssi_v = -radio.readRSSI(SERIAL_MSG[2]);
      Serial.write(ok_code);
      Serial.write((uint8_t)rssi_v);
      break;
    }

    case 0x10: {
      // SERIAL_MSG[2] = enabled ?
      radio.spyMode(SERIAL_MSG[2]);
      Serial.write(ok_code);
      break;
    }

    case 0x11: {
      // SERIAL_MSG[2] = enabled ?
      radio.setHighPower(SERIAL_MSG[2]);
      Serial.write(ok_code);
      break;
    }

    case 0x12: {
      // SERIAL_MSG[2] = power level (max 255)
      radio.setPowerLevel(SERIAL_MSG[2]);
      Serial.write(ok_code);
      break;
    }

    case 0x13: {
      // pass
      break;
    }

    case 0x14: {
      // NO ARG
      Serial.write(ok_code);
      Serial.write(radio.getPowerLevel());
      break;
    }

    case 0x15: {
      // NO ARG
      radio.sleep();
      Serial.write(ok_code);
      break;
    }

    case 0x16: {
      // SERIAL_MSG[2] = caclFactor
      Serial.write(ok_code);
      Serial.write(radio.readTemperature(SERIAL_MSG[2]));
      break;
    }

    case 0x17: {
      // NO ARG
      radio.rcCalibration();
      Serial.write(ok_code);
      break;
    }

    case 0x18: {
      // NO ARG
      radio.set300KBPS();
      Serial.write(ok_code);
      break;
    }

    case 0x19: {
      // SERIAL_MSG[2] = newReg
      Serial.write(ok_code);
      Serial.write(radio.setLNA(SERIAL_MSG[2]));
      break;
    }

    case 0x1A: {
      // SERIAL_MSG[2] = Register Address
      Serial.write(ok_code);
      Serial.write(radio.readReg(SERIAL_MSG[2]));
      break;
    }

    case 0x1B: {
      // SERIAL_MSG[2] = Register Address
      // SERIAL_MSG[3] = Register Value
      radio.writeReg(SERIAL_MSG[2], SERIAL_MSG[3]);
      Serial.write(ok_code);
      break;
    }

    // ... //

    case 0x1E: {
      SERIAL_MSG[0] = radio.SENDERID;
      for (int i = 1; i <= radio.DATALEN; i++)
        SERIAL_MSG[i] = radio.DATA[i-1];
      Serial.write(ok_code);
      Serial.write(SERIAL_MSG, radio.DATALEN+1);
      break;
    }

    case 0x1F: {
      Serial.write(ok_code);
      break;
    }

    default: {
      // invalid opcode, send back ko_code
      Serial.write(ko_code);
      break;
    }
  } // end switch ... case
} // end function
