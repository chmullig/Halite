from asciimatics.effects import Cycle, Stars
from asciimatics.renderers import FigletText
from asciimatics.scene import Scene
from asciimatics.screen import Screen

import numpy as np
import time

size = 10
prod = np.random.random_integers(1,10, size*size).reshape((size, size))
strength = np.random.random_integers(0, 255, size*size).reshape((size, size))
owner = np.random.random_integers(0, 3, size*size).reshape((size, size))


def demo(screen):
    for x in range(size):
        for y in range(size):
            thisStr = "{: =2X} ".format(strength[x,y])
            screen.print_at(thisStr, 3*x, y, owner[x,y], 3 if owner[x,y] > 0 else 2)
    screen.refresh()
    time.sleep(10)

Screen.wrapper(demo)
