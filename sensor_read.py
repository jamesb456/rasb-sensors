from serial import Serial
import time
import psycopg2
import json
conn = None
sensor_dict = { 1 : 'H', 2 : 'T', 3 : 'S' , 4 : 'L' }
ser = Serial('/dev/ttyUSB0',9600,timeout=3)
did = 3


 
#getting a list of sensors and sending this to the server    
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
    
    
#from the sever, getting back the device id, the sensor ids then sending the sensor ids to the arduino to be stored
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
            
        
#sending the sensor data to the server
def send_sensor_data(filename):
    with open(filename,'w') as json_file:
        json_dict = {}
        json_dict['device-id'] = did
        json_dict['sensor-values'] = {}
        ser.write("Q".encode())
        
        line = ser.readline().decode('utf-8')
        if line != "":
            response = line[:-2]
            response = response.split(" ")
            print(f"Response = {response}")
            json_dict['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            for i in range(0,len(response) - 1,2):
                json_dict['sensor-values'][response[i]] = int(float(response[i+1]))
            json.dump(json_dict,json_file)
            
            
                
        

# read_setup_response('response.txt')


while True:
    send_sensor_data('data.txt')
    time.sleep(5)
        
    
    
    
