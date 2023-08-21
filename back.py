
import vk_api
import os
import wget
import yaml
from yaml.loader import SafeLoader
from telegraph import Telegraph
from time import sleep
from telebot import TeleBot 
from telebot.types import InputMediaPhoto

def log_error(error_message):
    try:
        with open('error.txt', 'a') as file:
            file.write(str(error_message) + '\n')
    except FileNotFoundError:
        with open('error.txt', 'w') as file:
            file.write(str(error_message) + '\n')

def photo_download(url, filename):
    try:
        filename= wget.download(url, filename)
        with open(filename, 'rb') as photo:
            photo = photo.read()
            return photo
    except Exception as e:
        print(e)
        os.system()

class Config():
    """
    Инициализация Конфига
    """
    def __init__(self, config_name="config.yml") -> None:
        self.config:dict = Config.load_conf(config_name)
        self.login:str = self.config['vk']["login"]
        self.password:str = self.config['vk']["password"]
        self.tgph_name:str = self.config["tgph"]["name"]
        self.tgph_token:str = self.config["tgph"]["token"]
        self.tg_bot:str = self.config["tg_bot"]
        self.badword:dict = self.config["badword"]
        self.group_ids:list = self.config["group_ids"]
        self.obj_groups:object = self.config['groups']
        self.group_instances:dict = {}
        for group in self.obj_groups:
            self.group_instances[group] = self.Group(self.config, group)

    class Group():
        def __init__(self, config, group_id):
            self.group_id = group_id
            self.last_post = config["groups"][group_id]["last_post"]
            self.channels = config["groups"][group_id]['channels']

        def mark_lastpost(group_id, post_id):
            conf = Config.load_conf(); print( group_id, "OldPost:\n ", conf['groups'][group_id]['last_post'])
            conf['groups'][group_id]['last_post'] = post_id
            print("NewPost:\n ", conf['groups'][group_id]['last_post'])
            Config.dumb_conf(data = conf)


    def load_conf(config_file:str='config.yml') -> dict:
        """
        ### Descriptions

        Загрузка Config файла, сохраняя его в переменную , как словарь
        
        Returns: 
        {{}}
        """
        with open(config_file) as f:
            data = yaml.load(f, SafeLoader)
            return data
    
    def dumb_conf(config_file:str='config.yml', data:object=None):
        """
        Перезапись Config файла, сохраняя словарь в файл
        """
        with open(config_file, 'w') as conf:
            yaml.dump(data, conf)      


class VkReq():
    """
    Технический класс подразделяющий в себе, всё, что нужно, чтобы сделать и рассортировать запрос wall.get
    
    Эстетики ради;3
    
    """
    def wall_get(vk:object, group_id) -> list:
        """
        #### Descriptions:
        Возвращает списком последние посты в виде объектов
        #### Returns:
        [{"text":"", "photos":["url"], "id":0}]
        """
        #Запрос в ВК
        resp = vk.wall.get(owner_id=group_id, count=15)['items']
        group_name=VkReq.public_name(vk=vk, group_id=group_id)
        print("vk.wall.get: ", group_name)
        
        
        last_post = Config().group_instances[group_id].last_post
        if type(last_post) != int:
            print(f"\n\n--Warning | 🐸 KWA:\n You don't write last post for {group_name}. \nIm do it, don't worry^^")
            last_post = 0
            Config.Group.mark_lastpost(group_id, last_post)

        posts_list=[]
        for post in resp:
            if not (post['id'] <= last_post):
                photos = VkReq.attachments(post, "photo")
                post_data = {"id": post['id'],"group": group_name,"photos": photos, "text": post['text']}
                posts_list.append(post_data)
        return posts_list[::-1]




    def auth(login, password):
        vk_sessions = vk_api.VkApi(login=login, password=password, captcha_handler=VkReq.captcha_handler, app_id=6121396, auth_handler=VkReq.auth_handler)
        vk_sessions.auth()
        VK = vk_sessions.get_api()
        return VK


    def auth_handler():
        """ При двухфакторной аутентификации вызывается эта функция.
        """

        # Код двухфакторной аутентификации
        key = input("Enter authentication code: ")
        # Если: True - сохранить, False - не сохранять.
        remember_device = True

        return key, remember_device

    def captcha_handler(captcha):
        key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
        # Пробуем снова отправить запрос с капчей
        return captcha.try_again(key)

    def public_name(vk:object, group_id):
        resp = vk.groups.getById(group_id=-group_id)
        name = resp[0]["screen_name"]
        return name
    
    def approve_req(vk:object, group_ids):
        for group in group_ids:
            print('Check Request to ',VkReq.public_name(vk=vk, group_id=-group))
            p = vk.groups.getRequests(group_id=group)
            items = p['items']
            if items != []:
                for ids in items:
                    p = vk.groups.approveRequest(group_id=group, user_id=ids)
                    print(f'ApproveRequest: {items}')

    def attachments(post, attach_type:str="photo"):
        """
        ### Descriptions      
        Возвращает список фотографий в посте
        #### Returns:
        ['url', 'url1']
        """
        attach = []
        for attachments in post['attachments']:
            if attachments['type'] == attach_type:
                match attach_type:
                    case "photo":
                        photo=attachments['photo']['sizes'][-1]['url']
                        attach.append(photo)
                    case "video":
                        owner_id=attachments['video']['owner_id']
                        video_id=attachments['video']['id']
                        video=f"https://vk.com/video{owner_id}_{video_id}"
                        attach.append(video)
        return attach


class TGHP():
    def tgph_auth(config):
        print("Auth in Telegraph:")
        TGPH = Telegraph()
        tgph_resp = TGPH.create_account(short_name=config['tgph']['name'])
        tgph_token = tgph_resp["access_token"]
        TGPH = Telegraph(tgph_token)
        config["tgph"]["token"] = tgph_token
        Config.dumb_conf(data=config)
        return TGPH 

    def telegraph_page(post, telegraph:Telegraph) -> str:
        """
        ### Descriptions

        Do Telegraph post

        ### Returns

        URL on Telegraph post

        """
        page = [] 
        text = {'tag': 'p','children': [post['text']]}
        
        title=post['text']
        title=title.split()[:3]
        title=' '.join(title)
        
        photos = [{'tag': 'img','attrs': {'src': photo_url}} for photo_url in post['photos']]
        page.append(text)
        
        for photo in photos:
            page.append(photo)
        response = telegraph.create_page(title=title, author_url=f"https://vk.com/{post['group']}", content=page)
        return response['url']

    def cut_text(text="TG_CUTTER TEXT\n"):
        lines = text.split("\n")
        short_text=lines[0]
        if len(lines[0]) >500:
            short_text = lines[0].split(" "); short_text= short_text[:25]; " ".join(short_text)
            if len(short_text)> 500:
                resp ="NOT CUT"
                return resp
            return short_text
        return short_text
    
def badword_clear(text:str):
    config=Config()
    print(config.badword)
    for word in config.badword:
        replace_word = config.badword[word]
        text= text.replace(word, replace_word)
    return text

def TgRepost(tg:TeleBot, vk:vk_api.VkApi.get_api, tgph:Telegraph, links:dict):
    def tg_photo(post, text):
        media=[]; r=1
        for photo_url in post['photos']:
            filename=f"photos/{r}.png"
            photo = photo_download(photo_url, filename)
            if r == 1:
                media.append((InputMediaPhoto(photo, text)))
            else:
                media.append((InputMediaPhoto(photo)))
            r=r+1
        return media

    for group in links.keys():
        for channel in links[group]['channels']:
            posts_list = VkReq.wall_get(vk=vk, group_id=group)
            if posts_list != []:
                for post in posts_list:
                    text = badword_clear(post['text']); media=tg_photo(post=post, text=text); id=post['id']
                    print("Post ",id,":\n", text)
                    if len(text) > 1000:
                        text_short=TGHP.cut_text(text)
                        if  text_short == "NOT CUT":
                            text_short = ""
                        print("Text in post is too long. Posting in telegraph /.__./")
                        page_tghp=TGHP.telegraph_page(post=post, telegraph=tgph)
                        text_short = str(text_short) + "\n" + str(page_tghp)
                        print(text_short)
                        tg.send_message(chat_id=channel, text=text_short)
                    else:
                        if media !=[]:
                            print("tg.send_media ", channel)
                            tg.send_media_group(chat_id=channel, media=media)
                        else:
                            print("tg.send_message ", channel)
                            tg.send_message(chat_id=channel, text=text)
                    Config.Group.mark_lastpost(group, id); sleep(10)
                    
            else:
                print("No new posts in ", VkReq.public_name(vk=vk, group_id=group), "| 🐸 Kwa")     