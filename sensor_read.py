from serial import Serial
import time
import sched
from tqdm import tqdm
import psycopg2
import json
conn = None
sensor_dict = { 1 : 'H', 2 : 'T', 3 : 'S' , 4 : 'L' }
ser = Serial('/dev/ttyUSB0',9600,timeout=3)
did = 3


def get_table_name(sensor_type):
	table_name = None
	if(sensor_type == 'H'):
		table_name = "Humidity"
	elif(sensor_type == 'T'):
		table_name = "Temperature"
	elif(sensor_type == 'S'):
		table_name = "Soil"
	elif(sensor_type == 'L'):
		table_name = "Light"
	return table_name

def insert_db(sql):
	retval = None
	try:
		conn = psycopg2.connect(host="localhost",database="sensordb",user="designer",password="iot")
		cur = conn.cursor()
		cur.execute(sql)
	
		retval = cur.fetchone()
	
		conn.commit()
		cur.close()
		
	except(Exception,psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if conn is not None:
			conn.close()
		return retval


def insert_device(lati,longi):
	return insert_db(f"INSERT INTO device (latitude,longitude) VALUES({lati},{longi}) RETURNING did")

def insert_sensor(did,sensor_type):
	return insert_db(f"INSERT INTO sensors (did,stype) VALUES({did},'{sensor_type}') RETURNING sid")

def insert_sensor_value(timestamp, sensor_value, sensor_id):
	sensor_type = sensor_dict[sensor_id]
	table_name = get_table_name(sensor_type)
	if(table_name != ""):
		insert_db(f"INSERT INTO {table_name} (dt,sid,sensor_value) VALUES('{timestamp}',{sensor_id},{sensor_value}) RETURNING dt")
		

def setup():
	did = insert_device(0,0)
	ser.flushInput()
	ser.write("Q".encode());
	line = ""
	while line == "":
		line = ser.readline().decode('utf-8')
		print(f"Line = {line}")
		ser.write("Q".encode());
	response = line[:-2]
	response = response.split("	")
	print(f"Response = {response}")
		
	sid = None
	for resp in response[::2]:
		sid = insert_sensor(did,resp)
		sensor_dict[sid] = resp
		
	print(str(sensor_dict))
	
	
def web_setup(lat,lon):
	ser.flushInput()
	ser.write("L".encode());
	line = ""
	while line == "":
		line = ser.readline().decode('utf-8')
		print(f"Line = {line}")
		ser.write("L".encode());
	response = line
	response = response.split(" ")
	
	json_dict = {}
	json_dict['sensors'] = []
	for resp in response:
		json_dict['sensors'].append(resp)
	json_dict['lat'] = lat
	json_dict['long'] = lon
	
	print(json_dict['sensors'])
	with open('json.txt','w') as outfile:
		json.dump(json_dict,outfile)
	print("done setup")
	
def read_setup_response(filename):
	with open(filename) as response:
		json_dict = json.load(response)
		did = json_dict['device-id']
		line = ser.readline().decode('utf-8')
		while not line.startswith("Done setup"):
			print(f"The line is '{line}'")
			line = ser.readline().decode('utf-8')
			
		ser.write("R\n".encode())
		
		print(json_dict['sensor-dict'])
		for (t,sid) in json_dict['sensor-dict'].items():
			ser.write(f"{sid}\n".encode())
		print("Arduino setup done")
			
		
			
def send_sensor_data(filename):
	with open(filename,'w') as json_file:
		json_dict = {}
		json_dict['device-id'] = did
		json_dict['sensor-values'] = {}
		ser.write("Q".encode())
		
		line = ser.readline().decode('utf-8')
		if line != "":
			response = line[:-2]
			response = response.split("	")
			print(f"Response = {response}")
			json_dict['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
			for i in range(0,len(response) - 1,2):
				json_dict['sensor-values'][response[i]] = int(float(response[i+1]))
			json.dump(json_dict,json_file)
			
			
				
		

# read_setup_response('response.txt')


while True:
	send_sensor_data('data.txt')
	time.sleep(5)
		
	
	
	
