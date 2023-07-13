import soundfile as sf
import sounddevice as sd
from scipy import signal
from scipy.io.wavfile import write

class Audio:
    def __init__(self, fs: int, channels: int):
        '''Recording Settings'''
        self.fs = fs
        self.channels = channels

    def play(self, file: str):
        '''Play an audio file'''
        data, samplerate = sf.read(file)
        converted_data = signal.resample(data, int(len(data) * self.fs / samplerate))
        sf.write("sound/converted_test.wav", converted_data, self.fs)
        sd.play(converted_data, self.fs)
        sd.wait()

    def record(self, file: str, duration: int):
        '''Record and save audio to wav file'''
        print('Recording...')
        recording = sd.rec(int(duration * self.fs), samplerate=self.fs, channels=self.channels)
        sd.wait()
        print('Recording stop')

        write(file, self.fs, recording)