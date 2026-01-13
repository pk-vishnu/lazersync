import numpy as np
import matplotlib.pyplot as plt

class LEDControl:
    keyboard_matrix = [
        [21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, -1],
        [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 7],
        [49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 6],
        [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, -1, 5],
        [75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, -1, 63, -1],
        [76, 77, 78, -1, -1, -1, 79, -1, -1, -1, 0, 1, 2, 3, 4],
    ]
    def __init__(self, rows=6, cols=15):
        self.rows = rows
        self.cols = cols
        self.led_positions = self.generate_led_positions()
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-1, self.cols)
        self.ax.set_ylim(-1, self.rows)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.led_scatter = self.ax.scatter(
            [pos[0] for pos in self.led_positions],
            [pos[1] for pos in self.led_positions],
            c='black', s=100
        )

    def generate_led_positions(self):
        led_positions = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.keyboard_matrix[r][c] != -1:
                    led_positions.append((c, self.rows - 1 - r))
        return led_positions

    def update_leds(self, normalized_amplitudes):
        led_colors = ['black'] * len(self.led_positions)
        col_groups = [
            range(0, 3),   # Bass (columns 0, 1, 2)
            range(3, 5),   # Bass (columns 3, 4)
            range(5, 8),   # Mid (columns 5, 6, 7)
            range(8, 10),  # Mid (columns 8, 9)
            range(10, 12), # Treble (columns 10, 11)
            range(12, 15)  # Treble (columns 12, 13, 14)
        ]

        for band_idx, rows_lit in enumerate(normalized_amplitudes):
            for col in col_groups[band_idx]:
                valid_rows = [r for r in range(self.rows) if self.keyboard_matrix[r][col] != -1]
                valid_rows.sort()  # Ensure rows are sorted from bottom to top
                for i, row in enumerate(valid_rows[:rows_lit]):
                    flipped_row = row
                    if (col, flipped_row) in self.led_positions:
                        led_index = self.led_positions.index((col, flipped_row))
                        led_colors[led_index] = 'red'
        self.led_scatter.set_color(led_colors)

    def plot(self):
        plt.pause(0.01)

    def cleanup(self):
        plt.close(self.fig)
