# ksu.py
`ksu.py` is a python command line tool & library for controlling USB-connected KSU-1 power supplies.

## Command Line

### Usage
```console
➜ ./ksu.py   
usage: ksu [-h] -d DEVICE [-v [VOLTAGE]] [-i [CURRENT_LIMIT]] [-o [{on,off}]] [-r [{on,off}]] [-l [{on,off}]] [-s [COUNT]] [-t STATUS_INTERVAL]

options:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        Path to/name of serial device created by the KSU
                        Example: '/dev/ttyACM0' or 'COM14'
  -v [VOLTAGE], --voltage [VOLTAGE]
                        If no argument is supplied, queries the current target voltage.
                        Otherwise, sets the target voltage to the value provided in the argument.
  -i [CURRENT_LIMIT], --current-limit [CURRENT_LIMIT]
                        If no argument is supplied, queries the current current limit.
                        Otherwise, sets the current limit to the value provided in the argument.
  -o [{on,off}], --output [{on,off}]
                        If no argument is supplied, queries the current output state.
                        Otherwise, sets the output state to the value provided in the argument.
  -r [{on,off}], --relay [{on,off}]
                        If no argument is supplied, queries the current relay state.
                        Otherwise, sets the relay state to the value provided in the argument.
  -l [{on,off}], --lock [{on,off}]
                        If no argument is supplied, queries the current lock state.
                        Otherwise, sets the lock state to the value provided in the argument.
  -s [COUNT], --status [COUNT]
                        If no argument is supplied, queries the status of the power supply repeatedly until killed.
                        Otherwise, queries the status of the power supply the number of times specified in the argument.
  -t STATUS_INTERVAL, --status-interval STATUS_INTERVAL
                        Sets the delay between status queries.
                        Default value is 1.0 second.
```
### Examples

#### Set the output voltage to 12.0 V
```console
➜ ./ksu.py -d /dev/ttyACM0 -v 12
12.0
```

#### Query the current limit
```console
➜ ./ksu.py -d /dev/ttyACM0 -i       
1.0
```

#### Set the output voltage to 5.0 V, the current limit to 1.0 A, turn on the output, and turn on the relay
```console
➜ ./ksu.py -d /dev/ttyACM0 -v 5 -i 1 -o on -r on
5.0
1.0
on
on
```

#### Query the status of the power supply once
```console
➜ ./ksu.py -d /dev/ttyACM0 -s 1                 
{"ina228": {"vout": 5.005, "iout": 0.0}, "tmp100": {"temp": 26.4}, "tps55289": {"scp": true, "ocp": true, "ovp": true, "mode": "buck-boost"}}
```

Pretty-print with `jq`:
```json
➜ ./ksu.py -d /dev/ttyACM0 -s 1 | jq
{
  "ina228": {
    "vout": 5.005,
    "iout": 0
  },
  "tmp100": {
    "temp": 26.6
  },
  "tps55289": {
    "scp": true,
    "ocp": true,
    "ovp": true,
    "mode": "buck-boost"
  }
}
```

## Library

`ksu.py` defines a single class called KSU.

### class KSU:

#### Constructor
The constructor of the KSU class takes 1 argument: a string which represents the path to / name of the serial device that is created by the USB-connected power supply.

#### `setVoltage`
Takes one float argument: the target voltage in Volts.

Returns the voltage that was actually set (based on the bounds allowed by the power supply, and whether the lock is active).
#### `getVoltage`
Returns the current target voltage in Volts.
#### `setCurrentLimit`
Takes one float argument: the desired current limit in Amps.

Returns the current limit that was actually set (based on the bounds allowed by the power supply, and whether the lock is active).
#### `getCurrentLimit`
Returns the current current limit in Amps.
#### `setRelay`
Takes one bool argument: the desired state of the relay.

Returns the state of the relay after setting it (which could be different based on whether the lock is active).
#### `getRelay`
Returns the state of the relay.
#### `setOutput`
Takes one bool argument: the desired state of the output.

Returns the state of the output after setting it (which could be different based on whether the lock is active).
#### `getOutput`
Returns the state of the output.
#### `setLock`
Takes one bool argument: the desired state of the lock.

Returns the state of the lock after setting it.
#### `getLock`
Returns the state of the lock.
#### `getStatus`
Queries the current status of the power supply.

Returns a dict that looks like:
```python
{
  "ina228": {
    "vout": 4.119,
    "iout": 0
  },
  "tmp100": {
    "temp": 26.8
  },
  "tps55289": {
    "scp": true,
    "ocp": true,
    "ovp": true,
    "mode": "buck"
  }
}
```

### Example

Set the voltage to 5.0 V, the current limit to 1.0 A, turn on the relay, and turn on the output.

Then, continuously print the real voltage and current being output by the power supply.
```python
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
```