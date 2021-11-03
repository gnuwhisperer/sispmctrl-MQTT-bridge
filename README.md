sispmctl-MQTT-bridge
=====================

This code implement the function of controlling Gembird silverlit USB switchable outlets through MQTT


The script will need you to install sispmctl

On Ubuntu/RPI use:
sudo apt-get install sispmctl

How to use: 

The command 

>mosquitto_pub -h brokerIP -t "cmnd/sispmctl/<device_id>/POWER<outlet>" -m On

Will turn on outlet <outlet> (numbered 1-4) on the gembird device with the serial <device_id>. 

To get the ids run: 
>sispmctl -s  

The script will also write a 

tele/sispmctl/01:1c:aa:b5:41/LWT True

when a device is detected or False when disconnected. 

The script will send the changed state of the outlets in POLL_TIME = 5 intervals or after switching:

tele/sispmctl/01:1c:aa:b5:41/STATE = {"POWER1":"OFF", "POWER2":"OFF", "POWER3":"OFF", "POWER4":"OFF"}

Config is expecet to be in /etc/sispmctl.conf or the current workdir.

To have it not neccesscarely run als root, you can add a udev rule with the Vendor and Product ID.

$ lsusb |grep socket
Bus 001 Device 010: ID 04b4:fd13 Cypress Semiconductor Corp. Programmable power socket

$ cat /etc/udev/rules.d/sispm.rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="04b4", ATTRS{idProduct}=="fd13", MODE="0777"
