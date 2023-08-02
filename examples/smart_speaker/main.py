import pvporcupine
import queue, sys
import sounddevice as sd
import numpy as np
import audio
import api
import os
from dotenv import load_dotenv

load_dotenv('../.env') 

AUDIO_DEVICE_NUM = 8

# 録音の設定
SAMPLE_RATE = 16000
CHANNELS = 1

REC_FILE = "../sound/rec.wav"
OUTPUT_FILE = "../sound/output.wav"

# ChatGPTのキャラクター設定
CHAT_CHARACTER = '''あなたは英会話教室の教師です。
全て英語の歌にして返答します。必ず3行で返答します。
簡単な英単語だけを使ってください。'''

sd.default.device = AUDIO_DEVICE_NUM

codama = audio.Audio(SAMPLE_RATE, CHANNELS)
openai = api.OpenAI()
google = api.Google()

# porcupineの設定
porcupine = pvporcupine.create(
  access_key=os.environ.get("ACCESS_KEY"),
  keyword_paths=["../codama_ja_raspberry-pi_v2_2_0.ppn"],
  model_path="../porcupine_params_ja.pv"
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
                    stream.stop()
                    stream.close()

                    # 3秒間録音
                    codama.record(REC_FILE, 3)
                    # Whisper APIで音声データをテキストに変換
                    input_text = openai.whisper(REC_FILE)
                    # ChatGPT APIで返答を生成
                    reply_text = openai.chatgpt(input_text, CHAT_CHARACTER)
                    # Google Cloud Text-to-Speech APIで音声合成
                    google.synthesize_text(reply_text, OUTPUT_FILE)
                    # スピーカーで再生
                    codama.play(OUTPUT_FILE)
                    break

    except KeyboardInterrupt:
        pass
    finally:
        sd.stop()
        while not q.empty():
            q.get(block=False)

if __name__ == "__main__":
    run()