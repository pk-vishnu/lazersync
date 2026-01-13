import numpy as np
import time

class FakeAudio:
    def __init__(self):
        self.start = time.time()

    def get_bands(self):
        t = time.time() - self.start

        bass = int((1 + np.sin(t * 2)) * 127)
        mids = int((1 + np.sin(t * 1.3)) * 80)
        highs = int((1 + np.sin(t * 3.7)) * 50)

        return [
            bass,
            bass // 2,
            mids,
            mids // 2,
            highs,
            highs // 2,
        ]
