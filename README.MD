<h1>TEA<a href="vk.com">VK</a> - VK to Telegram post retranslate</h1>

<h2>Авто-пост публикаций из VK в ТГ</h2>
<h1>Из фишек</h1>
<h3>

- Ретрансляция постов из ВК в Телеграм

- Возможность добавить бесконечно большое количество, как групп, так и каналов TG

- Сохранение особо крупных постов (1000 символов) в Telegraph

- TODO: Вытаскивать Видео? Музыку? 
</h3>


<h1>🔧 | Настройка</h1>
<h3>
Можете воспользоваться <a href="config_clear">Clear Config</a>, чтобы начать настройку бота.
</h3>

<h2> Объект group</h2>

<h3>Groups состоит из объектов group, именна которых прямо совпадают с Group-ID VK </h3>
<h3>

Group содержат в себе:
- last_post - ID Последнего поста
- channels - список ID TG-Каналов для репостов. Это может быть и просто Ваш ID, чтобы принимать сообщения в ЛС

</h3>
<h4>
Подобная структура позволяет, увеличивать или уменьшать колличество отслеживаемых групп и при этом контролировать отправку постов в разные каналы
</h4>

<img src="photos\group_data.png"></img>
<a href="https://t.me/getidsbot">Узнать ID TG</a>
```yaml
groups:
  -101010101: #Сюда ID VK Стены.
    channels: # Это список каналов.
    #Чёрточки перед TG-Channel обязательны! yaml-list!
    - -1011011011011 #TG-Channel один
    - -2021021021021 #TG-Channel Два, если нужно, можно убрать/добавить
    last_post: 144888

#Ваши Логин и пароль
vk:
  login: SUPER_LOGIN!
  password: SUPER_PASSWORD!
  tg_bot: 0101010101:yabototvetchauyblyabudu
#Здесь всё просходит автоматически, можете не менять
tgph:
  name: Name
  #Token получается автоматически 
  token: AUTO_CONFIGURE
```

<h1>Установка, запуск</h1>
<h3>Надеюсь у вас есть Python 3.10 и выше</h3>

```bash
pip install -r requirements.txt 
```
<h3>Start</h3>

```bash
python main.py 
```