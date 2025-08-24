import time, math
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_lsm303_accel, adafruit_lsm303dlh_mag

i2c = acc = mag = None

def init_accelmag():
    """Init accel+mag once on the given I2C bus (default /dev/i2c-1)."""
    global i2c, acc, mag
    i2c = I2C(2)
    acc = adafruit_lsm303_accel.LSM303_Accel(i2c)     # 0x19
    mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)   # 0x1E

def read_accelmag():
    ax, ay, az = acc.acceleration   # m/s^2
    mx, my, mz = mag.magnetic       # µT
    return {"ts": time.time(), "accel": (ax, ay, az), "mag": (mx, my, mz)}

def heading(accel, magv):
    ax, ay, az = accel; mx, my, mz = magv
    roll  = math.atan2(ay, az)
    pitch = math.atan2(-ax, (ay*ay+az*az) ** 0.5)
    mx_c = mx*math.cos(pitch) + mz*math.sin(pitch)
    my_c = mx*math.sin(roll)*math.sin(pitch) + my*math.cos(roll) - mz*math.sin(roll)*math.cos(pitch)
    h = math.degrees(math.atan2(-my_c, mx_c))
    return h if h >= 0 else h + 360

if __name__ == "__main__":
    init_accelmag()
    while True:
        print(read_accelmag())