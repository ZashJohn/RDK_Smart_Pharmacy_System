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
GPIO.setwarnings(False)  # 不打印 warning 信息
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(20, 1)  # 关闭吸泵电磁阀


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
    mc.send_angles([0.87, (-50.44), 47.28, 0.35, (-0.43), (-0.26)], 70)
    time.sleep(1)
    for count in range(2):
        mc.send_angle(5, 30, 80)
        time.sleep(0.5)
        mc.send_angle(5, -30, 80)
        time.sleep(0.5)
    # mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    # time.sleep(1)
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(2)


def head_dance():
    # 跳舞
    mc.send_angles([0.87, (-50.44), 47.28, 0.35, (-0.43), (-0.26)], 70)
    time.sleep(1)
    for count in range(1):
        mc.send_angles([(-0.17), (-94.3), 118.91, (-39.9), 59.32, (-0.52)], 80)
        time.sleep(1.2)
        mc.send_angles([67.85, (-3.42), (-116.98), 106.52, 23.11, (-0.52)], 80)
        time.sleep(1.7)
        mc.send_angles([(-38.14), (-115.04), 116.63, 69.69, 3.25, (-11.6)], 80)
        time.sleep(1.7)
        mc.send_angles([2.72, (-26.19), 140.27, (-110.74), (-6.15), (-11.25)], 80)
        time.sleep(1)
        mc.send_angles([0, 0, 0, 0, 0, 0], 80)


def head_nod():
    # 点头
    mc.send_angles([0.87, (-50.44), 47.28, 0.35, (-0.43), (-0.26)], 70)
    for count in range(2):
        mc.send_angle(4, 13, 70)
        time.sleep(0.5)
        mc.send_angle(4, -20, 70)
        time.sleep(1)
        mc.send_angle(4, 13, 70)
        time.sleep(0.5)
    mc.send_angles([0.87, (-50.44), 47.28, 0.35, (-0.43), (-0.26)], 70)


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

    # 初始化摄像头（放在循环外避免重复开关）
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("摄像头无法打开！")

    try:
        for i in range(4):
            # 控制机械臂旋转（假设mc已定义）
            mc.send_angles([-62.22 + i * 90, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
            time.sleep(4)  # 等待机械臂稳定

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
    cv2.destroyAllWindows()  # 关闭所有opencv窗口
    cv2.imshow('xingqi', img_bgr)
    if check:
        print('请确认拍照成功，按c键继续，按q键退出')
        while (True):
            key = cv2.waitKey(10) & 0xFF
            if key == ord('c'):  # 按c键继续
                break
            if key == ord('q'):  # 按q键退出
                # exit()
                cv2.destroyAllWindows()  # 关闭所有opencv窗口
                raise NameError('按q退出')
    else:
        if cv2.waitKey(10) & 0xFF == None:
            pass

    # 关闭摄像头
    cap.release()
    # 关闭图像窗口
    # cv2.destroyAllWindows()


def eye2hand(X_im=160, Y_im=120):
    '''
    输入目标点在图像中的像素坐标，转换为机械臂坐标
    '''

    # 整理两个标定点的坐标
    cali_1_mc = [-12.1, -244.9]  # 左下角，第一个标定点的机械臂坐标，要手动填！
    cali_1_im = [130, 433]  # 右上角，第二个标定点的像素坐标
    cali_2_mc = [75.3, -183.2]  # 右上角，第二个标定点的机械臂坐标，要手动填！
    cali_2_im = [366, 256]  # 左下角，第一个标定点的像素坐标，要手动填！

    X_cali_im = [cali_1_im[0], cali_2_im[0]]  # 像素坐标
    X_cali_mc = [cali_1_mc[0], cali_2_mc[0]]  # 机械臂坐标
    Y_cali_im = [cali_2_im[1], cali_1_im[1]]  # 像素坐标，先小后大
    Y_cali_mc = [cali_2_mc[1], cali_1_mc[1]]  # 机械臂坐标，先大后小

    # X差值
    X_mc = int(np.interp(X_im, X_cali_im, X_cali_mc))

    # Y差值
    Y_mc = int(np.interp(Y_im, Y_cali_im, Y_cali_mc))

    return X_mc, Y_mc


if __name__ == '__main__':
    direction=3
    if (direction == 0):
        mc.send_angles([-100, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
    elif (direction == 1):
        mc.send_angles([-40, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
    elif (direction == 2):
        mc.send_angles([60, -1.84, -84.99, -3.86, -2.37, 73.21], 30)
    elif (direction == 3):
        mc.send_angles([120, -1.84, -84.99, -3.86, -2.37, 73.21], 30)

    time.sleep(3)


