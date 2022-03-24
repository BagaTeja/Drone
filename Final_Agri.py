from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative


# Set up option parsing to get connection string
import re
import argparse
#import Spray as S
import haversine as hs
from haversine import Unit


parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect', help="Vehicle connection target string. If not specified, SITL automatically started and used.")
parser.add_argument('--point', help="Number of points drone should visit.")
parser.add_argument('--loc', help="Location Hyphen seperated")
args = parser.parse_args()
connection_string = args.connect
Point_String = int(args.point)
Loc_String = args.loc

Lati = []
Longi = []

Loc_String = Loc_String.split("-")

for i in range(Point_String):
    mark = Loc_String[i].split(":")
    Lati.append(mark[0])
    Longi.append(mark[1])


sitl = None


# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


arm_and_takeoff(2)

print("Set default/target airspeed to 1")
vehicle.airspeed = 1
        
        
point = LocationGlobalRelative(float(Lati[0]),float(Longi[0]), 3)
vehicle.simple_goto(point)

l = 0

while(l<int(Point_String)):
    ploc = str(vehicle.location.global_frame)
    print(ploc)
    DPos = re.findall(r"[-+]?\d*\.\d+|\d+", ploc)
    loci1 = (float(DPos[0]), float(DPos[1]))
    loci2 = (float(Lati[l]), float(Longi[l]))
    dist = hs.haversine(loci1, loci2, unit=Unit.METERS)
    print(loci1, loci2, dist)
    if(dist<1):
        if l == 0:
            #S.Spray().Start()
            pass

        l = l + 1

        if(l<int(Point_String)):
            point = LocationGlobalRelative(float(Lati[l]), float(Longi[l]), 3)
            vehicle.simple_goto(point)


print("Spraying Stopped.......")
#S.Spray().Stop()

vehicle.mode = VehicleMode("LAND")

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl:
    sitl.stop()

