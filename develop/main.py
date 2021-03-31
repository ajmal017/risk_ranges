import tkinter as tk
from tkinter import filedialog, Text
import os

root = tk.Tk()

canvas = tk.Canvas(root, bg='#263D42')
canvas.pack()

frame = tk.Frame(root, bg="white")
frame.place()

mylabel = tk.Label(root, text="Hello")
mylabel.pack()

root.mainloop()
