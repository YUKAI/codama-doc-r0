# coding:utf-8
import os.path as osp
import sys
ver = (sys.version_info.major, sys.version_info.minor)
inspath = '../.lib/lib/python%d.%d/site-packages' % ver
sys.path.insert(0, osp.abspath(inspath))

import speak
from speak import Speak, NluMetaData


sdk = None

def mute():
    print ("mute")
    global sdk
    sdk.mute()


def unmute():
    print ("unmute")
    global sdk
    sdk.unmute()


def on_started():
    print ("on_started")

    # First
    global sdk

    # アプリケーション起動時に挨拶文を送信することにより、
    # Sebastienから返信メッセージが再生され起動確認が出来る。
    metaData = NluMetaData()
    metaData.cacheFlag = False
    # metaData.initTalkFlag = True
    metaData.voiceText = "こんにちは"
    sdk.put_meta(metaData)

    return


def on_failed(ecode, failstr):
    print ("on_failed : %s(%d)" % (failstr, ecode))
    return


def on_stop():
    print ("on_stop")
    return


def on_text_out(data):
    print ("on_text_out", data)
    return


def on_meta_out(data):
    print ("on_meta_out", data)
    return


def on_play_start(data):
    print ("on_play_start", data)
    return


def on_play_end(data):
    # 音声再生が終わったら、wake up wordを待機するためにSebastienの音声入力をOFFにする
    print ("on_play_end", data)
    global sdk
    sdk.mute()
    return


def on_cache_failed():
    print ("on_cache_failed")
    return


def on_gain_value(data):
    print ("on_gain_value", data)
    return

def cancel_play():
    print ("cancel play")

    global sdk
    sdk.cancel_play()

    return


def init(configname=None):
    global sdk
    if configname is not None:
        sdk = speak.Speak(configname)
    else:
        sdk = speak.Speak()

    # 要初期化
    sdk.init()

    # コールバック先の設定
    sdk.set_on_meta_out(on_meta_out)
    sdk.set_on_text_out(on_text_out)
    sdk.set_on_cache_failed(on_cache_failed)
    sdk.set_on_gain_value(on_gain_value)
    sdk.set_on_play_start(on_play_start)
    sdk.set_on_play_end(on_play_end)


def start():
    sdk.start(on_started, on_failed)
