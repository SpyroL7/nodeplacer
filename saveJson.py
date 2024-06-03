import json
from parseOutput import parse


def toJson(points, rooms):
    ps = [{"nodeId": k, "coords": v1, "connections": v2} for (k, (v1, v2)) in points.items()]
    rs = [{"roomName": k, "nodes": v} for (k, v) in rooms.items()]

    output = {
        "nodes": ps,
        "rooms": rs
    }

    output_file = open("data.json", "w")
    json.dump(output, output_file, indent=4)


p, r = parse()
toJson(p, r)