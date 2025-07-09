from pymycobot.mycobot import MyCobot
from pymycobot import PI_PORT, PI_BAUD

# 连接机械臂
mc = MyCobot(PI_PORT, PI_BAUD)

# 设置运动模式为插补
mc.set_fresh_mode(0)

#get angles
list1=mc.get_angles()
print(list1)
