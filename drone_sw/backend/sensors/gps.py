import time, serial, pynmea2

ser = None

def init_gps(port="/dev/serial0", baud=9600):
    """Init GPS once on the given serial port."""
    global ser
    ser = serial.Serial(port, baudrate=baud, timeout=0.2)

def read_gps():
    """Return dict with GPS fix info, or None if no new sentence yet."""
    line = ser.readline().decode("ascii", errors="ignore").strip()
    if not line.startswith("$"): return None
    try:
        msg = pynmea2.parse(line)
    except: return None
    t = time.time()
    if msg.sentence_type == "GGA":
        return {"ts": t, "lat": msg.latitude, "lon": msg.longitude,
                "alt": msg.altitude, "sats": msg.num_sats, "fix": msg.gps_qual}
    if msg.sentence_type == "RMC":
        return {"ts": t, "lat": msg.latitude, "lon": msg.longitude,
                "alt": None, "sats": None, "fix": None}
    return None