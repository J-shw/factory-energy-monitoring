def energy_data(volts: float, amps: float, limit) -> tuple[bool, bool]:

    highLowVoltage = volts > limit.highVoltageValue or volts < limit.lowVoltageValue
    overCurrent = amps > limit.overCurrentValue
    return highLowVoltage, overCurrent