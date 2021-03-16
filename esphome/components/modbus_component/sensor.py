import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import (
    sensor,
    modbus,
    binary_sensor,
    text_sensor,
    modbus_component,
    switch,
)
from esphome.core import coroutine
from esphome.util import Registry

from esphome.const import (
    CONF_ID,
    ICON_EMPTY,
    CONF_ADDRESS,
    CONF_OFFSET,
    DEVICE_CLASS_EMPTY,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
)

from .const import (
    CONF_MODBUSDEVICE_ADDRESS,
    CONF_VALUE_TYPE,
    CONF_SCALE_FACTOR,
    CONF_REGISTER_COUNT,
    CONF_MODBUS_FUNCTIONCODE,
    CONF_COMMAND_THROTTLE,
    CONF_RESPONSE_SIZE,
    CONF_BITMASK,
    UNIT_AMPERE_HOURS,
    UNIT_KG,
    UNIT_KWATT_HOURS,
    UNIT_MILLIOHM,
    UNIT_HOURS,
)


AUTO_LOAD = [
    "modbus",
    "binary_sensor",
    "text_sensor",
    "status",
    "switch",
    "modbus_component",
]

modbus_component_ns = cg.esphome_ns.namespace("modbus_component")
ModbusComponent = modbus_component_ns.class_(
    "ModbusComponent", cg.PollingComponent, modbus.ModbusDevice
)

ModbusFunctionCode_ns = cg.esphome_ns.namespace("modbus_component::ModbusFunctionCode")
ModbusFunctionCode = ModbusFunctionCode_ns.enum("ModbusFunctionCode")
MODBUS_FUNCTION_CODE = {
    "read_coils": ModbusFunctionCode.READ_COILS,
    "read_discrete_inputs": ModbusFunctionCode.READ_DISCRETE_INPUTS,
    "read_holding_registers": ModbusFunctionCode.READ_HOLDING_REGISTERS,
    "read_input_registers": ModbusFunctionCode.READ_INPUT_REGISTERS,
    "write_single_coil": ModbusFunctionCode.WRITE_SINGLE_COIL,
    "write_single_register": ModbusFunctionCode.WRITE_SINGLE_REGISTER,
    "write_multiple_registers": ModbusFunctionCode.WRITE_MULTIPLE_REGISTERS,
}

SensorValueType_ns = cg.esphome_ns.namespace("modbus_component::SensorValueType")
SensorValueType = SensorValueType_ns.enum("SensorValueType")
SENSOR_VALUE_TYPE = {
    "RAW": SensorValueType.RAW,
    "U_WORD": SensorValueType.U_WORD,
    "S_WORD": SensorValueType.S_WORD,
    "U_DWORD": SensorValueType.U_DWORD,
    "U_DWORD_R": SensorValueType.U_DWORD_R,
    "S_DWORD": SensorValueType.S_DWORD,
    "S_DWORD_R": SensorValueType.S_DWORD_R,
    "U_QWORD": SensorValueType.U_QWORD,
    "U_QWORDU_R": SensorValueType.U_QWORD_R,
    "S_QWORD": SensorValueType.S_QWORD,
    "U_QWORD_R": SensorValueType.S_QWORD_R,
}

# Filters
# Filter = binary_sensor_ns.class_(" RAW_Filter")
# LambdaFilter = binary_sensor_ns.class_("LambdaFilter", Filter)
## not yet used: Filter operating at the raw modbus data
RAW_FILTER_REGISTRY = Registry()
validate_filters = cv.validate_registry("raw_filter", RAW_FILTER_REGISTRY)

MODBUS_REGISTRY = Registry()
validate_modbus_range = cv.validate_registry("sensors", MODBUS_REGISTRY)

sensor_entry = sensor.SENSOR_SCHEMA.extend(
    {
        cv.Optional(CONF_MODBUS_FUNCTIONCODE): cv.enum(MODBUS_FUNCTION_CODE),
        cv.Optional(CONF_ADDRESS): cv.int_,
        cv.Optional(CONF_OFFSET): cv.int_,
        cv.Optional(CONF_BITMASK, default=0xFFFFFFFF): cv.hex_uint32_t,
        cv.Optional(CONF_VALUE_TYPE): cv.enum(SENSOR_VALUE_TYPE),
        cv.Optional(CONF_SCALE_FACTOR): cv.float_,
        cv.Optional(CONF_REGISTER_COUNT, default=1): cv.int_,
    }
)

binary_sensor_entry = binary_sensor.BINARY_SENSOR_SCHEMA.extend(
    {
        cv.Optional(CONF_MODBUS_FUNCTIONCODE): cv.enum(MODBUS_FUNCTION_CODE),
        cv.Optional(CONF_ADDRESS): cv.int_,
        cv.Optional(CONF_OFFSET): cv.int_,
        cv.Optional(CONF_BITMASK, default=0x1): cv.hex_uint32_t,
    }
)

modbus_switch_entry = switch.SWITCH_SCHEMA.extend(
    {
        cv.Optional(CONF_MODBUS_FUNCTIONCODE): cv.enum(MODBUS_FUNCTION_CODE),
        cv.Optional(CONF_ADDRESS): cv.int_,
        cv.Optional(CONF_OFFSET): cv.int_,
        cv.Optional(CONF_BITMASK, default=0x1): cv.hex_uint32_t,
    }
).extend(cv.COMPONENT_SCHEMA)

text_sensor_entry = text_sensor.TEXT_SENSOR_SCHEMA.extend(
    {
        cv.Optional(CONF_MODBUS_FUNCTIONCODE): cv.enum(MODBUS_FUNCTION_CODE),
        cv.Optional(CONF_ADDRESS): cv.int_,
        cv.Optional(CONF_OFFSET): cv.int_,
        cv.Optional(CONF_RESPONSE_SIZE, default=0): cv.int_,
    }
)


def modbus_sensor_schema(
    modbus_functioncode_,
    register_address_,
    register_offset_,
    bitmask_,
    value_type_,
    scale_factor_,
    register_count_,
    unit_of_measurement_,
    icon_,
    accuracy_decimals_,
    device_class_=DEVICE_CLASS_EMPTY,
):
    if device_class_ == DEVICE_CLASS_EMPTY:
        if unit_of_measurement_ == UNIT_AMPERE:
            device_class_ = DEVICE_CLASS_CURRENT
        if unit_of_measurement_ == UNIT_CELSIUS:
            device_class_ = DEVICE_CLASS_TEMPERATURE
        if unit_of_measurement_ == UNIT_KWATT_HOURS:
            device_class_ = DEVICE_CLASS_ENERGY
        if unit_of_measurement_ == UNIT_WATT:
            device_class_ = DEVICE_CLASS_ENERGY
        if unit_of_measurement_ == UNIT_VOLT:
            device_class_ = DEVICE_CLASS_VOLTAGE
    return sensor.sensor_schema(
        unit_of_measurement_, icon_, accuracy_decimals_, device_class_
    ).extend(
        {
            cv.Optional(
                CONF_MODBUS_FUNCTIONCODE, default=modbus_functioncode_
            ): cv.enum(MODBUS_FUNCTION_CODE),
            cv.Optional(CONF_ADDRESS, default=register_address_): cv.int_,
            cv.Optional(CONF_OFFSET, default=register_offset_): cv.int_,
            cv.Optional(CONF_BITMASK, default=bitmask_): cv.hex_uint32_t,
            cv.Optional(CONF_VALUE_TYPE, default=value_type_): cv.enum(
                SENSOR_VALUE_TYPE
            ),
            cv.Optional(CONF_SCALE_FACTOR, default=scale_factor_): cv.float_,
            cv.Optional(CONF_REGISTER_COUNT, default=register_count_): cv.int_,
        }
    )


def modbus_binarysensor_schema(
    modbus_functioncode_, register_address_, register_offset_, bitmask_=1
):
    return binary_sensor.BINARY_SENSOR_SCHEMA.extend(
        {
            cv.Optional(
                CONF_MODBUS_FUNCTIONCODE, default=modbus_functioncode_
            ): cv.enum(MODBUS_FUNCTION_CODE),
            cv.Optional(CONF_ADDRESS, default=register_address_): cv.int_,
            cv.Optional(CONF_OFFSET, default=register_offset_): cv.int_,
            cv.Optional(CONF_BITMASK, default=bitmask_): cv.hex_uint32_t,
        }
    )


def modbus_switch_schema(
    modbus_functioncode_, register_address_, register_offset_, bitmask_=1
):
    return switch.SWITCH_SCHEMA.extend(
        {
            cv.Optional(
                CONF_MODBUS_FUNCTIONCODE, default=modbus_functioncode_
            ): cv.enum(MODBUS_FUNCTION_CODE),
            cv.Optional(CONF_ADDRESS, default=register_address_): cv.int_,
            cv.Optional(CONF_OFFSET, default=register_offset_): cv.int_,
            cv.Optional(CONF_BITMASK, default=bitmask_): cv.hex_uint32_t,
        }
    )


def modbus_textsensor_schema(
    modbus_functioncode_, register_address_, register_offset_, response_size_
):
    return text_sensor.TEXT_SENSOR_SCHEMA.extend(
        {
            cv.Optional(
                CONF_MODBUS_FUNCTIONCODE, default=modbus_functioncode_
            ): cv.enum(MODBUS_FUNCTION_CODE),
            cv.Optional(CONF_ADDRESS, default=register_address_): cv.int_,
            cv.Optional(CONF_OFFSET, default=register_offset_): cv.int_,
            cv.Optional(CONF_RESPONSE_SIZE, default=response_size_): cv.int_,
        }
    )


MODBUS_CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.Optional(CONF_MODBUSDEVICE_ADDRESS, default=0x1): cv.hex_uint8_t,
            cv.Optional(CONF_COMMAND_THROTTLE, default=0x0): cv.hex_uint16_t,
            cv.Optional("sensors"): cv.All(
                cv.ensure_list(sensor_entry), cv.Length(min=0)
            ),
            cv.Optional("binary_sensors"): cv.All(
                cv.ensure_list(binary_sensor_entry), cv.Length(min=0)
            ),
            cv.Optional("text_sensors"): cv.All(
                cv.ensure_list(text_sensor_entry), cv.Length(min=0)
            ),
            cv.Optional("switches"): cv.All(
                cv.ensure_list(modbus_switch_entry), cv.Length(min=0)
            ),
        }
    )
    .extend(cv.polling_component_schema("60s"))
    .extend(modbus.modbus_device_schema(0x01))
)


def modbus_component_schema(device_address=0x1):
    return (
        cv.Schema(
            {
                cv.Optional(CONF_MODBUSDEVICE_ADDRESS, default=0x1): cv.hex_uint8_t,
                cv.Optional(CONF_COMMAND_THROTTLE, default=0x0500): cv.hex_uint16_t,
                cv.Optional("sensors"): cv.All(
                    cv.ensure_list(sensor_entry), cv.Length(min=0)
                ),
                cv.Optional("binary_sensors"): cv.All(
                    cv.ensure_list(binary_sensor_entry), cv.Length(min=0)
                ),
                cv.Optional("text_sensors"): cv.All(
                    cv.ensure_list(text_sensor_entry), cv.Length(min=0)
                ),
                cv.Optional("switches"): cv.All(
                    cv.ensure_list(modbus_switch_entry), cv.Length(min=0)
                ),
            }
        )
        .extend(cv.polling_component_schema("60s"))
        .extend(modbus.modbus_device_schema(device_address))
    )


ALLBITS = 0xFFFFFFFF

CONFIG_SCHEMA = (
    MODBUS_CONFIG_SCHEMA.extend(
        {
            cv.GenerateID(): cv.declare_id(ModbusComponent),
        }
    )
    .extend(cv.polling_component_schema("60s"))
    .extend(modbus.modbus_device_schema(0x01))
)


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_COMMAND_THROTTLE])
    yield cg.add(var.set_command_throttle(config[CONF_COMMAND_THROTTLE]))
    yield cg.register_component(var, config)
    yield modbus.register_modbus_device(var, config)
    if config.get("sensors"):
        conf = config["sensors"]
        for s in conf:
            sens = yield sensor.new_sensor(s)
            cg.add(
                var.add_sensor(
                    sens,
                    s[CONF_MODBUS_FUNCTIONCODE],
                    s[CONF_ADDRESS],
                    s[CONF_OFFSET],
                    s[CONF_BITMASK],
                    s[CONF_VALUE_TYPE],
                    s[CONF_REGISTER_COUNT],
                )
            )
    if config.get("binary_sensors"):
        conf = config["binary_sensors"]
        for s in conf:
            sens = yield binary_sensor.new_binary_sensor(s)
            cg.add(
                var.add_binarysensor(
                    sens,
                    s[CONF_MODBUS_FUNCTIONCODE],
                    s[CONF_ADDRESS],
                    s[CONF_OFFSET],
                    s[CONF_BITMASK],
                )
            )
    if config.get("text_sensors"):
        conf = config["text_sensors"]
        for s in conf:
            sens = yield text_sensor.new_text_sensor(s)
            cg.add(
                var.add_textsensor(
                    sens,
                    s[CONF_MODBUS_FUNCTIONCODE],
                    s[CONF_ADDRESS],
                    s[CONF_OFFSET],
                    s[CONF_RESPONSE_SIZE],
                )
            )


@coroutine
def build_modbus_registers(config):
    yield cg.build_registry_list(MODBUS_REGISTRY, config)
