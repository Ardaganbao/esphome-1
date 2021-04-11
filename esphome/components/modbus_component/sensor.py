import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.components import mqtt
from esphome.components import (
    sensor,
    modbus,
    binary_sensor,
    text_sensor,
    switch,
)
from esphome.core import coroutine
from esphome.util import Registry
from esphome.cpp_types import App

from esphome.const import (
    CONF_ID,
    CONF_ADDRESS,
    CONF_OFFSET,
    CONF_TRIGGER_ID,
    CONF_NAME,
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
    CONF_SKIP_UPDATES,
    CONF_HEX_ENCODE,
)

CODEOWNERS = ["@martgras"]

AUTO_LOAD = [
    "modbus",
    "binary_sensor",
    "text_sensor",
    "status",
    "switch",
    "modbus_component",
]


# pylint: disable=invalid-name
text_sensor_ns = cg.esphome_ns.namespace("text_sensor")
TextSensor = text_sensor_ns.class_("TextSensor", cg.Nameable)

modbus_component_ns = cg.esphome_ns.namespace("modbus_component")
ModbusComponent = modbus_component_ns.class_(
    "ModbusComponent", cg.PollingComponent, modbus.ModbusDevice
)
RawData = modbus_component_ns.struct("RawData")
RawDataCodeTrigger = modbus_component_ns.class_(
    "RawDataCodeTrigger", automation.Trigger.template(RawData)
)

ModbusSwitch = modbus_component_ns.class_("ModbusSwitch", switch.Switch, cg.Component)


ModbusFunctionCode_ns = cg.esphome_ns.namespace("modbus_component::ModbusFunctionCode")
ModbusFunctionCode = ModbusFunctionCode_ns.enum("ModbusFunctionCode")
MODBUS_FUNCTION_CODE = {
    "read_coils": ModbusFunctionCode.READ_COILS,
    "read_discrete_inputs": ModbusFunctionCode.READ_DISCRETE_INPUTS,
    "read_holding_registers": ModbusFunctionCode.READ_HOLDING_REGISTERS,
    "read_input_registers": ModbusFunctionCode.READ_INPUT_REGISTERS,
    "write_single_coil": ModbusFunctionCode.WRITE_SINGLE_COIL,
    "write_single_register": ModbusFunctionCode.WRITE_SINGLE_REGISTER,
    "write_multiple_coils": ModbusFunctionCode.WRITE_MULTIPLE_COILS,
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

CONF_ON_RAW = "on_raw"
CONF_MQTT_ID2 = "mqtt_id_sensorswitch"
CONF_CREATE_SWITCH = "create_switch"

# CONF_SWITCH_ID = "modbusswitch_id"

MODBUS_REGISTRY = Registry()
validate_modbus_range = cv.validate_registry("sensors", MODBUS_REGISTRY)

sensor_entry = sensor.SENSOR_SCHEMA.extend(
    {
        cv.Optional(CONF_MODBUS_FUNCTIONCODE): cv.enum(MODBUS_FUNCTION_CODE),
        cv.Optional(CONF_ADDRESS): cv.int_,
        cv.Optional(CONF_OFFSET): cv.int_,
        cv.Optional(CONF_BITMASK, default=0xFFFFFFFF): cv.hex_uint32_t,
        cv.Optional(CONF_VALUE_TYPE): cv.enum(SENSOR_VALUE_TYPE),
        cv.Optional(CONF_SCALE_FACTOR, default=1.0): cv.float_,
        cv.Optional(CONF_REGISTER_COUNT, default=1): cv.int_,
        cv.Optional(CONF_SKIP_UPDATES, default=0): cv.int_,
    }
)

#        cv.OnlyWith(CONF_MQTT_ID2, "mqtt"): cv.declare_id(
#            mqtt.MQTTSwitchComponent
#        ),

binary_sensor_entry = binary_sensor.BINARY_SENSOR_SCHEMA.extend(
    {
        cv.Optional(CONF_MODBUS_FUNCTIONCODE): cv.enum(MODBUS_FUNCTION_CODE),
        cv.Optional(CONF_ADDRESS): cv.int_,
        cv.Optional(CONF_OFFSET): cv.int_,
        cv.Optional(CONF_BITMASK, default=0x1): cv.hex_uint32_t,
        cv.Optional(CONF_SKIP_UPDATES, default=0): cv.int_,
        cv.Optional(CONF_CREATE_SWITCH, default=False): cv.boolean,
    }
)

modbus_switch_entry = switch.SWITCH_SCHEMA.extend(
    {
        cv.GenerateID(): cv.declare_id(ModbusSwitch),
        cv.Optional(CONF_MODBUS_FUNCTIONCODE): cv.enum(MODBUS_FUNCTION_CODE),
        cv.Optional(CONF_ADDRESS): cv.int_,
        cv.Optional(CONF_OFFSET, default=0): cv.int_,
        cv.Optional(CONF_BITMASK, default=0x1): cv.hex_uint32_t,
    }
).extend(cv.COMPONENT_SCHEMA)

text_sensor_entry = text_sensor.TEXT_SENSOR_SCHEMA.extend(
    {
        cv.GenerateID(): cv.declare_id(TextSensor),
        cv.Optional(CONF_ON_RAW): automation.validate_automation(
            {
                cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(RawDataCodeTrigger),
            }
        ),
        cv.Optional(CONF_MODBUS_FUNCTIONCODE): cv.enum(MODBUS_FUNCTION_CODE),
        cv.Optional(CONF_ADDRESS): cv.int_,
        cv.Optional(CONF_OFFSET): cv.int_,
        cv.Optional(CONF_REGISTER_COUNT, default=1): cv.int_,
        cv.Optional(CONF_RESPONSE_SIZE, default=0): cv.int_,
        cv.Optional(CONF_HEX_ENCODE, default=0): cv.boolean,
        cv.Optional(CONF_SKIP_UPDATES, default=0): cv.int_,
    }
).extend(cv.COMPONENT_SCHEMA)


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
        for cfg in conf:
            sens = yield sensor.new_sensor(cfg)
            cg.add(
                var.add_sensor(
                    sens,
                    cfg[CONF_MODBUS_FUNCTIONCODE],
                    cfg[CONF_ADDRESS],
                    cfg[CONF_OFFSET],
                    cfg[CONF_BITMASK],
                    cfg[CONF_VALUE_TYPE],
                    cfg[CONF_REGISTER_COUNT],
                    cfg[CONF_SKIP_UPDATES],
                    cfg[CONF_SCALE_FACTOR],
                )
            )
    if config.get("binary_sensors"):
        conf = config["binary_sensors"]
        for cfg in conf:
            sens = yield binary_sensor.new_binary_sensor(cfg)
            cg.add(
                var.add_binarysensor(
                    sens,
                    App,
                    cfg[CONF_MODBUS_FUNCTIONCODE],
                    cfg[CONF_ADDRESS],
                    cfg[CONF_OFFSET],
                    cfg[CONF_BITMASK],
                    cfg[CONF_CREATE_SWITCH],
                    cfg[CONF_SKIP_UPDATES],
                )
            )
        if CONF_MQTT_ID2 in config:
            mqtt_ = cg.new_Pvariable(config[CONF_MQTT_ID2], var)
            yield mqtt.register_mqtt_component(mqtt_, config)

    if config.get("text_sensors"):
        conf = config["text_sensors"]
        for cfg in conf:
            sens = yield new_text_sensor(cfg)
            cg.add(
                var.add_textsensor(
                    sens,
                    cfg[CONF_MODBUS_FUNCTIONCODE],
                    cfg[CONF_ADDRESS],
                    cfg[CONF_OFFSET],
                    cfg[CONF_REGISTER_COUNT],
                    cfg[CONF_RESPONSE_SIZE],
                    cfg[CONF_HEX_ENCODE],
                    cfg[CONF_SKIP_UPDATES],
                )
            )
            if config.get(CONF_ON_RAW):
                cfg_raw = cfg[CONF_ON_RAW]
                for c in cfg_raw:
                    trigger = cg.new_Pvariable(c[CONF_TRIGGER_ID], var, sens)
                    yield automation.build_automation(trigger, [(RawData, "x")], c)
    if config.get("switches"):
        conf = config["switches"]
        for cfg in conf:
            sens = yield new_modbus_switch(cfg)
            cg.add(
                var.add_modbus_switch(
                    sens,
                    cfg[CONF_MODBUS_FUNCTIONCODE],
                    cfg[CONF_ADDRESS],
                    cfg[CONF_OFFSET],
                    cfg[CONF_BITMASK],
                )
            )


@coroutine
def build_modbus_registers(config):
    yield cg.build_registry_list(MODBUS_REGISTRY, config)


@coroutine
def new_text_sensor(config):
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_NAME])
    yield text_sensor.register_text_sensor(var, config)
    yield var


@coroutine
def new_modbus_switch(config):

    var = cg.new_Pvariable(
        config[CONF_ID],
        config[CONF_MODBUS_FUNCTIONCODE],
        config[CONF_ADDRESS],
        config[CONF_OFFSET],
        config[CONF_BITMASK],
    )
    yield cg.register_component(var, config)
    yield switch.register_switch(var, config)
    yield var
