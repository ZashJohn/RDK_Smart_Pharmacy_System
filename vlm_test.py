from utils_vlm import *
# Yi-Vision调用函数
import openai
from openai import OpenAI
import base64
import cv2

result=yi_vision_api(PROMPT='帮我把红色卡片放在黄色五角星上面', img_path='temp/vl_now.jpg', vlm_option=0)
print(result)
post_processing_viz(result, img_path='temp/vl_now.jpg', check=False)