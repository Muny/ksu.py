#!/usr/bin/env python3
import serial

class KSU:
    """
    """
    def __init__(self, device: str):
        """
        """
        self.ser = serial.Serial(device, 115200, timeout=0.5)

        self.__write__('id')
        self.__read__()
        id_line = self.__read__().strip()
        id_parts = id_line.split(',')

        if len(id_line) < 1 or len(id_parts) != 4:
            print(id_line)
            raise Exception('Could not identify device, check to make sure the specified device is correct')

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()

    def __write__(self, line: str = None):
        if line is not None:
            self.ser.write(line.encode('ascii'))
        self.ser.write(b'\n')

    def __read__(self) -> str:
        return self.ser.readline().decode('ascii')
    
    def __rlast__(self) -> str:
        self.__read__()
        return self.__read__().split(',')[-1].strip()

    def setVoltage(self, voltage_V: float) -> float:
        self.__write__(f'vset,{voltage_V}')
        return float(self.__rlast__())
    
    def getVoltage(self) -> float:
        self.__write__('vset')
        return float(self.__rlast__())

    def setCurrentLimit(self, currentLimit_A: float) -> float:
        self.__write__(f'iset,{currentLimit_A}')
        return float(self.__rlast__())
    
    def getCurrentLimit(self) -> float:
        self.__write__('iset')
        return float(self.__rlast__())

    def setRelay(self, on: bool) -> bool:
        self.__write__(f'relay,{"on" if on else "off"}')
        return True if self.__rlast__() == 'on' else False
    
    def getRelay(self) -> bool:
        self.__write__('relay')
        return True if self.__rlast__() == 'on' else False

    def setOutput(self, on: bool) -> bool:
        self.__write__(f'output,{"on" if on else "off"}')
        return True if self.__rlast__() == 'on' else False
    
    def getOutput(self) -> bool:
        self.__write__('output')
        return True if self.__rlast__() == 'on' else False

    def setLock(self, on: bool) -> bool:
        self.__write__(f'lock,{"on" if on else "off"}')
        return True if self.__rlast__() == 'on' else False
    
    def getLock(self) -> bool:
        self.__write__('lock')
        return True if self.__rlast__() == 'on' else False
    
    def getStatus(self):
        self.__write__('status')
        self.__read__()

        status = {}

        end = False
        while not end:
            line = self.__read__().strip()

            parts = line.split(',')

            if len(parts) == 2 and parts[1] == 'end':
                end = True
            elif len(parts) == 4:
                part = parts[1]
                measurement = parts[2]
                value = parts[3]

                if part not in status:
                    status[part] = {}

                if measurement in ['vout', 'iout', 'temp']:
                    value = float(value)
                elif measurement in ['scp', 'ocp', 'ovp']:
                    value = bool(value)

                status[part][measurement] = value

        return status


if __name__ == '__main__':
    # import these here so they're not dependencies unless
    # you're running this tool in the command line
    import argparse
    import math
    import json
    import time
    import sys

    parser = argparse.ArgumentParser(prog='ksu', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-d', '--device', help='Path to/name of serial device created by the KSU\nExample: \'/dev/ttyACM0\' or \'COM14\'', required=True)
    parser.add_argument('-v', '--voltage', help='If no argument is supplied, queries the current target voltage.\nOtherwise, sets the target voltage to the value provided in the argument.', nargs='?', default=float('nan'), type=float)
    parser.add_argument('-i', '--current-limit', help='If no argument is supplied, queries the current current limit.\nOtherwise, sets the current limit to the value provided in the argument.', nargs='?', default=float('nan'), type=float)
    parser.add_argument('-o', '--output', help='If no argument is supplied, queries the current output state.\nOtherwise, sets the output state to the value provided in the argument.', choices=['on', 'off'], nargs='?', default='', type=str)
    parser.add_argument('-r', '--relay', help='If no argument is supplied, queries the current relay state.\nOtherwise, sets the relay state to the value provided in the argument.', choices=['on', 'off'], nargs='?', default='', type=str)
    parser.add_argument('-l', '--lock', help='If no argument is supplied, queries the current lock state.\nOtherwise, sets the lock state to the value provided in the argument.', choices=['on', 'off'], nargs='?', default='', type=str)
    parser.add_argument('-s', '--status', help='If no argument is supplied, queries the status of the power supply repeatedly until killed.\nOtherwise, queries the status of the power supply the number of times specified in the argument.', metavar='COUNT', nargs='?', default=float('nan'), type=int)
    parser.add_argument('-t', '--status-interval', help='Sets the delay between status queries.\nDefault value is 1.0 second.', default=1.0, type=float)

    args = parser.parse_args()

    if len(sys.argv) < 4:
        # the device was specified, but no other arguments were given
        parser.print_help()
        exit()

    ksu = KSU(args.device)

    if args.voltage == None:
        print(ksu.getVoltage())
    elif not math.isnan(args.voltage):
        print(ksu.setVoltage(args.voltage))

    if args.current_limit == None:
        print(ksu.getCurrentLimit())
    elif not math.isnan(args.current_limit):
        print(ksu.setCurrentLimit(args.current_limit))

    if args.output == None:
        print('on' if ksu.getOutput() else 'off')
    elif args.output != '':
        print('on' if ksu.setOutput(True if args.output == 'on' else False) else 'off')

    if args.relay == None:
        print('on' if ksu.getRelay() else 'off')
    elif args.relay != '':
        print('on' if ksu.setRelay(True if args.relay == 'on' else False) else 'off')

    if args.lock == None:
        print('on' if ksu.getLock() else 'off')
    elif args.lock != '':
        print('on' if ksu.setLock(True if args.lock == 'on' else False) else 'off')

    if args.status == None or not math.isnan(args.status):
        i = 0
        while args.status == None or i < args.status:
            if i != 0:
                time.sleep(args.status_interval)

            print(json.dumps(ksu.getStatus()))

            i += 1