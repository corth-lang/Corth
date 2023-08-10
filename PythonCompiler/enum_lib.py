last = -1


def reset():
    global last

    last = -1


def step():
    global last

    last += 1
    return last

