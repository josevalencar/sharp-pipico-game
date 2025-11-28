from machine import ADC
import utime

adc = ADC(26)

MIN_V = 0.4
MAX_V = 2.8

def read_voltage():
    raw = adc.read_u16()
    voltage = raw * (3.3 / 65535.0)
    return voltage

def normalize(voltage):
    if voltage < MIN_V:
        voltage = MIN_V
    if voltage > MAX_V:
        voltage = MAX_V
    return (voltage - MIN_V) / (MAX_V - MIN_V)

def main():
    while True:
        v = read_voltage()
        norm = normalize(v)
        print("{:.3f}".format(norm))
        utime.sleep_ms(30)

try:
    main()
except KeyboardInterrupt:
    pass
