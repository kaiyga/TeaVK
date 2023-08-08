from back import *

#Load Config
config = Config("config.yml")
# Auth
try:
    os.makedirs("photos", exist_ok=True)
    TG = TeleBot(config.tg_bot, "HTML")
    VK = VkReq.auth(config.login, config.password)
    TGPH = Telegraph(config.tgph_token) if config.tgph_token != "" else TGHP.tgph_auth(config=config)
except vk_api.AuthError as error_msg:
    print(error_msg)


while True:
    try:
        print("Checking")
        VkReq.approve_req(vk=VK, group_ids=config.config['group_ids'])
        TgRepost(tg=TG, vk=VK, tgph=TGPH, links=config.obj_groups)
        sleep(1200)
    except Exception as e:
        log_error(e)
        print(e)
        sleep(1200)
