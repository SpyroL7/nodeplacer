from main import main
from tkinter import *
from tkinter.filedialog import askopenfilename

master = Tk()
master.title("coordinate placer")
master.withdraw()

points = {}  # nodeId: ((x, y), [connections])
rooms = {}

filename = askopenfilename()
f = open(filename, "r")
for line in f:
    if line == "\n":
        pass
    elif line[-2] == ']':
        parts = line.split(" ")
        connections = list(map(lambda x : int(x.replace("[", "").replace(",", "").replace("]", "")), parts[4:]))
        print(connections)
        points[parts[0][:-1]] = ((int(parts[1][1:-1]), int(parts[2][:-1])), connections)
    else:
        parts = line.split(":")
        rooms[parts[0]] = parts[1].strip()


print(points)
print(rooms)