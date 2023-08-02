import pvporcupine
import queue, sys
import numpy as np
import sounddevice as sd
import os
from dotenv import load_dotenv

load_dotenv('.env') 

AUDIO_DEVICE_NUM = 8

# 録音の設定
SAMPLE_RATE = 16000
CHANNELS = 1

sd.default.device = AUDIO_DEVICE_NUM

# porcupineの設定
porcupine = pvporcupine.create(
  access_key=os.environ.get("ACCESS_KEY"),
  keyword_paths=["codama_ja_raspberry-pi_v2_2_0.ppn"],
  model_path="porcupine_params_ja.pv"
)

q = queue.Queue()

def recordCallback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())

def run():
    try:
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            dtype="int16",
            blocksize=porcupine.frame_length,
            channels=CHANNELS,
            callback=recordCallback,
        )
        stream.start()
        print("Start")

        while True:
            if not q.empty():
                data = q.get(block=False)
                data = np.reshape(data, [data.shape[0]])
                
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