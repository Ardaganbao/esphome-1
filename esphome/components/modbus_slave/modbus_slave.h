#pragma once

#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"

#define MODBUS_FRAME_SIZE 4
#define MODBUS_CRC_LENGTH 2

#define MODBUS_ADDRESS_INDEX 0
#define MODBUS_FUNCTION_CODE_INDEX 1
#define MODBUS_DATA_INDEX 2

#define MODBUS_BROADCAST_ADDRESS 0
#define MODBUS_ADDRESS_MIN 1
#define MODBUS_ADDRESS_MAX 247

#define MODBUS_HALF_SILENCE_MULTIPLIER 3
#define MODBUS_FULL_SILENCE_MULTIPLIER 7

#define MODBUS_MAX_BUFFER 256
#define MODBUS_INVALID_UNIT_ADDRESS 255
#define MODBUS_DEFAULT_UNIT_ADDRESS 1

namespace esphome {
namespace modbus_slave {
/**
 * Modbus function codes
 */
enum {
  FC_INVALID = 0,
  FC_READ_COILS = 1,
  FC_READ_DISCRETE_INPUT = 2,
  FC_READ_HOLDING_REGISTERS = 3,
  FC_READ_INPUT_REGISTERS = 4,
  FC_WRITE_COIL = 5,
  FC_WRITE_REGISTER = 6,
  FC_READ_EXCEPTION_STATUS = 7,
  FC_WRITE_MULTIPLE_COILS = 15,
  FC_WRITE_MULTIPLE_REGISTERS = 16
};

enum {
  CB_READ_COILS = 0,
  CB_READ_DISCRETE_INPUTS,
  CB_READ_HOLDING_REGISTERS,
  CB_READ_INPUT_REGISTERS,
  CB_WRITE_COILS,
  CB_WRITE_HOLDING_REGISTERS,
  CB_READ_EXCEPTION_STATUS,
  CB_MAX
};

enum { COIL_OFF = 0x0000, COIL_ON = 0xff00 };

enum {
  STATUS_OK = 0,
  STATUS_ILLEGAL_FUNCTION,
  STATUS_ILLEGAL_DATA_ADDRESS,
  STATUS_ILLEGAL_DATA_VALUE,
  STATUS_SLAVE_DEVICE_FAILURE,
  STATUS_ACKNOWLEDGE,
  STATUS_SLAVE_DEVICE_BUSY,
  STATUS_NEGATIVE_ACKNOWLEDGE,
  STATUS_MEMORY_PARITY_ERROR,
  STATUS_GATEWAY_PATH_UNAVAILABLE,
  STATUS_GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND,
};
typedef uint8_t (*ModbusCallback)(uint8_t, uint16_t, uint16_t);
class ModbusSlaveFunction;

class ModbusSlaveESP : public uart::UARTDevice, public Component {
 public:
  ModbusSlaveESP() = default;

  void setup() override;

  void loop() override;

  void dump_config() override;

  

  float get_setup_priority() const override;
 
  void set_flow_control_pin(GPIOPin *flow_control_pin) { this->flow_control_pin_ = flow_control_pin; }
   
 protected:
  GPIOPin *flow_control_pin_{nullptr};  
  
 
};
 

/**
 * @class ModbusSlaveFunction

class ModbusSlaveFunction {
 public:
  ModbusSlaveFunction(uint8_t unitAddress = MODBUS_DEFAULT_UNIT_ADDRESS);
  uint8_t getUnitAddress();
  void setUnitAddress(uint8_t unitAddress);
  ModbusCallback cbVector[CB_MAX];

 private:
  uint8_t _unitAddress = MODBUS_DEFAULT_UNIT_ADDRESS;



  uint16_t writeResponse();
}; */

}  // namespace modbus_slave
}  // namespace esphome
