import os, sys
import ctypes
import numpy as np

class Map:
    @property
    def shape(self):
        return productions.shape
    def __init__(self, productions, owned_by, strengths):
        self.productions = productions
        self.owned_by = owned_by
        self.strengths = strengths
        self.moves = []
    def __getitem__(self, loc):
        x, y = loc
        return Site(self.owned_by[x, y], self.strengths[x, y], self.productions[x, y])


class Replay:
    def __init__(self, f):
        self.f = f
        magic, version = f.readline().split()
        assert magic == b'HLT'
        assert int(version) == 9

        self.w, self.h, self.nplayers, self.nframes = [int(x) for x in f.readline().split()]
        self.players = []
        for i in range(self.nplayers):
            name, rgb = f.readline().split(b"\0")
            self.players.append([name.decode('ascii'), [float(x) for x in rgb.split()]])

        prodbytes = (ctypes.c_uint8  * (self.w*self.h))()
        f.readinto(prodbytes)
        self.production = np.array(prodbytes).reshape((self.w,self.h))
        f.read(1) #apparently there's a newline here

        self.frames = []
        for i in range(self.nframes):
            frame = self._read_line()
            frame = self._get_statistics(frame)
            self.frames.append(frame)

    def _get_statistics(self, frame):
        stats = []
        for i, (player, _) in enumerate(self.players):
            s = {}
            overlay = np.nonzero(frame.owned_by == i+1)
            s['territory'] = len(overlay)
            s['production'] = self.production[overlay].sum()
            s['strength'] = frame.strengths[overlay].sum()
            stats.append(s)
        frame.stats = stats
        return frame

    def _read_line(self):
        owned_by = np.zeros_like(self.production)
        strength = np.zeros_like(self.production)

        x, y = 0, 0
        i = 0
        while i < self.w*self.h:
            numPieces = self.f.read(1)[0]
            owner = self.f.read(1)[0]
            for j in range(numPieces):
                if x >= self.h:
                    break
                tileStrength = self.f.read(1)[0]
                owned_by[x,y] = owner
                strength[x,y] = tileStrength
                y+=1
                i+=1
                if y >= self.w:
                    y = 0
                    x += 1

        prodbytes = (ctypes.c_uint8  * (self.w*self.h))()
        self.f.readinto(prodbytes)

        return Map(self.production, owned_by, strength)

if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as f:
        replay = Replay(f)
        print(replay.production)
        print(replay.frames[0].owned_by)
        print(replay.frames[-1].owned_by)
