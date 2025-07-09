import json
import ast
from API_KEY import *
from openai import OpenAI
from utils_tts import *
from utils_robot import *
from utils_yolo import *

def load_and_parse_results():
    """从 global_results.txt 加载并解析为 Python 列表"""
    try:
        with open("global_results.txt", "r", encoding="utf-8") as f:
            content = f.read().strip()  # 读取并去除首尾空格
            data = ast.literal_eval(content)  # 安全解析 Python 字面量
            return data
    except FileNotFoundError:
        print("错误：未找到 global_results.txt 文件")
        return None
    except (SyntaxError, ValueError) as e:
        print(f"错误：文件内容解析失败 - {e}")
        return None

# 模块全局变量声明
global_results = None  # 初始化为None，后续由load_medicine()填充



# 药品中英文名称对照表
MEDICINE_NAME_MAPPING = {
    '甲硝唑片': 'JiaXiaoZuoPian',
    '感冒灵颗粒': 'GanMaoLingKeLi',
    '莫匹罗星软膏': 'MoPiLuoXingRuanGao',
    '醋酸地塞米松口腔贴片': 'CuSuanDiSeMiSongKouQiangTiePian',
    '阿莫西林胶囊': 'AMoXiLinJiaoNang',
    '藿香正气水': 'HuoXiangZhengQiShui',
    '盐酸伐昔洛韦片': 'YanSuanFaXiLuoWeiPian',
    '布洛芬': 'BuLuoFen'
}


def yolo_getmedicine(medicine='感冒灵颗粒'):
    #第一步
    # 根据文字生成对应的wav文件
    tts(f'{medicine}马上就到了')

    # 播放语音
    play_wav('temp/tts.wav')

    #第二步,根据返回的结果查找药品,并记录其保存在哪张图片以及中心点在图片中的位置,获取direction,center_x,center_y
    result=find_medicine_positions(medicine, global_results)[0]
    print(result)
    direction=result['direction']
    center_x=result['center_x']
    center_y=result['center_y']

    #第三步,根据direction,来转动到指定的方向
    if(direction==0):
        mc.send_angles([-100, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
    elif(direction==1):
        mc.send_angles([-40, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
    elif (direction == 2):
        mc.send_angles([60, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
    elif (direction == 3):
        mc.send_angles([120, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
    time.sleep(3)

    #第四步,根据center_x,center_y,手眼标定来获取机械臂该移动到的物理坐标
    mmachine_x,mmachine_y=eye2hand(center_x,center_y,direction)
    print([mmachine_x,mmachine_y])
    safe=160
    end=[286.2,3]
    if medicine=='感冒灵颗粒':
        h=110
        safe=200
        end=[240,3]
    elif medicine=='阿莫西林胶囊' or medicine=='藿香正气水':
        h=90
    else:
        h=65

    #第五步,吸取并移动药品
    move_medicine(mc, XY_START=[mmachine_x,mmachine_y], HEIGHT_START=h,XY_END=end, HEIGHT_SAFE=safe)
    tts(f'{medicine}已经帮您放到盒子中,请小主人吃药啦')

    # 播放语音
    play_wav('temp/tts.wav')



def llm_yolo_getmedicine(PROMPT='我感冒流鼻涕，还喉咙肿痛,请帮我开药'):
    #第一步:识别并记录四周存在的药品以及它们的位置
    tts('别着急呀,药品正在识别中，小主人可以先准备好温水哦')
    # 播放语音
    play_wav('temp/tts.wav')
    if global_results==None:
        load_medicine()
    tts('扫描完毕,所有药品坐标已锁定,正在帮你挑选最合适的药方')
    # 播放语音
    play_wav('temp/tts.wav')

    SYSTEM_PROMPT = '''
    我即将说一句给机械臂的指令,这个指令中包含了我目前的生病的症状,请你根据我的症状,在以下八种药品中找到合适药物来治疗,只用返回药品名称即可
    8种药品分别为:'甲硝唑片','感冒灵颗粒','莫匹罗星软膏','醋酸地塞米松口腔贴片','阿莫西林胶囊','藿香正气水','盐酸伐昔洛韦片','布洛芬'
    
    【输出json格式】
    你直接输出json即可, 从{开始, 记住一定不要输出包含```json的开头或结尾
    在'medicine'键中,输出药品名列表,列表中的每个元素必须与上面给出的八种药品名称相同,针对用户的症状可以返回能够治疗该症状的多个药品名称,如果在已有的4中药品中没有找到能够治疗该症状的药品,则对应空列表
    在'response'键中,以第一人称输出你回复我的话,必须有response键且不能为空,回复内容不超过30个字,回复帮我找到的对应药品名称即可,要求温暖一些,尽可能体现出对我的关怀,如果没有找到药品名称,就给出建议的药品
    
    【以下是一些具体的例子】
    我的指令:"我发烧到38.5℃，头很痛,请帮我开药" 你输出:{"medicine": ["布洛芬"], "response": "布洛芬能退烧止痛，记得多喝水呀！"}
    我的指令:"我感冒流鼻涕，还喉咙肿痛,请帮我开药" 你输出:{"medicine": ["感冒灵颗粒", "阿莫西林胶囊"], "response": "感冒灵缓解症状，阿莫西林消炎，早日康复哦！"}
    我的指令:"手上擦伤后红肿发炎了请帮我开药" 你输出:{"medicine": ["莫匹罗星软膏"], "response": "涂软膏消炎，伤口别碰水呢！"}
    我的指令:"口腔溃疡好疼，吃饭都困难请帮我开药" 你输出:{"medicine": ["醋酸地塞米松口腔贴片"], "response": "贴片能缓解溃疡，少吃辛辣食物~"}
    我的指令:"头晕恶心，可能是中暑了请帮我开药" 你输出:{"medicine": ["藿香正气水"], "response": "喝点藿香正气水解暑，注意通风！"}
    我的指令:"我肚子疼，拉肚子请帮我开药" 你输出:{"medicine": [], "response": "暂时没有对症药品，建议服用蒙脱石散，注意饮食清淡哦！"}
    
    上面只是给出一些例子,具体针对哪种症状使用那些药品还需要你来判断
    我现在的指令是：
    
    '''
    message = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": PROMPT},
    ]

    API_BASE = "https://api.lingyiwanwu.com/v1"
    API_KEY = YI_KEY

    MODEL = 'yi-large'
    # MODEL = 'yi-medium'
    # MODEL = 'yi-spark'

    # 访问大模型API
    client = OpenAI(api_key=API_KEY, base_url=API_BASE)
    # completion = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": PROMPT}])
    # print(message)
    completion = client.chat.completions.create(model=MODEL, messages=message)
    result = completion.choices[0].message.content.strip()

    # 解析JSON字符串
    response_data = json.loads(result)

    # 提取medicine（Python列表）和response（字符串）
    medicine_list = response_data['medicine']  # 获取药品列表
    response_str = response_data['response']  # 获取回复文本

    #根据文字生成对应的wav文件
    tts(response_str)

    #播放语音
    play_wav('temp/tts.wav')

    # 如果药品列表不为空，对每个药品调用函数
    if medicine_list:
        for medicine in medicine_list:
            # 调用函数，传入药品名称作为参数
            yolo_getmedicine(medicine)



    return result


#把药品信息加载到数据库中
def load_medicine():
    global global_results
    # 第一步：拍摄四次照片
    all_direction_view_shot()

    # 第二步：用YOLO识别图片并返回结果
    model_path = "asset/models/best.pt"
    image_path = "temp/yolo/"  # 注意：all_direction_view_shot()保存图片到temp/yolo/
    global_results = predict_to_json(model_path, image_path)
    
    with open("global_results.txt","w")as f:
        f.write(str(global_results))


#药品查询函数
def find_medicine_positions(chinese_name: str, global_results: list) -> list:
    """
    根据中文药品名称和全局检测结果，返回药品的位置和方向信息

    参数:
        chinese_name: 中文药品名称（如 '布洛芬'）
        global_results: predict_to_json() 返回的结果列表

    返回:
        匹配的药品信息列表，格式:
        [{
            "direction": 方向索引(int),
            "center_x": 中心X坐标(float),
            "center_y": 中心Y坐标(float)
        }, ...]
        如果未找到则返回空列表 []
    """
    if chinese_name not in MEDICINE_NAME_MAPPING:
        raise ValueError(f"未知药品名称: {chinese_name}")

    english_name = MEDICINE_NAME_MAPPING[chinese_name]
    found_positions = []

    for direction_data in global_results:
        direction = direction_data['direction']
        for detection in direction_data['detections']:
            if detection['class_name'] == english_name:
                found_positions.append({
                    "direction": direction,
                    "center_x": detection['center_x'],
                    "center_y": detection['center_y']
                })

    return found_positions




if __name__ == '__main__':
    yolo_getmedicine()
    time.sleep(3)
    yolo_getmedicine('布洛芬')
    time.sleep(3)
    yolo_getmedicine('阿莫西林胶囊')
    time.sleep(3)
    
