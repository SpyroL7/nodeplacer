from tkinter import *
from tkinter.filedialog import askopenfilename


def parse():
    master = Tk()
    master.title("coordinate placer")
    master.withdraw()

    points = {}  # nodeId: ((x, y), [connections])
    rooms = {}

    filename = askopenfilename()
    f = open(filename, "r")
    for line in f:
        line = line.strip()
        if "->" in line:
            parts = line.split(" ")
            if parts[4] == "[]":
                connections = []
            else:
                connections = list(map(lambda x: int(x.replace("[", "").replace(",", "").replace("]", "")), parts[4:]))
            points[int(parts[0][:-1])] = ((int(parts[1][1:-1]), int(parts[2][:-1])), connections)
        elif line != "\n":
            parts1 = line.split(":")
            parts2 = parts1[1].strip().split(" ")
            room_nodes = list(map(lambda x: int(x.replace("[", "").replace(",", "").replace("]", "")), parts2))
            rooms[parts1[0]] = room_nodes
    f.close()
    return points, rooms
