#!/usr/bin/env python3

import sys
import json
import shelve
import model


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Convert organizer DB files used in previous versions to JSON format")
        print(f"Usage: {sys.argv[0]} [input.db] [output.json]")
        sys.exit(1)

    # load object from shelve
    with shelve.open(sys.argv[1]) as db:
        data = db["organizer"]

    # create dictionary from object
    boxes = []
    for box in data[0]:
        drawers = []
        for drawer in box.subelems:
            items = []
            for item in drawer.subelems:
                items.append({"name": item.name, "amount": item.amount})
            drawers.append({"items": items})
        boxes.append(
            {"x": box.x, "y": box.y, "h": box.h, "w": box.w, "drawers": drawers}
        )
    organizer = {"width": data[1], "height": data[2], "boxes": boxes}

    # dump dictionary to json
    with open(sys.argv[2], "w") as f:
        json.dump(organizer, f, indent=2)
