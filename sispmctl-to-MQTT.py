#!/usr/bin/python3.7 -u

import configparser
import json
import os
import sys
import _thread
import time

import paho.mqtt.client as mqtt

# The MQTT format for setting outlets are cmnd/<prefix>/<device_id>/POWER<outlet>
POLL_TIME = 5  # For checking state changes on outlets.
QOS = 1

def socket_off(device, socket):
	global states
	#print("turn socket", socket, "off")
	os.system("/usr/bin/sispmctl -q -D %s -f %i" % (device, socket))
	states[device]=socket_get_state(device)
	publish_state(device)

def socket_on(device, socket):
	global states
	#print("turn socket", socket, "on")
	os.system("/usr/bin/sispmctl -q -D %s -o %i" % (device, socket))
	states[device]=socket_get_state(device)
	publish_state(device)
	
def socket_get_state(device):
    #print("get state of all socket",device)
    result = {}
    for line in os.popen("/usr/bin/sispmctl -q -D %s -n -g all" % device).readlines():
        if line[0] == "0":
            result["POWER"+str(len(result)+1)]="OFF"
        elif line[0] == "1":
            result["POWER"+str(len(result)+1)]="ON"
    return result

def devices_get_serialnumbers():
	#generate device list: {'01:02:03:04:05': 0}
	discovered_devices = {}
	discovered_states = {}
	for line in os.popen("/usr/bin/sispmctl -s ").readlines():
		if line.find("serial number") != -1:
			serial = line.strip("\n").split("    ")[1]
			discovered_devices[serial] = len(discovered_devices)
			discovered_states[serial] = socket_get_state(serial)
	return (discovered_devices,discovered_states)

def publish_state(device):
	global states
	topic = "tele/"+ prefix +"/"+ device +"/STATE"
	for socket, state in states[device].items():
		message = (topic+"/"+socket)
		client.publish(message, state, QOS)
		#print("SENT MQTT MESSAGE: ", message, state )

def on_connect(mqtt, rc, a):
    mqtt.subscribe("cmnd/"+prefix+"/#", 0)

def on_message(a, mqtt, msg):
	global devices
	# try:
	if True:
		print(f"received mqtt message: {msg.topic} message:  {msg.payload.decode()}")
		#cmnd/<prefix>/<serial>/POWER<socket+1> = <ON|OFF|0|1>
		topics = msg.topic.split("/")
		socket = int(topics[-1][-1])
		#print("socket: "+str(socket))
		value = msg.payload.decode()
		device = topics[-3]
		if not device in devices:
			return
		if value.upper() == "ON" or value == "1":
			# Turn on
			socket_on(device, socket)
		if value.upper() == "OFF" or value == "1":
			# Turn off
			socket_off(device, socket)
    # except:
    #   print "Error occured while processing command"
	return


def ControlLoop():
    # schedule the client loop to handle messages, etc.
    print("Starting MQTT listener")
    while True:
        client.loop()
        time.sleep(0.1)


# Get all devices.
if __name__ == '__main__':
	# Where am I
	path = os.path.abspath(os.path.dirname(sys.argv[0]))
	# Load config file...
	try:
		ConfigFile = sys.argv[1]
	except:
		try:
			ConfigFile = "/etc/sispmctl.conf"
		except:
			ConfigFile = path + "/sispmctl.conf"
	try:
		f = open(ConfigFile, "r")
		f.close()
	except:
		try:
			ConfigFile = path + "/sispmctl.conf"
			f = open(ConfigFile, "r")
			f.close()
		except:
			print("Please provide a valid config file! By argument or as default sispmctl.conf file.")
			exit(1)
	config = configparser.RawConfigParser(allow_no_value=True)
	config.read(ConfigFile)

	# Load basic config.
	ip = config.get("MQTTServer", "Address")
	port = config.get("MQTTServer", "Port")
	user = config.get("MQTTServer", "User")
	password = config.get("MQTTServer", "Password")
	prefix = config.get("MQTTServer", "Prefix")
	instance = config.get("MQTTServer", "Instance")
	client = mqtt.Client("sispmctl-to-MQTT-client")

	if user != None:
    			client.username_pw_set(user, password)

	client.will_set(topic="tele/" + prefix+"/"+instance+"/LWT",
	                payload="Offline", qos=1, retain=True)

	# Connect and notify others of our presence.
	client.connect(ip)
	client.publish("tele/"+prefix+"/"+instance+"/LWT", "Online", 1, retain=True)
	client.on_connect = on_connect
	client.on_message = on_message
	client.subscribe("cmnd/"+prefix+"/#", 0)

	# Init
	devices = {}
	states = {}

	# Start tread...
	_thread.start_new_thread(ControlLoop, ())

	while True:
		# Check if anything changed
		# Send update if it did.
		# Detect devices
		old_devices = devices
		old_states = states
		devices,states = devices_get_serialnumbers()
		# Look for disconnections..
		for device in old_devices:
			if not device in devices:
				#print("device disconnected: "+device)
				topic = "tele/"+prefix +"/"+ device + "/LWT"
				client.publish(topic , False, QOS)

		# Look for devices being connected..
		for device in devices:
			if not device in old_devices:
				#print("device connected: "+device)
				topic = "tele/"+prefix +"/"+ device + "/LWT"
				client.publish(topic , True, QOS)
	            
		# Detect states changes on outlets
		#print(devices)states[device] != old_states[device]:
		for device in devices:
			if not device in old_states:
				#no old state, publish state
				publish_state(device)
			else:
				# old state exists, only publish if changed
				# compare stateclient.publish(topic, str(states[device]), QOS)
				#print("newstate: "+str(states[device])+" oldstate: "+str(old_states[device]))
				if states[device] != old_states[device]:
					publish_state(device)
		time.sleep(POLL_TIME)    
	    
	client.disconnect() 
