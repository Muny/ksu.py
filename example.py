import ksu

import time

ksu = ksu.KSU('/dev/ttyACM0')

ksu.setVoltage(5)
ksu.setCurrentLimit(1)
ksu.setRelay(True)
ksu.setOutput(True)

while True:
    status = ksu.getStatus()

    print(f"V: {status['ina228']['vout']}, I: {status['ina228']['iout']}")
    time.sleep(1)