#pragma once

#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"

namespace esphome {
namespace modbus_slave {

class ModbusSlaveDevice;

class ModbusSlaveESP : public uart::UARTDevice, public Component {
 public:
  ModbusSlaveESP() = default;

  void setup() override;

  void loop() override;

  void dump_config() override;

  void register_device(ModbusSlaveESPDevice *device) { this->devices_.push_back(device); }

  float get_setup_priority() const override;

  void send(uint8_t address, uint8_t function, uint16_t start_address, uint16_t register_count);

  void set_flow_control_pin(GPIOPin *flow_control_pin) { this->flow_control_pin_ = flow_control_pin; }

  void registerdevice(ModbusSlaveESPDevice *device);

 protected:
  GPIOPin *flow_control_pin_{nullptr};

  bool parse_modbus_byte_(uint8_t byte);  
  
  std::vector<uint8_t> rx_buffer_;
  uint32_t last_modbus_byte_{0};
  std::vector<ModbusSlaveESPDevice *> devices_;
};

uint16_t crc16(const uint8_t *data, uint8_t len);

class ModbusSlaveESPDevice :     public Component{
 public:
  void set_parent(ModbusSlaveESP *parent) { parent_ = parent; }
  void set_address(uint8_t address) { address_ = address; }
  virtual void on_modbus_data(const std::vector<uint8_t> &data) = 0;

  void send(uint8_t function, uint16_t start_address, uint16_t register_count) {
    this->parent_->send(this->address_, function, start_address, register_count);
  }

 protected:
  friend ModbusSlaveESP;

  ModbusSlaveESP *parent_;
  uint8_t address_;
};

}  // namespace modbus_slave
}  // namespace esphome
