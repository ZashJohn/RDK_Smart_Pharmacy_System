# utils_robot.py
# 启动并连接机械臂，导入各种工具包

print('导入机械臂连接模块')

from pymycobot.mycobot import MyCobot
from pymycobot import PI_PORT, PI_BAUD
import cv2
import numpy as np
import time
from utils_pump import *

# 连接机械臂
mc = MyCobot(PI_PORT, PI_BAUD)
# 设置运动模式为插补
mc.set_fresh_mode(0)

import RPi.GPIO as GPIO
# 初始化GPIO
GPIO.setwarnings(False)   # 不打印 warning 信息
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(20, 1)        # 关闭吸泵电磁阀

def back_zero():
    '''
    机械臂归零
    '''
    print('机械臂归零')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)

def relax_arms():
    print('放松机械臂关节')
    mc.release_all_servos()

def head_shake():
    # 左右摆头
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    time.sleep(1)
    for count in range(2):
        mc.send_angle(5, 30, 80)
        time.sleep(0.5)
        mc.send_angle(5, -30,80)
        time.sleep(0.5)
    # mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    # time.sleep(1)
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(2)

def head_dance():
    # 跳舞
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    time.sleep(1)
    for count in range(1):
        mc.send_angles([(-0.17),(-94.3),118.91,(-39.9),59.32,(-0.52)],80)
        time.sleep(1.2)
        mc.send_angles([67.85,(-3.42),(-116.98),106.52,23.11,(-0.52)],80)
        time.sleep(1.7)
        mc.send_angles([(-38.14),(-115.04),116.63,69.69,3.25,(-11.6)],80)
        time.sleep(1.7)
        mc.send_angles([2.72,(-26.19),140.27,(-110.74),(-6.15),(-11.25)],80)
        time.sleep(1)
        mc.send_angles([0,0,0,0,0,0],80)

def head_nod():
    # 点头
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    for count in range(2):
        mc.send_angle(4, 13, 70)
        time.sleep(0.5)
        mc.send_angle(4, -20, 70)
        time.sleep(1)
        mc.send_angle(4,13,70)
        time.sleep(0.5)
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)

def move_to_coords(X=150, Y=-130, HEIGHT_SAFE=230):
    print('移动至指定坐标：X {} Y {} HEIGHT_SAFE {}'.format(X, Y))
    mc.send_coords([X, Y, HEIGHT_SAFE, 0, 180, 90], 20, 0)
    time.sleep(4)

def single_joint_move(joint_index, angle):
    print('关节 {} 旋转至 {} 度'.format(joint_index, angle))
    mc.send_angle(joint_index, angle, 40)
    time.sleep(2)

def move_to_top_view():
    print('移动至俯视姿态')
    mc.send_angles([-62.22, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
    time.sleep(3)


def all_direction_view_shot(check=False):
    """
    移动机械臂到俯视姿态，并拍摄4个3方向的图片
    :param check: 是否手动确认每张照片（按'c'继续，按'q'退出）
    """
    print('移动至俯视姿态，并拍摄周围图片')

    

    try:
        for i in range(4):
            # 控制机械臂旋转（假设mc已定义）
            if (i == 0):
                mc.send_angles([-100, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
            elif (i == 1):
                mc.send_angles([-40, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
            elif (i == 2):
                mc.send_angles([60, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
            elif (i == 3):
                mc.send_angles([120, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
            
            time.sleep(6)  # 等待机械臂稳定
            time.sleep(2)  # 等待机械臂稳定
            
            # 初始化摄像头（放在循环外避免重复开关）
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise RuntimeError("摄像头无法打开！")

            # 捕获图像
            success, img_bgr = cap.read()
            if not success:
                print(f"警告：第 {i} 次拍摄失败！")
                continue

            # 保存图像
            save_path = f'temp/yolo/{i}.jpg'
            cv2.imwrite(save_path, img_bgr)
            print(f'图像已保存至: {save_path}')

            # 显示图像（可选）
            cv2.imshow('Preview', img_bgr)
            if check:
                print('按 "c" 继续，按 "q" 退出...')
                while True:
                    key = cv2.waitKey(10) & 0xFF
                    if key == ord('c'):
                        break
                    elif key == ord('q'):
                        raise KeyboardInterrupt('用户主动退出')
            else:
                cv2.waitKey(100)  # 短暂显示图像
                
            # 确保释放资源
            cap.release()
            cv2.destroyAllWindows()

        print('所有方向拍摄完成！')
    finally:
        # 确保释放资源
        cap.release()
        cv2.destroyAllWindows()

def top_view_shot(check=False):
    '''
    拍摄一张图片并保存
    check：是否需要人工看屏幕确认拍照成功，再在键盘上按q键确认继续
    '''
    print('    移动至俯视姿态')
    move_to_top_view()
    time.sleep(3)
    # 获取摄像头，传入0表示获取系统默认摄像头
    cap = cv2.VideoCapture(0)
    # 打开cap
    cap.open(0)
    time.sleep(0.3)
    success, img_bgr = cap.read()
    
    # 保存图像
    print('    保存至temp/vl_now.jpg')
    cv2.imwrite('temp/vl_now.jpg', img_bgr)

    # 屏幕上展示图像
    cv2.destroyAllWindows()   # 关闭所有opencv窗口
    cv2.imshow('xingqi', img_bgr)
    if check:
        print('请确认拍照成功，按c键继续，按q键退出')
        while(True):
            key = cv2.waitKey(10) & 0xFF
            if key == ord('c'): # 按c键继续
                break
            if key == ord('q'): # 按q键退出
                # exit()
                cv2.destroyAllWindows()   # 关闭所有opencv窗口
                raise NameError('按q退出')
    else:
        if cv2.waitKey(10) & 0xFF == None:
            pass
        
    # 关闭摄像头
    cap.release()
    # 关闭图像窗口
    # cv2.destroyAllWindows()

def rotate_point_degrees(x, y, a_degrees):
    """绕原点旋转点 (x, y) 逆时针角度 a_degrees（角度制）"""
    a_rad = np.deg2rad(a_degrees)  # 角度转弧度
    x_new = x * np.cos(a_rad) - y * np.sin(a_rad)
    y_new = x * np.sin(a_rad) + y * np.cos(a_rad)
    return x_new, y_new

def normal_equation_multi_output(X, Y):
    """多维输出的正规方程"""
    # 在 X 左侧添加一列 1（用于偏置项）
    X_b = np.c_[np.ones((X.shape[0], 1)), X]  # X_b 形状: (m, n+1)

    # 计算 W = (X_b^T X_b)^{-1} X_b^T Y
    XTX = X_b.T @ X_b
    XTX_inv = np.linalg.inv(XTX)
    W = XTX_inv @ X_b.T @ Y  # W 形状: (n+1, c)

    # 拆分权重和偏置
    b = W[0, :]  # 偏置 (1, c)
    W = W[1:, :]  # 权重 (n, c)

    return W, b


def eye2hand(X_im=160, Y_im=120,direction=2):
    #给出任意三个点的像素坐标和对应机械臂的坐标
    cali_1_im=[582,109]          #手动标记的数据
    cali_2_im=[381,111]
    cali_3_im=[47,362]

    cali_1_mc=[43.9,209.4]        #手动标记的数据
    cali_2_mc=[77.5,150]
    cali_3_mc=[193.8,85.1]

    X=np.array([cali_1_im,cali_2_im,cali_3_im])
    Y=np.array([cali_1_mc,cali_2_mc,cali_3_mc])

    W,b=normal_equation_multi_output(X,Y)
    print(W,b)

    Im_in=np.array([[X_im,Y_im]])

    result=Im_in @ W+b

    X_mc=int(result[0][0])
    Y_mc=int(result[0][1])

    if direction==2:
        X=X_mc
        Y=Y_mc
    elif direction==0:
        X,Y=rotate_point_degrees(X_mc,Y_mc,-160)
    elif direction==1:
        X,Y=rotate_point_degrees(X_mc,Y_mc,-100)
    elif direction==3:
        X,Y=rotate_point_degrees(X_mc, Y_mc, 60)

    X = int(X)
    Y = int(Y)

    return X,Y

# 吸泵吸取并移动物体
def pump_move(mc, XY_START=[230,-50], HEIGHT_START=65, XY_END=[100,220], HEIGHT_END=100, HEIGHT_SAFE=220):

    '''
    用吸泵，将物体从起点吸取移动至终点
    mc：机械臂实例
    XY_START：起点机械臂坐标
    HEIGHT_START：起点高度 90
    XY_END：终点机械臂坐标
    HEIGHT_END：终点高度
    HEIGHT_SAFE：搬运途中安全高度
    '''
    
    # 初始化GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)

    # 设置运动模式为插补
    mc.set_fresh_mode(0)
    
    # # 机械臂归零
    # print('    机械臂归零')
    # mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    # time.sleep(4)
    
    # 吸泵移动至物体上方
    print('    吸泵移动至物体上方')
    print(XY_START[0])
    print(XY_START[1])
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 20, 0)
    time.sleep(3)

    # 开启吸泵
    pump_on()
    
    # 吸泵向下吸取物体
    print('    吸泵向下吸取物体')
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_START, 0, 180, 90], 15, 0)
    time.sleep(3)

    # 升起物体
    print('    升起物体')
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(3)

    # 搬运物体至目标上方
    print('    搬运物体至目标上方')
    print(XY_END[0])
    print(XY_END[1])
    mc.send_coords([XY_END[0], XY_END[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(3)

    # 向下放下物体
    print('    向下放下物体')
    mc.send_coords([XY_END[0], XY_END[1], HEIGHT_END, 0, 180, 90], 20, 0)
    time.sleep(3)

    # 关闭吸泵
    pump_off()

    # 机械臂归零
    print('    机械臂归零')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)

def move_medicine(mc, XY_START=[230,-50], HEIGHT_START=65, XY_END=[267.1,-50.9], HEIGHT_SAFE=220):
    '''
    用吸泵，将药品吸取并移动至终点
    mc：机械臂实例
    XY_START：起点机械臂坐标
    HEIGHT_START：起点高度 90
    XY_END：终点机械臂坐标
    HEIGHT_END：终点高度
    HEIGHT_SAFE：搬运途中安全高度
    '''
    # 初始化GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)

    # 设置运动模式为插补
    mc.set_fresh_mode(0)

    # 吸泵移动至物体上方
    print('    吸泵移动至物体上方')
    print(XY_START[0])
    print(XY_START[1])
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 20, 0)
    time.sleep(3)

    # 开启吸泵
    pump_on()

    # 吸泵向下吸取物体
    print('    吸泵向下吸取物体')
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_START, 0, 180, 90], 15, 0)
    time.sleep(3)

    # 升起物体
    print('    升起物体')
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(3)



    # 搬运物体至目标上方
    print('    搬运物体至目标上方')
    print(XY_END[0])
    print(XY_END[1])
    mc.send_coords([XY_END[0], XY_END[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(3)



    # 关闭吸泵
    pump_off()

    # 机械臂归零
    print('    机械臂归零')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)

def pump_move_collision(mc, XY_START=[230,-50], HEIGHT_START=65, XY_END=[100,220], HEIGHT_END=100, HEIGHT_SAFE=220):

    '''
    用吸泵，将物体从起点吸取移动至终点

    mc：机械臂实例
    XY_START：起点机械臂坐标
    HEIGHT_START：起点高度
    XY_END：终点机械臂坐标
    HEIGHT_END：终点高度
    HEIGHT_SAFE：搬运途中安全高度
    '''
    
    # 初始化GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)

    # 设置运动模式为插补
    mc.set_fresh_mode(0)
    
    # # 机械臂归零
    # print('    机械臂归零')
    # mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    # time.sleep(4)
    
    # 吸泵移动至物体上方
    print('    吸泵移动至物体上方')
    print(XY_START[0])
    print(XY_START[1])
    mc.send_coords([XY_START[0]+58, XY_START[1]+40, HEIGHT_SAFE, 0, 180, 90], 10, 0)
    time.sleep(3)

    # 开启吸泵
    pump_on()
    
    # 吸泵向下吸取物体
    print('    吸泵向下吸取物体')
    mc.send_coords([XY_START[0]+58, XY_START[1]+40, HEIGHT_START, 0, 180, 90], 10, 0)
    time.sleep(3)

    # 升起物体
    print('    升起物体')
    mc.send_coords([XY_START[0]+58, XY_START[1]+40, HEIGHT_SAFE, 0, 180, 90], 10, 0)
    time.sleep(3)

    # 搬运物体至目标上方
    print('    搬运物体至目标上方')
    print(XY_END[0])
    print(XY_END[1])
    mc.send_coords([XY_END[0]-10, XY_END[1]+110, HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(3)

    # 向下放下物体
    print('    向下放下物体')
    mc.send_coords([XY_END[0]-10, XY_END[1]+110, HEIGHT_END, 0, 180, 90], 90, 0)
    time.sleep(5)


    # 向前移动进行撞击
    print('    向前移动进行撞击')
    mc.send_coords([XY_END[0]-10, XY_END[1], HEIGHT_END+50, 0, 180, 90], 90, 0)
    time.sleep(3)
    
    # 关闭吸泵
    pump_off()

    # 机械臂归零
    print('    机械臂归零')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)
