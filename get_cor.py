from pymycobot.mycobot import MyCobot
mc=MyCobot('/dev/ttyAMA0',1000000)
print(mc.get_coords())
