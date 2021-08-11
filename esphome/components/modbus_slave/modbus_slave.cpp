#include "modbus_slave.h"
#include "esphome/core/log.h"
#include "ModbusSlave.h"

namespace esphome {
namespace modbus_slave {


uint8_t input_pins[] = {2, 3, 4};     // Add the pins you want to read as a Discrete input.
 
// You shouldn't have to change anything below this to get this example to work

uint8_t input_pins_size = sizeof(input_pins) / sizeof(input_pins[0]);    // Get the size of the input_pins array
 


static const char *const TAG = "modbus_slave";
#define readCRC(arr, length) word(arr[(length - MODBUS_CRC_LENGTH) + 1], arr[length - MODBUS_CRC_LENGTH])

void ModbusSlaveESP::setup() {
  if (this->flow_control_pin_ != nullptr) {
    this->flow_control_pin_->setup();
  }

  uint32_t baudrate = this->parent_->get_baud_rate();


    // Set the defined input pins to input mode.
    for (int i = 0; i < input_pins_size; i++)
    {
        pinMode(input_pins[i], INPUT);
    }
 
 

    // Register functions to call when a certain function code is received. 
    this->cbVector[CB_READ_DISCRETE_INPUTS] = readDigitalIn; 

}
// read any new data from uart
void ModbusSlaveESP::read_uart() {
  const uint32_t now = millis();
  if (now - this->last_modbus_byte_ > 50) {
    this->rx_buffer_.clear();
    this->last_modbus_byte_ = now;
  }

  while (this->available()) {
    uint8_t byte{0};
    this->read_byte(&byte);
    if (this->parse_modbus_byte_(byte)) {
      this->last_modbus_byte_ = now;
    } else {
      this->rx_buffer_.clear();
    }
  }
}

void ModbusSlaveESP::loop() {
 read_uart();
 
}
bool ModbusSlaveESP::parse_modbus_byte_(uint8_t byte) {
 ESP_LOGW(TAG, "arda: parse_modbus_byte_  0x%X", byte);
return false;
}
void ModbusSlaveESP::dump_config() {
  ESP_LOGCONFIG(TAG, "ModbusSlaveESP:");
  LOG_PIN("  Flow Control Pin: ", this->flow_control_pin_);
}

float ModbusSlaveESP::get_setup_priority() const {
  // After UART bus
  return setup_priority::BUS - 1.0f;
}

 

// Handle the function code Read Input Status (FC=02) and write back the values from the digital input pins (discreet input).
uint8_t  readDigitalIn(uint8_t fc, uint16_t address, uint16_t length)
{
   
    return STATUS_OK;
}
  

}  // namespace modbus_slave
}  // namespace esphome
