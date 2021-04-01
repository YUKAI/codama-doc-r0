# ドコモAIエージェントAPIを利用したサンプルプログラムの実行

codamaを取り付けたRaspberry PiはNTTドコモが提供するドコモAIエージェントAPIのSpeak SDK for Pythonを利用して音声による対話を実現することが可能です。
(Speak SDK for Pythonの入手方法はドコモAIエージェントのドキュメントサイトよりご確認ください)

まず、以下の設定ガイドを参照し、I2S接続でのcodamaのセットアップ、ウェイクアップワードの作成を終わらせてください。

1. [Raspberry Piを設定する](../../../wiki/Raspberry-Pi-Setup)
2. [codamaをRaspberry Piに取り付け、設定する](../../../wiki/Codama-Setup)
3. [ウェイク・アップ・ワードの作成、動作確認をする](../../../wiki/regist-wake-up-word)

## 1. スピーカーの取り付け

codamaのボードには、音声出力するための、スピーカー端子(AUX)とスピーカ出力が備え付けられています。いずれかに、スピーカーを取り付けます。

スピーカーが動作可能かを確認するには以下のコマンドを実行します。Raspberry Piでは、デフォルトで音声出力は有効になっています。

```
$ aplay -l
**** ハードウェアデバイス PLAYBACK のリスト ****
カード 0: sndrpisimplecar [snd_rpi_simple_card], デバイス 0: simple-card_codec_link snd-soc-dummy-dai-0 []
  サブデバイス: 1/1
  サブデバイス #0: subdevice #0
```

## 2. Raspberry Pi上の環境構築

AIエージェントと連携するライブラリの動作に必要なものをインストールします。

```
$ sudo apt install pulseaudio
```

ライブラリをインストールします。

```
$ pip3 install --user https://github.com/docomoDeveloperSupport/speak-python-sdk/releases/download/v1.16.2/speak-1.16.2-cp37-cp37m-linux_armv7l. whl
```

サンプルプログラムを用意し、動作に必要なものをインストールします。

```
$ git clone -b trial https://github.com/docomoDeveloperSupport/speak-python-sample.git
$ pip3 install pyuv
```

## 3. ドコモAIエージェントAPI側の準備

ここではドコモAIエージェントAPIを利用する上で最小限のAIエージェントを作成していきます。

1. [Agentcraft](https://agentcraft.sebastien.ai)にアクセスし、お手持ちのGoogleアカウントやdアカウントでログインします。

<img src="https://user-images.githubusercontent.com/48305340/108954094-94a30c80-76af-11eb-9335-4520ad664886.png" width=600>
<br><br>

2. 新規AIエージェントを作成し、その後「新規トピック」を選択します。

<img src="https://user-images.githubusercontent.com/48305340/108955275-3bd47380-76b1-11eb-9259-3665589d5d05.png" height=400>
<img src="https://user-images.githubusercontent.com/48305340/108955397-6de5d580-76b1-11eb-9ea2-12c5c348c236.png" height=400>
<img src="https://user-images.githubusercontent.com/48305340/108955458-8c4bd100-76b1-11eb-983d-49e86262e187.png" height=200>
<br><br>

3. 以下のように入力していきます。トピック名、セクション名はなんでもかまいません。このAIエージェントは「こんにちは」と話しかけると「お名前をどうぞ」と返答し、名前を言うと「XXさんですね。よろしくおねがいします」と答える設定になっています。名前の部分を抽出して`#username`という変数に代入しています。入力を終えたら保存してください。

<img src="https://user-images.githubusercontent.com/48305340/109259525-b92dee80-783f-11eb-8a47-5b2cbe4ce8b6.jpg" width=1000>
<br><br>

4. 画面右下の青いアイコンからAIエージェントのテストができます。上の設定ができていれば以下のように動作します。

<img src="https://user-images.githubusercontent.com/48305340/109259803-4f621480-7840-11eb-9137-36d64b6f2b9d.png" width=250>

## 4. サンプルプログラムの実行

サンプルプログラムは、codamaでウェイク・アップ・ワードを検出すると、AIエージェントとの対話モードを開始し、AIエージェントから返答が来ると、ウェイク・アップ・ワードを待つというプログラムとなっています。

codamaはウェイク・アップ・ワードを検出するとGPIOの27をHIGHに設定します。また、AIエージェントは音声入力をON/OFFする機能を備えており、それらを用いてウェイク・アップ・ワードの検出と対話を実現しています。

<a name=get-device-token></a>
1. device_tokenを設定する

Raspberry Piのブラウザ上でAgentcraftを開いている場合、以下のように「設定」を選択したあと「デバイスを追加」を選択し、発行されたデバイストークンをコピーします。

<img src="https://user-images.githubusercontent.com/48305340/108959278-878a1b80-76b7-11eb-9e2f-0f9f4d075bb1.png" width=150>
<img src="https://user-images.githubusercontent.com/48305340/108960312-0df32d00-76b9-11eb-9bf6-d52af057a5f5.png" width=700>

またサンプルプログラムからデバイストークンを取得する方法もあります。まず上の画像内のクライアントシークレットをコピーして`speak-python-sample/GetTrialDeviceToken.py`を開き、`CLIENT_SECRET=`の後を置き換えます。

<img src="https://user-images.githubusercontent.com/48305340/108960180-d84e4400-76b8-11eb-8abc-5a2a56efa3e5.png" width=400>

そしてこのコードを実行し、出力結果からデバイストークンをコピーします。

```
$ python3 GetTrialDeviceToken.py
URL[https://api-agentcraft.sebastien.ai/devices]
SAVE ./.trial_device_id : XXXXXXXX-XXXX-XXXX-XXXX- XXXXXXXX
URL[https://api-agentcraft.sebastien.ai/devices/token]
SAVE ./.trial_device_token : XXXXXXXX-XXXX-XXXX-XXXX- XXXXXXXX
SAVE ./.trial_refresh_token : XXXXXXXX-XXXX-XXXX-XXXX- XXXXXXXX
```

以上どちらかの方法でコピーしたデバイストークンで`codama-doc-r0/sebastien/example/main.py`の`DEVICE_TOKEN=`の後を置き換えます。

<img src="https://user-images.githubusercontent.com/48305340/108966395-77773980-76c1-11eb-818e-903ac41a311b.png" width=350>
<br><br>

2. プログラムの実行と終了

以下のコマンドを実行し、プログラムを起動します。ウェイク・アップ・ワードを検出するとコンソールに `detected wake-up-word` と表示されます。その後、AIエージェントと対話をしてください。プログラムの終了は`ctrl-C`で行います。

```
$ python3 main.py
```

うまく反応が返ってきたらAIエージェント側の設定をいろいろ試してみましょう。ドコモAIエージェントAPIの[ドキュメントサイト](https://docs.sebastien.ai/documents/)を参考にしてください。

#### (補足)エラーメッセージ発生時の対処(Device Token の取り直し)

上記コマンド実行時に
```
UDS:Signature Expired(40102)
```

というエラーが発生する場合は [device_tokenを設定する](#get-device-token) 
からやり直してください。

