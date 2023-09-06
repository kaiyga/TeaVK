# |#############################|
# |By Gulyshalkash (GIT: kaiyga)|
# |#############################|
#UPD. Ты заглянул в Код. Это вторая версия исполнения оболочки моста. И здесь, пока, что не хватает комментариев к классам и функциям. 
#Рефакторинг зашёл далеко и я всё-же переписал всё на классах (Первые версии кода, были лишь робкой попыткой). Ибо так, мне кажется красивше:p
import vk_api
import os
import wget
import yaml
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

class Config:
    def __init__(self, config_file="config.yml") -> None:
        self.config_file = str(config_file)
        self.config:dict = Config.load_config(self.config_file)
        self.initTGHP()
        self.tg = self.config['tg_bot']
        self.vk = self.VK(self.config['vk'])
        self.badword = self.config['badword']
        self.groups = {}
        for group in list(self.config['groups'].keys()):
            print("Fonded Group:", group)
            self.groups[group]:self.Group = self.Group(group_id=group, group_dict=self.config['groups'][group])
    class Group:
        def __init__(self, group_id, group_dict) -> None:
            self.group_id:int = int(group_id)
            self.channels:list = group_dict['channels']
            self.last_post:int = group_dict['last_post']
        
    def mark_lastpost(self, group_id, last_post):
        self.last_post = last_post
        
        self.config['groups'][group_id]['last_post'] = last_post
        self.dumb_config(self.config)
            
    class VK:
        def __init__(self, vk_dict) -> None:
            self.login = vk_dict['login']
            self.password = vk_dict['password']

    class TGHP:
        def __init__(self, tghp_dict:dict) -> None:
            self.token = tghp_dict['token']
            self.name = tghp_dict['name']
                
    def initTGHP(self):
        self.tghp = self.TGHP(self.config['tgph'])  
        if self.config['tgph']['token'] == None or self.config['tgph']['token'] == "":
            print("Auth in Telegraph:")
            TGPH = Telegraph()
            tgph_resp = TGPH.create_account(short_name=self.tghp.name)
            self.tghp.token = tgph_resp["access_token"]
            self.config['tgph']['token'] = self.tghp.token
            self.dumb_config(self.config)       

    def reload_config(self):
        self.__init__(self.config_file)
    

    def test(self):
        print(self.config_file)

    def load_config(config_file="config.yml") -> dict:
        with open(str(config_file), 'r') as f:
            data:dict = yaml.safe_load(f)
            return data
        
    def dumb_config(self, data):
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(data, f)
        self.reload_config()

class Bridge:
    def __init__(self, config:Config) -> None:
            print("VK login...")
            self.vk = self.VkReq(config.vk)
            self.tg = TeleBot(config.tg)
            self.tghp = self.TGPH(config.tghp)
            self.groups = config.groups
            
    def repost_task (self, config:Config):
        for group in self.groups:
            gp = GroupPosts(group=self.groups[group], config=config, vk=self.vk, tg=self.tg, tgph=self.tghp) 
            gp.tg_reposts()




    class TGPH:
        def __init__(self, tghp_config:Config.TGHP) -> None:
            if tghp_config != None:
                self.tgph_ = Telegraph(tghp_config.token) 
            else:
                print("Auth in Telegraph:")
                TGPH = Telegraph()
                tgph_resp = TGPH.create_account(short_name=tghp_config.name)
                tgph_token = tgph_resp["access_token"]
                self.tgph_ = Telegraph(tgph_token)
                tghp_config.token = tgph_token
                self.update_tgph_token(tghp_config.token)

        def update_tgph_token(config, token):
            tghp_config = Config.load_config()
            tghp_config['tgph']['token']= token
            Config.dumb_config(tghp_config)


        def telegraph_page(self, post) -> str:
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
            response = self.tgph_.create_page(title=title, author_url=f"https://vk.com/{post['group']}", content=page)
            return response['url']

    class VkReq():
        def __init__(self, vk:Config.VK) -> None:
            vk_sessions = vk_api.VkApi(login=vk.login, password=vk.password, captcha_handler=self.captcha_handler, app_id=6121396, auth_handler=self.auth_handler)
            vk_sessions.auth()
            print("Success! Rest is easy^^")
            self.vk_ = vk_sessions.get_api()

        def auth_handler(self):
            """ При двухфакторной аутентификации вызывается эта функция.
            """

            # Код двухфакторной аутентификации
            key = input("2FA REQUARED! Enter authentication code: ")
            # Если: True - сохранить, False - не сохранять.
            remember_device = True

            return key, remember_device

        def captcha_handler(captcha):
            print("Need send capcha code:")
            key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
            # Пробуем снова отправить запрос с капчей
            return captcha.try_again(key)
        

        def public_name(self, group_id):
            resp = self.vk_.groups.getById(group_id=-group_id)
            name = resp[0]["screen_name"]
            return name

        def wall_get(self, group_id) -> list:
            """
            #### Descriptions:
            Возвращает списком последние посты в виде объектов
            #### Returns:
            [{"text":"", "photos":["url"], "id":0}]
            """
            #Запрос в ВК
            resp = self.vk_.wall.get(owner_id=group_id, count=15)['items']
            with open('resp.json', "w") as f:
                import json
                json.dump(resp, f)
                
            group_name=self.public_name(group_id=group_id)
            print("Get Wall from ", group_name)
        
            config = Config()
            last_post = config.groups[group_id].last_post
            if type(last_post) != int:
                print(f"\n\n--Warning | 🐸 KWA:\n You don't write last post for {group_name}. \nIm do it, don't worry^^")
                last_post = 0
                config.mark_lastpost(group_id=group_id, last_post=0)

            posts_list=[]
            for post in resp:
                if not (post['id'] <= last_post):
                    photos = Bridge.VkReq.attachments(post, "photo")
                    post_data = {"id": post['id'], "group": group_name,"photos": photos, "text": post['text']}
                    posts_list.append(post_data)
            return posts_list[::-1]

        def attachments(post, attach_type:str="photo"):
            """
            ### Descriptions      
            Возвращает список фотографий в посте
            #### Returns:
            ['url', 'url1']
            """
            attach = []
            for attachments in post['attachments']:
                try:
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
                except KeyError as e:
                    print("Post haven't ", attach_type, " | 🐸")
            return attach
        
        def approve_req(self):
            #   Эта функция не будет иметь широкой документации и сделана специально, для agwg_pub
            #   Принцип прост. Добавь объект groups = [-GroupID, -GroupID2]
            #   И оно будет в этих группах автоматически принимать заявки
            config = Config()
            try:
                group_ids= config.config['groups']
                for group in group_ids:
                    print('Check Request to ', self.public_name(group_id=group))
                    p = self.vk_.groups.getRequests(group_id=-group)
                    items = p['items']
                    if items != []:
                        for ids in items:
                            p = self.vk_.groups.approveRequest(group_id=-group, user_id=ids)
                            print(f'ApproveRequest: {ids}')
            except KeyError:
                print("approve not active")


class GroupPosts():
    def __init__ (self, group:Config.Group, config:Config, vk:Bridge.VkReq, tg:TeleBot, tgph:Bridge.TGPH) -> None:
        self.group = group
        self.vkposts = vk.wall_get(self.group.group_id)
        self.tg = tg
        self.tgph = tgph
        self.badword = config.badword
        self.config = config


    def tg_reposts(self):
        for channel in self.group.channels:
            if self.vkposts != []:
                for post in self.vkposts:
                    text=self.badword_clear(post['text']); media=self.tg_photo(post, text); id=post['id']
                    print(f"https://vk.com/wall{self.group.group_id}_{id}",)
                    if not (text == "" and media == []):
                        if len(text) > 1000:
                            short_text = self.cut_text(text)
                            if short_text == "NOT CUT":
                                short_text=""
                            print("Text in post is too long. Posting in telegraph /.__./")
                            page_tghp=self.tgph.telegraph_page(post=post)
                            text_short = str(text_short) + "\n" + str(page_tghp)
                            print(text_short)
                            self.tg.send_message(chat_id=channel, text=text_short)
                        else:
                            if media !=[]:
                                print("tg.send_media ", channel)
                                self.tg.send_media_group(chat_id=channel, media=media)
                            else:
                                print("tg.send_message ", channel)
                                self.tg.send_message(chat_id=channel, text=text)
                    self.config.mark_lastpost(self.group.group_id, id); sleep(10)



    def cut_text(self, text="TG_CUTTER TEXT\n"):
        lines = text.split("\n")
        short_text=lines[0]
        if len(lines[0]) >500:
            short_text = lines[0].split(" "); short_text= short_text[:25]; " ".join(short_text)
            if len(short_text)> 500:
                resp ="NOT CUT"
                return resp
            return short_text
        return short_text

    def badword_clear(self, text:str):
        for word in self.badword:
            replace_word = self.badword[word]
            text= text.replace(word, replace_word)
        return text

    def tg_photo(self, post, text):
        media=[]; r=1
        for photo_url in post['photos']:
            filename=f"photos/{r}.png"
            photo = self.photo_download(photo_url, filename)
            if r == 1:
                media.append((InputMediaPhoto(photo, text)))
            else:
                media.append((InputMediaPhoto(photo)))
            r=r+1
        return media
    
    def photo_download(self, url, filename):
        try:
            filename= wget.download(url, filename)
            with open(filename, 'rb') as photo:
                photo = photo.read()
                return photo
        except Exception as e:
            print(e)
            os.system('mkdir ./photos')



