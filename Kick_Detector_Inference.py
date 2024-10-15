import sensors
import time
import pandas as pd
import numpy as np
import tflite_runtime.interpreter as tflite


sensor_pins = {"accel": 0, "gyro": 0}
sensors.set_pins(sensor_pins)


def z_normalisation(column):
    return (column - column.mean()) / column.std()


try:
    while True:
        data = {'ax': [], 'ay': [], 'az': [], 'am': [], 'rx': [], 'ry': [], 'rz': [], 'rm': []}
        i = 0
        TFLITE_FILE_PATH = '/model.tflite'

        interpreter = tflite.Interpreter(TFLITE_FILE_PATH)
        interpreter.allocate_tensors()

        # Get input and output tensors.
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Test the model on random input data.
        input_shape = input_details[0]['shape']
        while True:
            i+=1
            # acceleration in x,y,z axes
            ax, ay, az = sensors.accel.get_xyz()
            data['ax'].append(ax)
            data['ay'].append(ay)
            data['az'].append(az)

            # magnitude of acceleration
            am = np.sqrt(ax ** 2 + ay ** 2 + az ** 2)
            data['am'].append(am)

            # rotation around x,y,z axes
            rx, ry, rz = sensors.gyro.get_xyz()
            data['rx'].append(rx)
            data['ry'].append(ry)
            data['rz'].append(rz)

            # magnitude of rotation
            rm = np.sqrt(rx**2 + ry**2 + rz**2)
            data['rm'].append(rm)

            # Create a df when data reaches 100 rows
            if i >= 300:
                df = pd.DataFrame.from_dict(data)
                last_100_rows = df[-300:]
                X = last_100_rows.iloc[:, 1:]
                X = X.apply(z_normalisation)
                X = X.to_numpy(dtype=np.float32)
                X = X[np.newaxis, :, :]
                input_data = X
                interpreter.set_tensor(input_details[0]['index'], input_data)
                interpreter.invoke()
                output_data = interpreter.get_tensor(output_details[0]['index'])
                label = np.argmax(output_data)
                label_mapping = {0: "no kick", 1: "front kick", 2: "low roundhouse kick", 3: "mid roundhouse kick"}
                print(label_mapping[label])


except KeyboardInterrupt:
    pass