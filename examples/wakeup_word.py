import pvporcupine
import queue, sys
import sounddevice as sd
import os
from dotenv import load_dotenv

load_dotenv('.env') 

AUDIO_DEVICE_NUM = 8
DOWN_SAMPLE = 1
SAMPLE_RATE = 16000
CHANNELS = 1

porcupine = pvporcupine.create(
  access_key=os.environ.get("ACCESS_KEY"),
  keyword_paths=["kodama_ja_raspberry-pi_v2_2_0.ppn"],
  model_path="porcupine_params_ja.pv"
)
q = queue.Queue()

sd.default.device = AUDIO_DEVICE_NUM

def recordCallback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())

def run():
    try:
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            dtype="int16",
            blocksize=512,
            channels=CHANNELS,
            callback=recordCallback,
        )
        stream.start()

        print("Start")
        cont = True

        while cont:
            while q.empty():
                pass
            data = q.get(block=False)
            data = data[::DOWN_SAMPLE, 0]

            keyword_index = porcupine.process(data)

            # "こだま"を検知したら
            if keyword_index == 0:
                print("Detected: こだま")

    except KeyboardInterrupt:
        pass
    finally:
        sd.stop()
        while not q.empty():
            q.get(block=False)

if __name__ == "__main__":
    run()