# |#############################|
# |By Gulyshalkash (GIT: kaiyga)|
# |#############################|

from back import *

print("Load Config... ")
config = Config('config.yml')
print("Login in services...")
bridge = Bridge(config)

while True:
    bridge.repost_task(config)
    