# Sebastienを利用したcodamaサンプルコード

codamaを取り付けたRaspberryPiはNTTドコモが提供する[/project:SEBASTIEN/](https://dev.smt.docomo.ne.jp/?p=common_page&p_name=sebastien_teaser)を利用して音声による対話を実装することが可能です。

まず、以下の設定ガイドを参照し、codamaのセットアップを終わらせてください。

* [Raspberry Piの設定ガイド](Raspberry-Pi-Setup)
* [codamaの取り付けおよび設定ガイド](Codama-Setup)

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

## 2. Sebastienライブラリのインストール

Sebastienを利用するためのライブラリをインストールします。Sebastienはpython3系、python2系どちらのバージョンでも動作します。ここでは、デフォルトの状態で、python3系とpython2系をインストールする方法を示します。


* python3系のインストール

```
$ cd wheel
$ sudo pip3 install speak-1.1.1-cp35-cp35m-linux_armv7l.whl
```

* python2系のインストール

```
$ cd wheel
$ sudo pip install speak-1.1.1-cp27-cp27mu-linux_armv7l.whl
```

## 3. Sebastienデバイストークンの取得

Sebastienのライブラリを利用するためには、Sebastienにアクセスするためのデバイストークンが必要です。以下の操作を実行してデバイストークンを取得してください。

### 手順1. device_idをリクエストする。

以下のコマンドを利用して、device_idをリクエストします。`client_secret`は、ロボスタトークプロバイダのものを利用できます。

client_secret: e68f2ef7-1e68-4e92-b48f-d2f92b2daa4e

```
$ curl https://mds.sebastien.ai/api/issue_device_id -X POST -H 'Content-Type:application/json' -d '{"client_secret": "e68f2ef7-1e68-4e92-b48f-d2f92b2daa4e"}' 
{
    "device_id": "{返信されたデバイスID}", 
    "status": "valid"
}
```

### 手順2. device_idをSebastienのユーザダッシュボードに登録する。

Sebastienのユーザダッシュボード[https://users.sebastien.ai/dashboard/](https://users.sebastien.ai/dashboard/)にアクセスし、手順1で取得した、 `device_id` を登録します。

* ユーザダッシュボードに表示される「新規デバイス登録」をクリックします。

<img width="500" alt="dashboard" src="https://user-images.githubusercontent.com/1875915/50274589-f4bf1800-0480-11e9-8819-4a25003e89ad.png">

* 手順1で取得した、`device_id`を入力して「登録」を押します。

<img width="500" alt="adddevice" src="https://user-images.githubusercontent.com/1875915/50274640-0f918c80-0481-11e9-89cc-c5fed5c04186.png">

* ロボスタトークのデバイスとして登録されたことを確認します。

<img width="500" alt="robotstart" src="https://user-images.githubusercontent.com/1875915/50274661-1e783f00-0481-11e9-8dd4-8a077969ff32.png">


### 手順3. device_tokenを取得する。

* 以下のコマンドを利用して、`device_token`を取得します。取得した`device_token`は、サンプルプログラムで利用します。

```
curl https://users.sebastien.ai/api/req_device_token -X POST -H 'Content-Type:application/json' -d '{"device_id": "{手順1で取得したデバイスID}"}'

{
    "device_token": "{デバイストークン}", 
    "refresh_token": "{リフレッシュトークン}", 
    "status": "valid"
}
``` 


## 4. サンプルプログラムの実行

サンプルプログラムは、codamaでウェイク・アップ・ワードを検出すると、Sebastienの対話モードを開始し、Sebstienから返答が来ると、ウェイク・アップ・ワードを待つというプログラムとなっています。

codamaはウェイク・アップ・ワードを検出するとGPIOの27をHIGHに設定します。また、Sebastienは音声入力をON/OFFする機能を備えており、それらを用いてウェイク・アップ・ワードの検出と対話を実現しています。

### 手順1. device_tokenを記述する

* `config.json.tmp` をコピーして、`config.json`をエディターで開き、`AccessToken` に取得した`device_token` を入力します。

```
{
    "Port"              : 443,
    "Host"              : "spf.sebastien.ai",
    "URLPath"           : "/talk",
    "OutputGain"        : 1.0,
    "UseSSL"            : true,
    "MicMute"           : true,
    "EnableOCSP"        : false,
    "AccessToken"       : "",   # device_tokenを入力します
    "EcBin"             : "nl_aec_all.bin",
    "NumPlayChannels"   : 1,
    "NumPlayFs"         : 16000,
    "NumPlaySPF"        : 320,
    "NumRecordChannels" : 1,
    "NumRecordFs"       : 16000,
    "NumRecordSPF"      : 320,
    "SendChannel"       : 1,
    "NumThreadPools"    : 2,
    "IntellimicSetting" : "",
    "IntellimicGain"    : 1.0,
    "TimeoutTimeOpenHandshake"  : 5000,
    "TimeoutTimeCloseHandshake" : 1000,
    "TimeoutTimeAuthentication" : 5000,
    "TimeoutTimeSocketShutdown" : 100,
    "IntervalTimeHeartbeat"     : 2000,
    "TimeoutTimeHeartbeat"      : 2000
}
```

### 手順2. プログラムの実行と終了

以下のコマンドを実行し、プログラムを起動します。ウェイク・アップ・ワードを検出するとコンソールに `detected wake-up-word` と表示されます。その後、Sebastienと対話をしてください。プログラムの終了は`ctrl-C`で行います。

```
$ python3 main.py
```


