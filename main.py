# |#############################|
# |By Gulyshalkash (GIT: kaiyga)|
# |#############################|

from newback import *
from time import sleep
print("Load Config... ")
print("Login in services...")
bridge = Bridge("config.yml")

while True:
    try:
        bridge.repost_task()
        sleep(1200)
    except Exception as e:     
        print(e)   
        log_error(e)
        sleep(4800)