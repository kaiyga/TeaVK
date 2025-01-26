import vk_api
import os
import re
import yaml
from telegraph import Telegraph
from time import sleep
from telebot import TeleBot 
from telebot.types import InputMediaPhoto
import requests

RATE_LIMIT_SEC = 10

def log_error(error_message):
    try:
        with open('error.txt', 'a') as file:
            file.write(str(error_message) + '\n')
    except FileNotFoundError:
        with open('error.txt', 'w') as file:
            file.write(str(error_message) + '\n')

class Config:
    """
    Object for consistent state of config
    """
    def __init__(self, file):
        self.file = file
        self.config:dict = self.load()
         
    def reload_config(self):
        self.__init__(self.file)
    
    def load(self, file="config.yml") -> dict:
        with open(str(file), 'r') as f:
            data:dict = yaml.safe_load(f)
            return data
        
    def dumb(self, data):
        with open(self.file, 'w') as f:
            yaml.safe_dump(data, f)
        self.reload_config()
        
class BridgeConfig(Config):
    def __init__(self, file):
        super().__init__(file)
    
    def mark_lastpost(self, group_id, last_post):
        self.config['groups'][group_id]["last_post"] = last_post
        self.dumb(self.config) 

class Post():
    """
    Form for post object
    """
    # Унифицированная форма, чтобы не думать, как выглядит мой объект
    # Абсолютно не ООПшно и императивно
    
    # T___T По хорошему, тут написать, что-то типо postService
    # Принимает репозитории и сам себя постит, но я просто чищу код
    
    def __init__(self, id, group, group_id, text, photos):
        self.id = id
        self.group_id = group_id
        self.group = group
        self.text:str = text
        self.photos:list[str] = photos
        
        self.skip = False
        self.clear_text = ""
        
    def cut_text(self):
        lines = self.text.split("\n")
        short_text=lines[0]
        
        if len(short_text) > 500:
            split = lines[0].split(" ")
            
            short_text = " ".join(split[:25])
            
            if len(short_text) > 500:
                short_text = split[:15]
            
            if len(short_text) > 500:
                short_text = split[:10]
            
            if len(short_text) > 500:
                short_text = ""
                    
        return short_text

    def badword_clear(self, badwords:dict):
        for word in badwords:
            replace_word = badwords[word]
            text = self.text.replace(word, replace_word)
        self.clear_text = text

    def redflag(self, redflags:dict[str]):
        words = re.findall(r'\b\w+\b', self.text.lower()) 
        for word in words:
            if word in redflags:
                self.skip = True
                return        
        

class Bridge():
    def __init__(self, config_file):
        cf = BridgeConfig(config_file)
        self.config = cf
        
        redflags = []

        try:
            redflags = cf.config['redflags']
        except KeyError:
            pass
        
        self.redflags = map(str.lower, redflags)
        
        self.vk = VKClient(**cf.config.get('vk'))
        
        self.tg = TeleBot(cf.config.get('tg_bot')) 
        
        if not cf.config.get("tgph").get("token"):
            tgphT = TGPHClient.get_token(cf.config.get("tgph").get("name"))
            cf.config['tgph']['token'] = tgphT
            cf.dumb(cf.config)
        else:
            tgphT = cf.config.get("tgph").get("token")
            
        self.tgph = TGPHClient(tgphT)
        
    def repost_task(self):
        groups = self.config.config['groups']
        
        for group in list(groups.keys()):
            if not groups[group]['last_post']:
                last_post = 0
                self.config.config['groups'][group]['last_post'] = last_post
                self.config.dumb(self.config.config)
            else:
                last_post = self.config.config['groups'][group]['last_post']
                
            posts = self.vk.wall_get(group, last_post)
            
            for post in posts:
                post.redflag(self.redflags)
                post.badword_clear(self.config.config['badword'])
                for channel_id in groups[group]['channels']:
                    self._repost(channel_id, post)
                
    
    def _repost(self, channel_id, post:Post):
        
        if post.skip:
            return
        
        print(f"https://vk.com/wall{post.group_id}_{post.id}")
        
        media = []
        for i, photo in enumerate(post.photos, 0):
            s = requests.get(photo, allow_redirects=True)
            if i != 0:
                media.append(InputMediaPhoto(s.content))
            else:
                media.append(InputMediaPhoto(s.content, post.clear_text))
     
        if post.text or media != []:
            if len(post.text) > 1000:
                tghp_page = self.tgph.telegraph_page(post)
                text = str(post.cut_text()) + "\n" + str(tghp_page)
                self.tg.send_message(chat_id=channel_id, text=post.clear_text)
            else:
                if media != []:
                    print("TG Send media", channel_id)
                    self.tg.send_media_group(chat_id=channel_id, media=media)
                else:
                    print("TG Send text")
                    self.tg.send_message(channel_id, text=post.clear_text)
                    
        self.config.mark_lastpost(post.group_id, post.id); sleep(RATE_LIMIT_SEC)

class VKClient():
    def __init__(self, login="", password="", token=""):
        if token:
            vk_sessions = vk_api.VkApi(token=token)
            self.vk_client = vk_sessions.get_api()
        elif login and password:
            vk_sessions = vk_api.VkApi(login=login, password=password, captcha_handler=self.captcha_handler, app_id=6121396, auth_handler=self.auth_handler)
            vk_sessions.auth()
            self.vk_client = vk_sessions.get_api()
        else:
            raise RuntimeError("Not have credatials for login in VK. Please edit it!\nhttps://github.com/kaiyga/TeaVK/wiki/1.-%5B%F0%9F%94%A7-%7C-Configure%5D")

    def auth_handler(self):
        key = input("2FA REQUARED! Enter authentication code: ")
        remember_device = True

        return key, remember_device

    def captcha_handler(captcha):
        print("Need send capcha code:")
        key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
        # Пробуем снова отправить запрос с капчей
        return captcha.try_again(key)

    def public_name(self, group_id):
        resp = self.vk_client.groups.getById(group_id=-group_id)
        name = resp[0]["screen_name"]
        return name

    def wall_get(self, group_id, last_post) -> list[Post]:
        """
        #### Descriptions:
        Возвращает списком последние посты в виде объектов
        #### Returns:
        [{"text":"", "photos":["url"], "id":0}]
        """
        #Запрос в ВК
        resp = self.vk_client.wall.get(owner_id=group_id, count=15)['items']
        with open('resp.json', "w") as f:
            import json
            json.dump(resp, f)
        
        
        group_name=self.public_name(group_id=group_id)
        print("Get Wall from ", group_name)

        posts_list=[]
        for post in resp:
            if not (post['id'] <= last_post):
                photos = self.attachments(post, "photo")
                
                # post_data = {"id": post['id'], "group": group_name,"photos": photos, "text": post['text']}
                post_data = Post(post['id'], group_name, group_id, text=post['text'], photos=photos)
                posts_list.append(post_data)
        return posts_list[::-1]

    def attachments(self, post, attach_type:str="photo"):
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
                        def get_size(att):
                            # Получаем фото с самой большой площадью
                            return att['height'] * att['width']
                        atts = sorted(attachments['photo']['sizes'], key=get_size)#[-1]['url']
                        attach.append(atts[-1]['url'])

                    case "video":
                        # Оно походу умрёт вместе с кодом, либо я когда-нибудь напишу скачивание видео с ВК...
                        # Но вообще, это невозможно, самый большой размер, который позволяет отпрваить  Telegram 50 мб. КВА
                        owner_id=attachments['video']['owner_id']
                        video_id=attachments['video']['id']
                        video=f"https://vk.com/video{owner_id}_{video_id}"
                        attach.append(video)
        return attach


class TGPHClient():
    def __init__(self, token):
        self.tgph = Telegraph(token)
    
    @classmethod
    def get_token(cls, name):
        print("Auth in Telegraph:")
        TGPH = Telegraph()
        tgph_resp = TGPH.create_account(short_name=name)
        return tgph_resp["access_token"]


    def telegraph_page(self, post:Post) -> str:
        """
        ### Descriptions

        Do Telegraph post

        ### Returns

        URL on Telegraph post

        """
        page = [] 
        text = {'tag': 'p','children': [post.text]}
        
        title=post.text
        title=title.split()[:3]
        title=' '.join(title)
        
        photos = [{'tag': 'img','attrs': {'src': photo_url}} for photo_url in post.photos]
        page.append(text)
        
        for photo in photos:
            page.append(photo)
        response = self.tgph.create_page(title=title, author_url=f"https://vk.com/{post.group}", content=page)
        return response['url']
        