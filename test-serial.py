from serial import Serial
import time
import sched
from tqdm import tqdm

ser = Serial('/dev/ttyUSB0',9600,timeout=3)
ser.flushInput()

while True:
	ser.write("Q");
	line = ser.readline().decode('utf-8')
	if line != "": #i.e. not a timeout
		print(line)
		time.sleep(5)
	
	
	
