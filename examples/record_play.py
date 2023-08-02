# 録音して再生する
import sounddevice as sd
from scipy.io.wavfile import write

# 録音の設定
SAMPLE_RATE = 16000     # サンプリングレート
DURATION = 5            # 録音時間（秒）
CHANNELS = 1            # モノラル

# 録音ファイルのパス
REC_FILE = 'sound/recorded.wav'

# 録音実行
print('Recording...')
recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS)
sd.wait()
print('Recording stop')

# wavファイルに保存
write(REC_FILE, SAMPLE_RATE, recording)

# 録音ファイルを再生
sd.play(recording, SAMPLE_RATE)
sd.wait()