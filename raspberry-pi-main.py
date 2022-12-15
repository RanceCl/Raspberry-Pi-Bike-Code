#!/usr/bin/env python3

import math
import bluetooth
import os
import serial
import time

#Setting the variables for the serial input from the ESP
#ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
#ser.reset_input_buffer()

#This section of code is to establish the bluetooth connection to the esp32
#The pi is the client and the esp32 is the server
motorControlMAC = "34:86:5D:FD:E7:CE"
motor_control_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
motor_control_sock.connect((motorControlMAC, 1))
print("Waiting for connection on RFCOMM channel", 1)

#This section of code is to establish the bluetooth connection to the phone
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", 2))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "849ebadc-9bae-4d4f-8375-458b079c1e92"

bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                            service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE]
                            )
print("Waiting for connection on RFCOMM channel", port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from", client_info)

GearControl = "gs0"
#GearControl = 0
curr_voltage = 0
speed = 0
gear = 1;

try:
    while True:
        #Read in the acceleration data
        esp32data = motor_control_sock.recv(1024)
        motordata = esp32data.decode('utf-8')

        print(motordata)
        #check what the button pressed was (low/medium/high speed)
        for i in range(len(motordata)-5):
            if(motordata[i] == 's' and motordata[i+1] == '+'):
                speedString = motordata[i+2] + motordata[i+3] + motordata[i+4] + motordata[i+5]
                speed = float(speedString)
                sOutString = motordata[i] + motordata[i+1] + motordata[i+2] + motordata[i+3] + motordata[i+4] + motordata[i+5]
                client_sock.send(sOutString)
            elif(motordata[i] == 'd' and motordata[i+1] == '+'):
                distanceString = motordata[i+2] + motordata[i+3] + motordata[i+4] + motordata[i+5]
                distance = float(distanceString)
                #print("distance:")
                #print(distance)
                dOutString = motordata[i] + motordata[i+1] + motordata[i+2] + motordata[i+3] + motordata[i+4] + motordata[i+5]
                client_sock.send(dOutString)
            elif(motordata[i] == 'e' and motordata[i+1] == '+'):
                voltageString = motordata[i+2] + motordata[i+3] + motordata[i+4] + motordata[i+5]
                curr_voltage = float(voltageString)
                #print("Curr voltage:")
                #print(curr_voltage)
                vOutString = motordata[i] + motordata[i+1] + motordata[i+2] + motordata[i+3] + motordata[i+4] + motordata[i+5]
                client_sock.send(vOutString)
            elif(motordata[i] == 'r' and motordata[i+1] == '+'):
                cadenceString = motordata[i+2] + motordata[i+3] + motordata[i+4] + motordata[i+5]
                cadence = float(cadenceString)     
        motordata = ''
        #Read in the current gear position
        try:
            appdata = client_sock.recv(1024,0x40)
            appstring = appdata.decode('utf-8')
            print(appstring)
        except:
            continue;
        #parse the data based on the first letter sent from the app
        #If the first letter of the app data is G, then it is an indicator of the gear shift
        if(appstring[0] == 'g'):
            GearControl = appstring
            print(appstring)
        #If the appdata is non, then the assist level is turned to none
        if(appstring == 'non'):
            assist = 'none'
        #If the appdata is low, then the assist level is turned to low
        if(appstring == 'low'):
            assist = 'low'
        #If the appdata is med, then the assist level is turned to medium
        if(appstring == 'med'):
            assist = 'medium'
        #If the appdata is hig, then the assist level is turned to high
        if(appstring == 'hig'):
            assist = 'high'
        #parse motor data
        max_voltage = 29.4
        
        #automatic gear shift implementation
        if(GearControl == "gs1"):
            if(cadence > 80):
                #move up a gear (CCW)
                if(gear < 6):
                    print("Switching Up")
                    #send serial signal to esp32
                    #ser.write(b"Up\n")
                    #gear = gear+1
            elif(cadence < 60):
                #move down a gear (CW)
                if(gear > 1):
                    print("Switching Down")
                    #send serial signal to esp32
                    #ser.write(b"Down\n")
                    #gear = gear-1
        #main motor assist control
        if(assist == 'none'):
            motor_control_sock.send('v+00.0')
            motor_control_sock.send('c+00.0')
        if(assist == 'low'):
            speed_target = 8
            duty_cycle = min([99.9, 100 * 0.3*max_voltage/curr_voltage]) #30 percent speed target, compensated
            if(speed < speed_target):
                target_current = "10.0" #low torque target
            else:
                target_current = "02.0" #virtual idle
            Voutput = 'v+' + str(round(duty_cycle,1))
            motor_control_sock.send(Voutput)
            Coutput = 'c+' + target_current
            motor_control_sock.send(Coutput)
        if(assist == 'medium'):
            speed_target = 12
            duty_cycle = min([99.9, 100 * 0.6*max_voltage/curr_voltage]) #60 percent speed target, compensated
            if(speed < speed_target):
                target_current = "14.0" #low torque target
            else:
                target_current = "03.0" #virtual idle
            Voutput = 'v+' + str(round(duty_cycle,1))
            motor_control_sock.send(Voutput)
            Coutput = 'c+' + target_current
            motor_control_sock.send(Coutput)
        if(assist == 'high'):
            speed_target = 18
            duty_cycle = min([99.9, 100 * 0.9*max_voltage/curr_voltage]) #90 percent speed target, compensated
            if(speed < speed_target):
                target_current = "18.0" #low torque target
            else:
                target_current = "04.0" #virtual idle
            Voutput = 'v+' + str(round(duty_cycle,1))
            motor_control_sock.send(Voutput)
            Coutput = 'c+' + target_current
            motor_control_sock.send(Coutput)
except OSError:
    print("Error")
    print(os.ttyname(1))
    bluetooth.stop_advertising(server_sock)
    client_sock.close()
    server_sock.close()
    print("All done.")
