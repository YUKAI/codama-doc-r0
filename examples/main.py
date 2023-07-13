import pvporcupine
import queue, sys
import sounddevice as sd
import audio
import api
import os
from dotenv import load_dotenv

load_dotenv('.env') 

REC_FILE = "sound/rec.wav"
OUTPUT_FILE = "sound/output.wav"

AUDIO_DEVICE_NUM = 8
DOWN_SAMPLE = 1
SAMPLE_RATE = 16000
CHANNELS = 1

# ChatGPTのキャラクター設定
CHAT_CHARACTER = '''あなたは幼児向け英会話教室の教師です。
全て英語の歌にして返答します。必ず3行で返答します。
英単語は30words以上50words以内で返答します。行末には必ずピリオドを打ちます。
中学生でもわかるような簡単な英単語だけを使ってください。'''

porcupine = pvporcupine.create(
  access_key=os.environ.get("ACCESS_KEY"),
  keyword_paths=[os.environ.get("KEYWORD_FILE_PATH")],
  model_path="porcupine_params_ja.pv"
)
q = queue.Queue()

codama = audio.Audio(SAMPLE_RATE, CHANNELS)
openai = api.OpenAI()
google = api.Google()
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
                cont = False
                stream.stop()
                stream.close()

                # 3秒間録音
                codama.record(REC_FILE, 3)
                input_text = openai.whisper(REC_FILE)
                reply_text = openai.chatgpt(input_text, CHAT_CHARACTER)
                google.synthesize_text(reply_text, OUTPUT_FILE)
                codama.play(OUTPUT_FILE)

    except KeyboardInterrupt:
        pass
    finally:
        sd.stop()
        while not q.empty():
            q.get(block=False)

if __name__ == "__main__":
    run()