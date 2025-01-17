import matplotlib.pyplot as plt

# Keyboard Matrix Layout
keyboard_matrix = [
    [21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, -1],  # Row 1
    [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 7],  # Row 2
    [49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 6],  # Row 3
    [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, -1, 5],  # Row 4
    [75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, -1, 63, -1],  # Row 5
    [76, 77, 78, -1, -1, -1, 79, -1, -1, -1, 0, 1, 2, 3, 4],   # Row 6
]

col_groups = [
    range(0, 3),   # Band 1: Bass (columns 0, 1, 2)
    range(3, 5),   # Band 2: Bass (columns 3, 4)
    range(5, 8),   # Band 3: Mid (columns 5, 6, 7)
    range(8, 10),  # Band 4: Mid (columns 8, 9)
    range(10, 12), # Band 5: Treble (columns 10, 11)
    range(12, 15)  # Band 6: Treble (columns 12, 13, 14)
]

# Create a mapping of matrix positions to coordinates for plotting
rows, cols = len(keyboard_matrix), len(keyboard_matrix[0])
led_positions = [(c, rows - 1 - r) for r in range(rows) for c in range(cols) if keyboard_matrix[r][c] != -1]


def update_leds(led_scatter, normalized_amplitudes, col_groups, led_positions, rows):
    """Updates the LED scatter plot based on normalized amplitudes."""
    led_colors = ['black'] * len(led_positions)

    for band_idx, rows_lit in enumerate(normalized_amplitudes):
        for col in col_groups[band_idx]:
            valid_rows = [r for r in range(rows) if keyboard_matrix[r][col] != -1]
            valid_rows.sort()

            for i, row in enumerate(valid_rows[:rows_lit]):
                flipped_row = row
                if (col, flipped_row) in led_positions:
                    led_index = led_positions.index((col, flipped_row))
                    led_colors[led_index] = 'red'

    led_scatter.set_color(led_colors)
    return led_scatter
