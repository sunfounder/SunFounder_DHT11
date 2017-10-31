'''
**********************************************************************
* Filename    : dht11.py
* Description : test for SunFoudner DHT11 humiture & temperature module
* Author      : Dream
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Dream    2016-09-30    New release
**********************************************************************
'''
import time
import RPi.GPIO as GPIO

class DHT11(object):
    MAX_UNCHANGE_COUNT = 100

    STATE_INIT_PULL_DOWN = 1
    STATE_INIT_PULL_UP = 2
    STATE_DATA_FIRST_PULL_DOWN = 3
    STATE_DATA_PULL_UP = 4
    STATE_DATA_PULL_DOWN = 5

    def __init__(self, channel):
        self.channel = channel
        GPIO.setmode(GPIO.BCM)

    def read_dht11(self):
        GPIO.setup(self.channel, GPIO.OUT)
        GPIO.output(self.channel, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(self.channel, GPIO.LOW)
        time.sleep(0.02)
        GPIO.setup(self.channel, GPIO.IN, GPIO.PUD_UP)

        unchanged_count = 0
        last = -1
        data = []
        while True:
            current = GPIO.input(self.channel)
            data.append(current)
            if last != current:
                unchanged_count = 0
                last = current
            else:
                unchanged_count += 1
                if unchanged_count > self.MAX_UNCHANGE_COUNT:
                    break

        state = self.STATE_INIT_PULL_DOWN

        lengths = []
        current_length = 0

        for current in data:
            current_length += 1

            if state == self.STATE_INIT_PULL_DOWN:
                if current == 0:
                    state = self.STATE_INIT_PULL_UP
                else:
                    continue
            if state == self.STATE_INIT_PULL_UP:
                if current == 1:
                    state = self.STATE_DATA_FIRST_PULL_DOWN
                else:
                    continue
            if state == self.STATE_DATA_FIRST_PULL_DOWN:
                if current == 0:
                    state = self.STATE_DATA_PULL_UP
                else:
                    continue
            if state == self.STATE_DATA_PULL_UP:
                if current == 1:
                    current_length = 0
                    state = self.STATE_DATA_PULL_DOWN
                else:
                    continue
            if state == self.STATE_DATA_PULL_DOWN:
                if current == 0:
                    lengths.append(current_length)
                    state = self.STATE_DATA_PULL_UP
                else:
                    continue
        if len(lengths) != 40:
            return False

        shortest_pull_up = min(lengths)
        longest_pull_up = max(lengths)
        halfway = (longest_pull_up + shortest_pull_up) / 2
        bits = []
        the_bytes = []
        byte = 0

        for length in lengths:
            bit = 0
            if length > halfway:
                bit = 1
            bits.append(bit)
        #print "bits: %s, length: %d" % (bits, len(bits))
        for i in range(0, len(bits)):
            byte = byte << 1
            if (bits[i]):
                byte = byte | 1
            else:
                byte = byte | 0
            if ((i + 1) % 8 == 0):
                the_bytes.append(byte)
                byte = 0
        #print the_bytes
        checksum = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
        if the_bytes[4] != checksum:
            return False

        return the_bytes[0], the_bytes[2]

    def read(self, max_times=30):
        for i in range(max_times):
            result = self.read_dht11()
            if result:
                return result
        return False

def main():
    dht = DHT11(17)
    print("Raspberry Pi wiringPi DHT11 Temperature test program\n")
    while True:
        result = dht.read()
        if result:
            humidity, temperature = result
            print("humidity: %s %%,  Temperature: %s C`" % (humidity, temperature))
        else:
        	print("Data Error")
        time.sleep(0.1)

def destroy():
    GPIO.cleanup()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy() 