"""
- Read in data from sensors
- Create a buffer containing say 5 seconds worth of data
- Transform data and use saved model to predict it
- Output live predictions
"""

import sensors
import time
import grovelcd
import csv
import pandas as pd
import numpy as np
import re
import tflite_runtime.interpreter as tflite

# Creates a dataframe with the number of rows as column names
def create_dataframe_rows_as_columns(df):
    pattern = r'[0-9]'
    list_dfs = []
    lengths = []
    original_column_names = list(df.columns)
    new_column_names = []
    for i in range(212*7):
        name = f"{original_column_names[i%7]}_{i}"
        new_column_names.append(name)
    final_df = pd.DataFrame(columns=new_column_names)
    current_row = []
    whole_row = []
    temp = []
    for row in df.iterrows():
        # put all values from row in a list
        # append to whole row list
        current_row = row[1].values.flatten().tolist()
        whole_row.extend(current_row)
    if len(whole_row) < 212*7:
        for j in range(212*7-len(whole_row)):
            temp.append(pd.NA)
        whole_row.extend(temp)
    if len(whole_row) >= 212*7:
        whole_row = whole_row[:212*7]
    # print(len(whole_row))
    # print(final_df.columns)
    # print(len(final_df.columns))
    final_df.loc[len(final_df)] = whole_row
    whole_row = []
    temp = []
    final_df = final_df.dropna(axis=1)
    # Drop columns over 1204
    i=0
    columns_to_drop = []
    for column in final_df.columns:
        if i >= 1204:
            columns_to_drop.append(column)
        i+=1
    final_df = final_df.drop(columns=columns_to_drop)
    return final_df


def normalize_sample(df):
    mean_values = pd.read_pickle("mean_values.pkl")
    std_values = pd.read_pickle("std_values.pkl")
    for column_name in df.columns:
        df[column_name] = (df[column_name] - mean_values[column_name]) / std_values[column_name]
    return df

sensor_pins = {"accel": 0, "gyro": 0}
sensors.set_pins(sensor_pins)

try:
    while True:
        # data = {'ax': [], 'ay': [], 'az': [], 'am': [], 'rx': [], 'ry': [], 'rz': [], 'rm': []}
        data = {'ax': [], 'ay': [], 'az': [], 'am': [], 'rx': [], 'ry': [], 'rz': []}
        print("Reading for five seconds")
        timeout = time.time() + 4
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

            # # magnitude of rotation
            # rm = sensors.gyro.get_magnitude()
            # data['rm'].append(rm)

            # data to put in csv file
            # print(f"data: {ax, ay, az, am, rx, ry, rz, rm}")

            if time.time() > timeout:
                break
            time.sleep(0.01)
        print("EVALUATING")
        # Create a dataframe from the dictionary
        df = pd.DataFrame.from_dict(data)

        # Apply processing to dataframe
        converted_df = create_dataframe_rows_as_columns(df)
        numpy_df = normalize_sample(converted_df).to_numpy(dtype=np.float32)
        input_df = numpy_df.reshape((numpy_df.shape[0], numpy_df.shape[1], 1))
        np.save("input_df.npy", input_df)
        # Load Model
        TFLITE_FILE_PATH = '/best_model.tflite'

        interpreter = tflite.Interpreter(TFLITE_FILE_PATH)
        interpreter.allocate_tensors()

        # Get input and output tensors.
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        interpreter.set_tensor(input_details[0]['index'], input_df)
        # Predict sample
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        print(output_data)
        # Argmax to get label
        label = np.argmax(output_data)
        label_mapping = {0: "Front_kick", 1: "Low_roundhouse", 2: "Mid_roundhouse", 3: "Walking", 4: "Stationary",
                         5: "Lifting_knee"}

        print(label_mapping[label])

except KeyboardInterrupt:
    pass