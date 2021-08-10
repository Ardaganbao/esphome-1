#include "modbus_slave.h"
#include "esphome/core/log.h"

namespace esphome {
namespace modbus_slave {

static const char *const TAG = "modbus_slave";
#define readCRC(arr, length) word(arr[(length - MODBUS_CRC_LENGTH) + 1], arr[length - MODBUS_CRC_LENGTH])

void ModbusSlaveESP::setup() {
  if (this->flow_control_pin_ != nullptr) {
    this->flow_control_pin_->setup();
  }

  uint32_t baudrate = this->parent_->get_baud_rate();
}

void ModbusSlaveESP::loop() {

  
}

void ModbusSlaveESP::dump_config() {
  ESP_LOGCONFIG(TAG, "ModbusSlaveESP:");
  LOG_PIN("  Flow Control Pin: ", this->flow_control_pin_);
}

float ModbusSlaveESP::get_setup_priority() const {
  // After UART bus
  return setup_priority::BUS - 1.0f;
}

}  // namespace modbus_slave
}  // namespace esphome
