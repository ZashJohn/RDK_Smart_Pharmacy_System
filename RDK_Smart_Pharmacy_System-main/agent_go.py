# agent_go.py

print('薯一薯二 \n')

from utils_asr import *             # 录音+语音识别
from utils_robot import *           # 连接机械臂
from utils_llm import *             # 大语言模型API
from utils_led import *             # 控制LED灯颜色
from utils_camera import *          # 摄像头
from utils_robot import *           # 机械臂运动
from utils_pump import *            # GPIO、吸泵
from utils_vlm_move import *        # 多模态大模型识别图像，吸泵吸取并移动物体
from utils_drag_teaching import *   # 拖动示教
from utils_agent import *           # 智能体Agent编排
from utils_tts import *             # 语音合成模块
from utils_vlm_vqa import *
from utils_getmedicine import *

# print('播放欢迎词')
pump_off()
# back_zero()
play_wav('temp/test.wav')

message=[]
message.append({"role":"system","content":AGENT_SYS_PROMPT})
def agent_play():
    '''
    主函数，语音控制机械臂智能体编排动作
    '''
    # 归零
    back_zero()
    
    # print('测试摄像头')
    #check_camera()
    
    # 输入指令
    # 先回到原点，再把LED灯改为墨绿色，然后把绿色方块放在篮球上
    start_record_ok = input('输入数字录音指定时长，按k打字输入，按c输入默认指令\n')
    if str.isnumeric(start_record_ok):
        DURATION = int(start_record_ok)
        record(DURATION=DURATION)   # 录音,默认存放在temp/speech_record.wav
        #record_auto()
        order = speech_recognition() # 语音识别,默认识别temp/speech_record.wav
    elif start_record_ok == 'k':
        order = input('请输入指令')
    elif start_record_ok == 'c':
        order = '先归零，再摇头，然后把绿色方块放在篮球上'
    else:
        print('无指令，退出')
        # exit()
        raise NameError('无指令，退出')
    message.append({"role":"user","content":order})
    # 智能体Agent编排动作

    #转换为python字典
    output=eval(agent_plan(message))

    print(output)
    response = output['response'] # 获取机器人想对我说的话
    print('开始语音合成')
    tts(response)                     # 语音合成，导出wav音频文件,默认存放在temp/tts.wav
    play_wav('temp/tts.wav')          # 播放语音合成音频文件
    output_other=''
    for each in output['function']: # 运行智能体规划编排的每个函数
        print('开始执行动作', each)
        ret = eval(each)
        if ret != None:
            output_other = ret

    output['response']+='.'+ output_other
    message.append({"role":"assistant","content":str(output)})
    #print(message)

# agent_play()
if __name__ == '__main__':
    while True:
        agent_play()

