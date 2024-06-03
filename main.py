from parseOutput import parse
from collections import deque
from tkinter import *
from tkinter.filedialog import askopenfilename
import tkinter.font as tkfont
from PIL import Image, ImageTk
import sys


def main():
    master = Tk()
    master.title("coordinate placer")
    master.withdraw()

    filename = askopenfilename()
    if not filename:
        sys.exit()

    master.deiconify()
    image = Image.open(filename)
    width, height = image.size
    master.geometry(f"{width + 200}x{height}")
    bg = ImageTk.PhotoImage(image)

    canvas = Canvas(master, width=width, height=height)
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_image(0, 0, image=bg, anchor="nw")

    button_frame = Frame(master)
    button_frame.pack(side="right", fill="y")

    node = 0
    action_stack = deque()
    prevNodes = deque()  # [(nodeId, x, y)]

    points = {}  # dict, nodeId: ((x, y), [connections])
    rooms = {}  # dict, roomNo: [nodeId]

    def place_point(event):
        nonlocal node
        color = "red"
        connecting = False
        point1 = None
        if prevNodes:
            prevNode, prevX, prevY = prevNodes[-1]
            point1 = canvas.create_rectangle(prevX + 2, prevY + 2, prevX - 2, prevY - 2, fill="blue", outline="blue")
        for (k, ((x, y), z)) in points.items():
            if abs(x - event.x) < 7 and abs(y - event.y) < 7:
                point2 = canvas.create_rectangle(x + 2, y + 2, x - 2, y - 2, fill=color, outline=color)
                connecting = True
                prevNodes.append((k, x, y))
                n = k
                break
        if not connecting:
            n = node
            point2 = canvas.create_rectangle(event.x + 2, event.y + 2, event.x - 2, event.y - 2, fill=color,
                                             outline=color)
            points[node] = ((event.x, event.y), [])
            prevNodes.append((node, event.x, event.y))
            node += 1
        action_stack.append((n, point1, point2, None, connecting))

    def join_point(event):
        nonlocal node
        n = node
        if prevNodes:
            prevNode, prevX, prevY = prevNodes[-1]
            color = "red"
            connecting = False
            for (k, ((x, y), z)) in points.items():
                if abs(x - event.x) < 7 and abs(y - event.y) < 7:
                    point1 = canvas.create_rectangle(prevX + 2, prevY + 2, prevX - 2, prevY - 2, fill="blue",
                                                     outline="blue")
                    point2 = canvas.create_rectangle(x + 2, y + 2, x - 2, y - 2, fill=color, outline=color)
                    (_, connections) = points[prevNode]
                    connections.append(k)
                    (_, connections2) = points[k]
                    connections2.append(prevNode)
                    n = k
                    line = canvas.create_line(prevX, prevY, x, y, width=5, fill="hotpink1")
                    connecting = True
                    prevNodes.append((k, x, y))
                    break
            if not connecting:
                if abs(prevX - event.x) < 7:
                    line = canvas.create_line(prevX, prevY, prevX, event.y, width=5, fill="hotpink1")
                    point1 = canvas.create_rectangle(prevX + 2, prevY + 2, prevX - 2, prevY - 2, fill="blue",
                                                     outline="blue")
                    point2 = canvas.create_rectangle(prevX + 2, event.y + 2, prevX - 2, event.y - 2, fill=color,
                                                     outline=color)
                    prevY = event.y
                    points[node] = ((prevX, event.y), [prevNode])
                elif abs(prevY - event.y) < 7:
                    line = canvas.create_line(prevX, prevY, event.x, prevY, width=5, fill="hotpink1")
                    point1 = canvas.create_rectangle(prevX + 2, prevY + 2, prevX - 2, prevY - 2, fill="blue",
                                                     outline="blue")
                    point2 = canvas.create_rectangle(event.x + 2, prevY + 2, event.x - 2, prevY - 2, fill=color,
                                                     outline=color)
                    prevX = event.x
                    points[node] = ((event.x, prevY), [prevNode])
                else:
                    line = canvas.create_line(prevX, prevY, event.x, event.y, width=5, fill="hotpink1")
                    point1 = canvas.create_rectangle(prevX + 2, prevY + 2, prevX - 2, prevY - 2, fill="blue",
                                                     outline="blue")
                    point2 = canvas.create_rectangle(event.x + 2, event.y + 2, event.x - 2, event.y - 2, fill=color,
                                                     outline=color)
                    prevX, prevY = event.x, event.y
                    points[node] = ((event.x, event.y), [prevNode])
                (_, connections) = points[prevNode]
                connections.append(node)
                prevNodes.append((node, prevX, prevY))
                node += 1
            action_stack.append((n, point1, point2, line, connecting))

    def relaunch():
        global repeat
        repeat = True
        print_points()
        master.destroy()

    def print_points():
        for (k, ((x, y), cs)) in points.items():
            print(f"{k}: ({x}, {y}) -> {cs}")
        for (k, v) in rooms.items():
            print(f"{k}: {v}")
        print("-" * 10)

    def print_node():
        print(f"<{prevNodes[-1][0]}>")

    def import_nodes():
        nonlocal points, rooms, node
        while action_stack:
            undo()
        points, rooms = parse()
        for p in points.values():
            for con in p[1]:
                (x1, y1) = p[0]
                (x2, y2) = points[con][0]
                canvas.create_line(x1, y1, x2, y2, width=5, fill="hotpink1")
        for p in points.values():
            (x, y) = p[0]
            canvas.create_rectangle(x + 2, y + 2, x - 2, y - 2, fill="blue", outline="blue")
        node = max(points.keys()) + 1

    def undo():
        if action_stack:
            action = action_stack.pop()
            if len(action) == 2:
                (text, t) = action
                canvas.delete(t)
                if len(rooms[text]) == 1:
                    rooms.pop(text)
                else:
                    rooms[text].pop()
            else:
                (n, point1, point2, line, connecting) = action
                canvas.delete(point1)
                canvas.delete(point2)
                canvas.delete(line)
                prevNodes.pop()
                if not connecting:
                    points.pop(n, None)
                    if line is not None:
                        (_, connections) = points[prevNodes[-1][0]]
                        connections.remove(n)
                elif line is not None:
                    prevNode = prevNodes[-1][0]
                    (_, connections) = points[prevNode]
                    connections.remove(n)
                    (_, connections2) = points[n]
                    connections2.remove(prevNode)

    def assign_room():
        text = text_field.get()
        if text != "":
            (prevNode, x, y) = prevNodes[-1]
            font = tkfont.Font(family="Arial", size=16, weight=tkfont.BOLD)
            t = canvas.create_text((x, y - 10), text=text, fill="green3", font=font)
            if text in rooms:
                rooms[text].append(prevNode)
            else:
                rooms[text] = [prevNode]
            text_field.delete(0, END)
            action_stack.append((text, t))

    choose_file = Button(
        button_frame,
        text='change map',
        command=relaunch
    )
    choose_file.pack(ipadx=5, ipady=5, side="top", fill="x")

    print_button = Button(
        button_frame,
        text='print nodes',
        command=print_points
    )
    print_button.pack(ipadx=5, ipady=5, side="top", fill="x")

    print_node = Button(
        button_frame,
        text='print selected node',
        command=print_node
    )
    print_node.pack(ipadx=5, ipady=5, side="top", fill="x")

    import_button = Button(
        button_frame,
        text='import nodes',
        command=import_nodes
    )
    import_button.pack(ipadx=5, ipady=5, side="top", fill="x")

    undo_button = Button(
        button_frame,
        text='undo',
        command=undo
    )
    undo_button.pack(ipadx=5, ipady=5, side="top", fill="x")

    room_button = Button(
        button_frame,
        text='assign to room',
        command=assign_room
    )
    room_button.pack(ipadx=5, ipady=5, side="top", fill="x")

    text_field = Entry(button_frame, width=50)
    text_field.pack(ipadx=5, ipady=5, side="top", fill="x")

    canvas.bind("<ButtonPress-1>", place_point)  # left click to place point attached to nothing (or select existing point
    # so you can attach a new connection)
    canvas.bind("<Button-2>", join_point)  # right click to place a point, joining it to the point placed previously
    # coordinates -> list of connections'


    text_field.focus_set()
    master.mainloop()


repeat = True
if __name__ == "__main__":
    while repeat:
        repeat = False
        main()
