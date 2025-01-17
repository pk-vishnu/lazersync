# LazerSync [ WIP ]

LazerSync is a Python-based client-side visualization tool that generates real-time audio visualizations of given Device_ID and sends control data to a QMK keyboard firmware (LazerCore) via RAW HID. The visualizer uses an LED matrix to dynamically adjust based on the frequency bands of the audio input, providing synchronized RGB_MATRIX.

![Recording 2025-01-16 224056](https://github.com/user-attachments/assets/ca12cc01-f1ae-485b-a1c1-86045b8bfca5)


## Features

- **Real-time Audio Visualization**: 
  Visualizes audio frequencies across multiple bands in real time, driving a customizable LED matrix.

- **Volume-Based Normalization**: 
A script that normalizes the audio data based on raw audio amplitude.

- **Max Rows Normalization**: 
  A script that normalizes the audio data to fit within a fixed number of rows (6).

- **RAW HID Communication**: 
  Communicates directly with a QMK-based keyboard firmware, sending frequency band data via RAW HID protocol.

- **Dynamic RGB Matrix**: 
  Adjusts the color of the LEDs dynamically based on the audio input.


## How it works
LazerSync uses an FFT (Fast Fourier Transform) algorithm to break down audio data into different frequency bands. The bands are then normalized based on the amplitude, which controls how many rows of the keyboard's LED matrix will light up. This data is sent via the RAW HID protocol to the QMK firmware.

The QMK firmware processes the data and updates the RGB matrix based on the received values.

## RAW HID Protocol
The data sent to the QMK firmware contains a set of values that represent the number of rows to light up for each frequency band. These values are mapped to the RGB matrix's columns, ensuring a synchronized audio-to-LED experience.
