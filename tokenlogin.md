**Как получить токен**

В первую очередь надо пройти авторизацию в [приложении, чтобы вы получили ваш токен](https://oauth.vk.com/authorize?client_id=6121396&scope=1073737727&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1). 

```
https://oauth.vk.com/authorize?client_id=6121396&scope=1073737727&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1

# Ссылка
https://oauth.vk.com/authorize

# Приложение 
?client_id=6121396

# Точка перенаправления
&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1
```

Оно от ВК, оно редиректит в ВК и не перенапрвляет вас и ваш токен куда-бы оно ни было

По окончанию авторизации вы останетесь на пустом бланке, где будет сказано, что ссылку и токен в опасные места не сувать

Прошу заранее ознакомится со [скриптом](./getToken.py) и осознать, что эти 5 строк лишь выделяют ваш токен, так как это нужно и возвращают его в консоль.

```
python getToken.py ВАШ_URL
```

В дальнейшем ваш токен можно использовать в конфиге

```yaml
vk:
    login:
    password:
    token: TOKEN 
```


