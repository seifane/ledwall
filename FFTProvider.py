import threading
import time

import numpy as np
import pyaudio
import scipy
from matplotlib import pyplot as plt
from numpy.fft import rfftfreq
from scipy import signal
from scipy.fft import rfft, fft


class FFTProvider:

    FRAME_RATE = 30
    BASE_SAMPLE_RATE = 44100
    CHUNK_SIZE = int(BASE_SAMPLE_RATE / FRAME_RATE)
    GAMMA = 2

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = None

        self.callbacks = []
        self.is_running = False
        self.current_thread = None


    def start(self):
        if self.stream is not None or self.is_running or self.current_thread is not None:
            return
        self.stream = self.pa.open(format=pyaudio.paFloat32,
                                   channels=1,
                                   rate=self.BASE_SAMPLE_RATE,
                                   input=True,
                                   output=False,
                                   frames_per_buffer=self.CHUNK_SIZE)
        self.last_frame = None
        self.is_running = True
        self.current_thread = threading.Thread(target=self.loop)
        self.current_thread.start()

    def stop(self):
        self.is_running = False
        self.current_thread.join()
        self.current_thread = None
        self.stream.close()
        self.stream = None

    def add_callback(self, cb):
        self.callbacks.append(cb)

    def get_last_frame_range(self, start, end):
        y_split = []
        x_split = []
        bins_splits = []
        if self.last_frame is None:
            return None
        for idx, freq in enumerate(self.last_frame[0]):
            if start <= freq <= end:
                y_split.append(self.last_frame[1][idx])
                x_split.append(freq)

        corrected_max = x_split[-1] - start
        for freq in x_split:
            bins_splits.append((((freq - start) / corrected_max) ** (1 / self.GAMMA)) * 100)

        return (x_split, y_split, bins_splits)

    def loop(self):
        while self.is_running:
            if self.stream.get_read_available() < self.CHUNK_SIZE:
                time.sleep(0.001)
                continue
            raw = self.stream.read(self.CHUNK_SIZE)
            raw_frame = np.frombuffer(raw, np.float32)
            hamming = signal.windows.hamming(len(raw_frame), False)
            raw_frame_filtered = []
            for idx, d in enumerate(raw_frame):
                raw_frame_filtered.append(d * hamming[idx])

            yf = rfft(raw_frame_filtered)
            xf = rfftfreq(len(raw_frame_filtered), 1 / self.BASE_SAMPLE_RATE)

            yf_mag = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in yf]

            binIdxs = []
            for freq in xf:
                binIdxs.append(((freq / xf[-1]) ** (1 / self.GAMMA)) * 100)

            self.last_frame = (xf, yf_mag, binIdxs)
