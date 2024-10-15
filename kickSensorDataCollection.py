import sensors
import time
import grovelcd
import csv

""" 
- Input number to choose which kick is being executed
- Press a button to start
- Record 5 seconds of both Accelerometer and Gyro Data
- Save to a CSV file with the kick and data
"""

sensor_pins = {"accel": 0, "gyro": 0}
movements = {1: 'Front kick', 2: 'Low roundhouse', 3: 'Mid roundhouse', 4: 'Walking', 5: 'Stationary', 6: 'Lifting knee'
             }
headers = ['ax', 'ay', 'az', 'am', 'rx', 'ry', 'rz', 'rm']
sensors.set_pins(sensor_pins)
try:
    while True:
        data = {'ax': [], 'ay': [], 'az': [], 'am': [], 'rx': [], 'ry': [], 'rz': [], 'rm': []}
        movement = int(input("Enter number for kick\n 1: Front kick\n 2: Low roundhouse\n 3: Mid roundhouse\n"
                             " 4: Walking\n 5: Stationary\n 6: Lifting knee\n 7: EXIT\n"))
        if movement == 7:
            break

        start = input("Press any key to start\n")
        timeout = time.time() + 5
        while True:

            # acceleration in x,y,z axes
            ax, ay, az = sensors.accel.get_xyz()
            data['ax'].append(ax)
            data['ay'].append(ay)
            data['az'].append(az)

            # magnitude of acceleration
            am = sensors.accel.get_magnitude()
            data['am'].append(am)

            # rotation around x,y,z axes
            rx, ry, rz = sensors.gyro.get_xyz()
            data['rx'].append(rx)
            data['ry'].append(ry)
            data['rz'].append(rz)

            # magnitude of rotation
            rm = sensors.gyro.get_magnitude()
            data['rm'].append(rm)

            # data to put in csv file
            print(f"data: {ax, ay, az, am, rx, ry, rz, rm}")

            if time.time() > timeout:
                break
            time.sleep(0.01)

        with open('kick_data.csv', 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["*",movements[movement]])
            writer.writerow(headers)
            rows = zip(data['ax'], data['ay'], data['az'], data['am'], data['rx'], data['ry'], data['rz'])
            for row in rows:
                writer.writerow(row)
except KeyboardInterrupt:
    pass


