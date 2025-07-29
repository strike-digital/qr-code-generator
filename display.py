import random
from tkinter import Canvas, Tk


def display_qr_code(matrix: list[list], sequence: list[list[int, int]] = None):
    root = Tk()
    size = len(matrix[0])
    tile_size = 20

    w = Canvas(root, width=tile_size * size, height=tile_size * size)

    x = y = 0
    for row in matrix:
        for item in row:
            fill = "white"
            outline = "black"
            if item:
                fill = "black"
                outline = "black"
            w.create_rectangle(x, y, x + tile_size, y + tile_size, fill=fill, outline=outline)
            x += tile_size
        x = 0
        y += tile_size

    if sequence:
        x = y = -1
        for i, (column, row) in enumerate(sequence):
            prev_x = x
            prev_y = y
            x = row * tile_size + (tile_size / 2)
            y = column * tile_size + (tile_size / 2)
            if prev_x != -1:
                w.create_line(prev_x, prev_y, x, y, fill="blue")
            w.create_text(x, y, text=str(i))

    w.pack()
    root.mainloop()


def get_random_matrix(size):
    return [[random.getrandbits(1) for _ in range(size)] for _ in range(size)]


if __name__ == "__main__":
    display_qr_code(get_random_matrix(40))
