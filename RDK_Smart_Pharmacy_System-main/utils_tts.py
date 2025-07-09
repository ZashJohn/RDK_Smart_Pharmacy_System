# utils_tts.py
# 语音合成

print('导入语音合成模块')

import os
import appbuilder
from API_KEY import *
import wave

os.environ["APPBUILDER_TOKEN"] = APPBUILDER_TOKEN
tts_ab = appbuilder.TTS()

def tts(TEXT='我是同济子豪兄的麒麟臂', tts_wav_path = 'temp/tts.wav'):
    '''
    语音合成TTS，生成wav音频文件
    '''
    inp = appbuilder.Message(content={"text": TEXT})
    out = tts_ab.run(inp, model="paddlespeech-tts", audio_type="wav")
    # out = tts_ab.run(inp, audio_type="wav")
    with open(tts_wav_path, "wb") as f:
        f.write(out.content["audio_binary"])
    # print("TTS语音合成，导出wav音频文件至：{}".format(tts_wav_path))

def play_wav(wav_file='asset/welcome.wav'):
    '''
    播放wav音频文件
    '''
    prompt = 'aplay -t wav {} -q'.format(wav_file)
    os.system(prompt)


if __name__ == '__main__':
    tts(TEXT='您好！我是由薯一薯二团队开发的具身智能机械臂，可以根据您的症状推荐非处方药，并提供专业的健康建议。请告诉我您哪里不舒服，我来帮您缓解。', tts_wav_path = 'temp/test.wav')
    play_wav()
