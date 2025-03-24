def energy_data(volts: float, amps: float) -> tuple[bool, bool]:
    VOLTAGE_THRESHOLD_HIGH = 120 * 1.09
    VOLTAGE_THRESHOLD_LOW = 120 * 0.91
    AMP_THRESHOLD = 10

    highLowVoltage = volts > VOLTAGE_THRESHOLD_HIGH or volts < VOLTAGE_THRESHOLD_LOW
    overCurrent = amps > AMP_THRESHOLD
    return highLowVoltage, overCurrent