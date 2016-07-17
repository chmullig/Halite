from asciimatics.effects import Cycle, Stars
from asciimatics.renderers import FigletText
from asciimatics.scene import Scene
from asciimatics.screen import Screen
import asciimatics

import numpy as np
import time
from replay import *

def play_replay(replay):

    def play_frame(screen, frameId):
        frame = replay.frames[frameId]
        screen.print_at('{} {} {}'.format(' '*10, ' PROD', '  STR') , replay.h*3, 0, 7)
        for i, ((player, _), stats) in enumerate(zip(replay.players, frame.stats)):
            player = player.ljust(10)[:10]
            myprod = str(stats['production']).rjust(5)
            mystr = str(stats['strength']).rjust(5)
            screen.print_at('{} {} {}'.format(player, myprod, mystr) , replay.h*3, i+1, i+1)
        for x in range(replay.w):
            for y in range(replay.h):
                thisStr = "{: =2X} ".format(frame.strengths[x,y])
                color = frame.owned_by[x,y]
                if color == 0:
                    color = 7 #white
                screen.print_at(thisStr, 3*y, x, color)
        screen.print_at("*"*int(frameId/replay.h), 0, replay.h, 7)
        screen.refresh()

    def play_prod(screen):
        for x in range(replay.w):
            for y in range(replay.h):
                thisStr = "{: =2X} ".format(replay.production[x,y])
                screen.print_at(thisStr, 3*y, x, 7)
        screen.refresh()

    def play(screen):
        playing = True
        wasPlaying = playing
        showGame = True
        lastFrame = 0
        cmd = None
        while True:
            if showGame:
                play_frame(screen, lastFrame)
            else:
                play_prod(screen)

            if cmd and not playing:
                time.sleep(0.01)
            else:
                time.sleep(0.1)

            cmd = None
            evt = screen.get_event() 
            if evt and type(evt) == asciimatics.event.KeyboardEvent:
                press = evt.key_code
                if press == screen.KEY_TAB:
                    cmd = '\t'
                elif press == screen.KEY_ESCAPE:
                    exit()
                else:
                    try:
                        cmd = chr(press)
                        screen.print_at(cmd, 0, replay.h+2, 7)
                    except:
                        pass
            if cmd == ' ':
                playing = not playing
            elif cmd == ',':
                lastFrame -= 1
            elif cmd == '.':
                lastFrame += 1
            elif cmd == '\t':
                if showGame:
                    wasPlaying = playing
                    playing = False
                    showGame = False
                else:
                    playing = wasPlaying
                    showGame = True
            elif playing:
                lastFrame += 1

            #ensure we stay in the game
            if lastFrame < 0:
                lastFrame = 0
            elif lastFrame >= len(replay.frames):
                if playing:
                    break
                else:
                    lastFrame = len(replay.frames)-1
    Screen.wrapper(play)

if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as f:
        r = Replay(f)
        play_replay(r)
