#!/usr/bin/env python3
"""PyBluez simple example rfcomm-server.py
Simple demonstration of a server application that uses RFCOMM sockets.
Author: Albert Huang <albert@csail.mit.edu>
$Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $
"""

import math
import bluetooth


# This section of code is to establish the bluetooth connection
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "849ebadc-9bae-4d4f-8375-458b079c1e92"

bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                            service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE],
                            # protocols=[bluetooth.OBEX_UUID]
                            )

print("Waiting for connection on RFCOMM channel", port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from", client_info)

try:
    while True:
        data = client_sock.recv(1024)
        if not data:
            break
        print("Received", data)
except OSError:
    pass

print("Disconnected.")

client_sock.close()
server_sock.close()
print("All done.")



# This part of the code is to test out the sending of data from the raspberry pi

GearShift = 0 
radius = 12
IdeaMovementRatio = 1
        
# Read in the data
#PIN
RPM = 30

#PIN
VoltLevel = 30

#PIN
VoltMax = 100

#PIN
Acceleration = 20

#PIN
PedalSensor = 40
        
#Read in the commands from the bluetooth
PedalAssist = False
GearAssist= True
        
#Convert RPM to miles per hour
#velocity (miles/hr) = RPM (rotations/min) * 2 * pi * radius (in) * 60 (min/hr) * 1/63360 (miles/in)
Velocity = RPM * 2 * radius * 120/63360

#Find current percent of the battery remaining
VoltPercent = (VoltLevel/VoltMax) * 100

#Find the gearshift based on the pressure on the pedals vs acceleration
if(GearAssist):
    #System.out.println((PedalSensor/Acceleration))
    #Lower the gear shift if the current ratio is too high
    while (Acceleration/PedalSensor) > IdeaMovementRatio:
        GearShift -=1
        Acceleration -=1

        #Break out if the gear shift is already at 0
        if GearShift <= 0:
            break

    #Raise the gear shift if the current ratio is too low
    while (Acceleration/PedalSensor) < IdeaMovementRatio:
        GearShift +=1
        Acceleration +=1

        #Break out if the gear shift is already at the max value
        if GearShift >= 15:
            break

#Send values back to the app
print("Speed: ", Velocity)
print("Battery: ", VoltPercent)
print("Pedal assist: ", PedalAssist)
print("Gear shift: ", GearShift)