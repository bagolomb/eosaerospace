import time
from adafruit_extended_bus import ExtendedI2C as I2C
from micropython_ms5611.ms5611 import MS5611

i2c = baro = None
SLP0 = 101325.0  # Pa (sea-level pressure)

def init_baro(bus=1, addr=0x77):
    """Init MS5611 once on the given I2C bus and address (0x76 or 0x77)."""
    global i2c, baro
    i2c = I2C(bus)
    baro = MS5611(i2c, address=addr)

def read_baro():
    P = float(baro.pressure)      # Pa
    T = float(baro.temperature)   # °C
    alt = 44330.0 * (1.0 - (P/SLP0) ** 0.1903)
    return {"ts": time.time(), "P": P, "T": T, "alt": alt}