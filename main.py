# |#############################|
# |By Gulyshalkash (GIT: kaiyga)|
# |#############################|

from newback import *
from time import sleep
print("Load Config... ")
config = Config('config.yml')
print("Login in services...")
bridge = Bridge(config)

while True:
    try:
        bridge.repost_task(config)
        sleep(1200)
    except Exception as e:     
        print(e)   
        log_error(e)
        sleep(4800)