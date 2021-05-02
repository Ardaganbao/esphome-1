
#include "modbuscontroller.h"
#include "modbus_switch.h"

namespace esphome {
namespace modbus_controller {

static const char *TAG = "modbus_switch";

// ModbusSwitch
void ModbusSwitch::log() { LOG_SWITCH(TAG, get_name().c_str(), this); }

void ModbusSwitch::add_to_controller(ModbusController *master, ModbusFunctionCode register_type, uint16_t start_address,
                                     uint8_t offset, uint32_t bitmask) {
  /*
    Create a binary-sensor with a flag auto_switch . if true automatically create an assoociated switch object for
    this address and makes the sensor internal
    ... or maybe vice versa ?

  */
  this->register_type = register_type;
  this->start_address = start_address;
  this->bitmask = bitmask;
  this->offset = offset;
  this->sensor_value_type = SensorValueType::BIT;
  this->last_value = INT64_MIN;
  this->register_count = 1;
  this->skip_updates = 0;
  this->parent_ = master;
}

float ModbusSwitch::parse_and_publish(const std::vector<uint8_t> &data) {
  bool value = (data[0] != 0);
  switch (this->register_type) {
    case ModbusFunctionCode::READ_DISCRETE_INPUTS:
      //      value = data[this->offset] & 1;  // Discret Input is always just one bit
      value = coil_from_vector(this->offset, data);
      break;
    case ModbusFunctionCode::READ_COILS:
      // offset for coil is the actual number of the coil not the byte offset
      value = coil_from_vector(this->offset, data);
      break;
    default:
      value = get_data<uint16_t>(data, this->offset) & this->bitmask;
      break;
  }

  return value;
}

void ModbusSwitch::write_state(bool state) {
  // This will be called every time the user requests a state change.
  if (parent_ == nullptr) {
    // switch not configued correctly
    ESP_LOGE(TAG, "ModbusSwitch: %s : missing parent", this->get_name().c_str());
    return;
  }
  ModbusCommandItem cmd;
  ESP_LOGD(TAG, "write_state for ModbusSwitch '%s': new value = %d  type = %d address = %X offset = %x",
           this->get_name().c_str(), state, (int) this->register_type, this->start_address, this->offset);
  switch (this->register_type) {
    case ModbusFunctionCode::WRITE_SINGLE_COIL:
      cmd = ModbusCommandItem::create_write_single_coil(parent_, this->start_address + this->offset, state);
      break;
    case ModbusFunctionCode::WRITE_SINGLE_REGISTER:
      cmd = ModbusCommandItem::create_write_single_command(parent_, this->start_address,
                                                           state ? 0xFFFF & this->bitmask : 0);
      break;
    default:
      ESP_LOGE(TAG, "Invalid function code for ModbusSwitch: %d", (int) this->register_type);
      return;
      break;
  }
  parent_->queue_command(std::move(cmd));
  publish_state(state);
}
// ModbusSwitch end
}  // namespace modbus_controller
}  // namespace esphome