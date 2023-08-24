import sounddevice as sd
import numpy as np
import openai
import asyncio
from pydub import AudioSegment
from io import BytesIO
import pyaudio
from google.cloud import texttospeech
import os
from dotenv import load_dotenv

load_dotenv('../.env') 

SAMPLE_RATE = 16000
CHANNELS = 1

openai.api_key = os.environ.get("OPEN_AI_API_KEY")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secret-key.json"
client = texttospeech.TextToSpeechClient()

# ChatGPTのキャラクター設定
CHAT_CHARACTER = '''あなたはなんでも解説してくれる博士です。6行で説明してください。ただし一文ごとに/を入れて話してください。最後も/で終わってください。'''

async def text_to_speech(text, stream):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP",
        name="ja-JP-Wavenet-D",
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    audio_segment = AudioSegment.from_mp3(BytesIO(response.audio_content))

    stream.write(np.array(audio_segment.get_array_of_samples(), dtype=np.int16))

async def speech_worker(text_queue):
    stream = sd.OutputStream(
        samplerate=SAMPLE_RATE,
        dtype="int16",
        channels=CHANNELS,
    )
    stream.start()
    word = ''
    while True:
        text = await text_queue.get()
        if text is None:
            break

        word += text
        if '/' in word:
            word = word.strip('/')
            print(word)
            await text_to_speech(word, stream)
            word = ''


async def chat_worker(text_queue):
    async for chunk in await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": CHAT_CHARACTER},
            {"role": "user", "content": input_text}
        ],
        temperature=0.8,
        stream=True
    ):
        content = chunk['choices'][0]['delta'].get('content')
        if content:
            print(content)
            await text_queue.put(content)

async def main():
    global input_text
    input_text = "猫"
    text_queue = asyncio.Queue()

    chat_task = asyncio.create_task(chat_worker(text_queue))
    speech_task = asyncio.create_task(speech_worker(text_queue))

    await chat_task
    await text_queue.put(None)
    await speech_task
    
asyncio.run(main())