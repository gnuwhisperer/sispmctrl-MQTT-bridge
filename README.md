sispmctl-MQTT-bridge
=====================

This code implement the function of controlling Gembird silverlit USB switchable outlets through MQTT.

This Fork was done, to have it work better with [Homeassistant](https://www.home-assistant.io/).

The script will need you to install sispmctl

On Ubuntu/RPI use:
sudo apt-get install sispmctl

How to use: 

The command 
```
$ mosquitto_pub -h <host> -t "cmnd/sispmctl/<device_id>/socket/POWER1" -m on
$ mosquitto_pub -h <host> -t "cmnd/sispmctl/<device_id>/socket/POWER1" -m off
```
Will turn on outlet 1 (numbered 1-4) on the gembird device with the serial <device_id>. 

To get the ids run: 
>sispmctl -s  

The script will also write a 

tele/sispmctl/<device_id>/LWT True

when a device is detected or False when disconnected. 

The script will send the changed state of the outlets in POLL_TIME = 5 intervals or after switching.
It will send all states, because it integrated better with Homeassistant.
```
received mqtt message: cmnd/sispmctl/01:00:fd:ef:00/socket/POWER3 message:  ON
SENT MQTT MESSAGE:  tele/sispmctl/01:00:fd:ef:00/STATE/POWER1 ON 
SENT MQTT MESSAGE:  tele/sispmctl/01:00:fd:ef:00/STATE/POWER2 OFF 
SENT MQTT MESSAGE:  tele/sispmctl/01:00:fd:ef:00/STATE/POWER3 ON 
SENT MQTT MESSAGE:  tele/sispmctl/01:00:fd:ef:00/STATE/POWER4 ON 
received mqtt message: cmnd/sispmctl/01:00:fd:ef:00/socket/POWER3 message:  OFF
SENT MQTT MESSAGE:  tele/sispmctl/01:00:fd:ef:00/STATE/POWER1 ON
SENT MQTT MESSAGE:  tele/sispmctl/01:00:fd:ef:00/STATE/POWER2 OFF
SENT MQTT MESSAGE:  tele/sispmctl/01:00:fd:ef:00/STATE/POWER3 OFF
SENT MQTT MESSAGE:  tele/sispmctl/01:00:fd:ef:00/STATE/POWER4 ON
```

Config is expecet to be in /etc/sispmctl.conf or the current workdir.

To have it not neccesscarely run als root, you can add a udev rule with the Vendor and Product ID.
```
$ lsusb |grep socket
Bus 001 Device 010: ID 04b4:fd13 Cypress Semiconductor Corp. Programmable power socket

$ cat /etc/udev/rules.d/sispm.rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="04b4", ATTRS{idProduct}=="fd13", MODE="0777"
( Plug it out and back it, to have the rules reloaded. )
```

My Configuration for Homeassistant looks like this:
```
- platform: mqtt
  name: "Steckleisenschalter 1"
  state_topic: "tele/sispmctl/<device_id>/STATE/POWER1"
  command_topic: "cmnd/sispmctl/<device_id>/socket/POWER1"
  payload_on: "ON"
  payload_off: "OFF"
  state_on: "ON"
  state_off: "OFF"
  optimistic: false
```
