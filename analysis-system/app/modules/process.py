def energy_data(volts: float, amps: float, entity : dict) -> tuple[bool, bool]:

    highLowVoltage = volts > entity['highVoltageValue'] or volts < entity['lowVoltageValue']
    overCurrent = amps > entity['overCurrentValue']
    return highLowVoltage, overCurrent