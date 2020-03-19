import json
import psycopg2



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
	return insert_db(f"INSERT INTO device (latitude,longitude) VALUES({lati},{longi}) RETURNING did")[0]

def insert_sensor(did,sensor_type):
	return insert_db(f"INSERT INTO sensors (did,stype) VALUES({did},'{sensor_type}') RETURNING sid")[0]
	
def get_sensor_name(sid):
	stype = insert_db(f"SELECT stype FROM sensors WHERE sid = {sid} ")[0]
	return get_table_name(stype)

def insert_sensor_value(timestamp, sensor_value, sensor_id):
	
	table_name = get_sensor_name(sensor_id)
	if(table_name != ""):
		insert_db(f"INSERT INTO {table_name} (dt,sid,sensor_value) VALUES('{timestamp}',{sensor_id},{sensor_value}) RETURNING dt")


def read_setup():
	response = {}
	with open('json.txt') as json_file:
		data = json.load(json_file)
		did = insert_device(data['lat'],data['long'])
		
		response['device-id'] = did
		response['sensor-dict'] = {}
		for sensor in data['sensors']:
			sid = insert_sensor(did,sensor)
			response['sensor-dict'][sensor] = sid
	
		
	with open('response.txt','w') as resp_file:
		json.dump(response,resp_file)
		
def read_sensor_data():
	with open('data.txt') as data_file:
		data = json.load(data_file)
		did = data['device-id']
		for (sid,value) in data['sensor-values'].items():
			insert_sensor_value(data['timestamp'],value,sid)
			
		
		

		
read_sensor_data()
