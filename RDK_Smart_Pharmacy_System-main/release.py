from pymycobot import MyCobot
import time

# MyCobot280 类初始化需要两个参数：

# 初始化一个MyCobot280对象
# 这里为 PI版本创建对象代码
mc = MyCobot("/dev/ttyAMA0", 1000000)



# 让机械臂放松，可以手动摆动机械臂
mc.release_all_servos()
