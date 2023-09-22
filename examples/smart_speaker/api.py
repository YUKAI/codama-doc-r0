import pvporcupine
import openai
from google.cloud import texttospeech
import os
from dotenv import load_dotenv

load_dotenv('../.env') 

class Porcupine():
    def __init__(self):
        self.porcupine = pvporcupine.create(
            access_key=os.environ.get("ACCESS_KEY"),
            keyword_paths=["../codama_ja_raspberry-pi_v2_2_0.ppn"],
            model_path="../porcupine_params_ja.pv"
        ) 

class OpenAI():
    def __init__(self):
        openai.api_key = os.environ.get("OPEN_AI_API_KEY")
    
    def whisper(self, file: str) -> str:
        '''Convert wav file to text with whisper API.
        
        Args:
            file: A name of the audio file.
        
        Returns:
            Text converted from the audio file.
        '''
        audio_file= open(file, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        print('Convert audio to text:', transcript.text)
        return transcript.text
    
    def chatgpt(self, text: str, character: str) -> str:
        '''Reply with ChatGPT API
        
        Args:
            text: Text to be entered into the API
            character: ChatGPT's Character when replying
        
        Returns:
            Reply from ChatGPT API
        '''
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": character},
                {"role": "user", "content": text}
            ]
        )
        chat_message = completion.choices[0].message.content

        print('ChatGPT replies:', chat_message)
        return chat_message

class Google():
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secret-key.json"
        self.client = texttospeech.TextToSpeechClient()
    
    def synthesize_text(self, text: str, output_file: str):
        '''Convert text to speech and save to the audio file.
        
        Args:
            text: Text to be synthesized into speech
            output_file: File to save the text-to-speech result
        '''
        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-F",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        response = self.client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )

        with open(output_file, "wb") as out:
            out.write(response.audio_content)

    def synthesize_response(self, text: str):
        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            name="ja-JP-Wavenet-D",
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )
        return response