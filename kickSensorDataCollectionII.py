import sensors
import time
import grovelcd
import csv

"""
Plan:
1. Have a series of kicks planned 
2. After each kick write a line to the csv to indicate that the kick has happened 
Objectives:
1. Read continuously
2. Record sensor values to a csv file
3. If space bar pressed write a line with *Kick Name*
4. When the series of kicks are finished (on last space bar press) stop recording and save csv

kicks1 
- front 
- mid 
- front
- low
- mid
- low
- front
- mid
- front 
- front
- low
- mid 
- low
- mid
- low

kicks2



kicks3



"""


sensor_pins = {"accel": 0, "gyro": 0}
sensors.set_pins(sensor_pins)

# List of series of kicks
kicks1 = []
kicks2 = []
kicks3 = []

csv_name = "continuous_kick_data_test.csv"

try:
    while True:
        # Wait for enter to be pressed to start recording
        action = int(input("Press 1 to start\n Press 2 to EXIT"))
        if action == 2:
            break

        # data = {'ax': [], 'ay': [], 'az': [], 'am': [], 'rx': [], 'ry': [], 'rz': [], 'rm': []}

        headers = ['time','ax', 'ay', 'az', 'am', 'rx', 'ry', 'rz', 'rm']

        with open(csv_name, "a",  encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        # Infinite loop
        print("Press ctrl+c to exit")
        start_time = time.time()
        while True:
            data = []
            curr_time = time.time() - start_time
            data.append(curr_time)
            # * Do kicks *
            # Record sensor data
            ax, ay, az = sensors.accel.get_xyz()
            data.append(ax)
            data.append(ay)
            data.append(az)

            # magnitude of acceleration
            am = sensors.accel.get_magnitude()
            data.append(am)

            # rotation around x,y,z axes
            rx, ry, rz = sensors.gyro.get_xyz()
            data.append(rx)
            data.append(ry)
            data.append(rz)

            # magnitude of rotation
            rm = sensors.gyro.get_magnitude()
            data.append(rm)

            # Save row to csv
            with open(csv_name, "a", encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(data)

            # time.sleep(0.01)



except KeyboardInterrupt:
    print("Program interrupted")