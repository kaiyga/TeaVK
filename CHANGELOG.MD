

TeaVK [0.2] Refactoring Update

Переделал заднюю исполнительную оболочку

  Таким образом, что мы используем один конфиг, благодаря которому, можно инициализировать "мост" (Бот-ретраснялтор)

  А основная функция ретрасляции инициализирует набор постов для каждой группы в конфиге

Вместе с тем элегантно изменился главный файл

Добавил тестовый конфиг Docker, который при сборке возьмёт ваш config.yml и будет продолжать работу уже с ним
  (TODO: Сделать Docker-compose (Пока не с руки)) by kaiyga


TeaVK [0.2.1] Timeouts, Error Loging

Добавил обработку ошибок и тайм-ауты


Bag Fix [0.2.2]
TeaVK [0.2.2] text and media is None FIX

Фикс проблемы с неподдерживаемые мною типы данных, которые вызывали отправку пустого сообщения (Что просто невозможно)
Тем самым вызывая ошибку в  TelegramAPI
И тормозя тем самым цикл.
Теперь при имении текста или медиа (Пока только фотографий)
Проверка проходит

TeaVK [0.2.3] BAG FIX : ACCESS_TOKEN_INVALID, auth_handler() takes 0 positional arguments

Исправлена проблема проверки и использования токена Telegraph

Исправлена проблема связанная с тем, что в auth_handler() передавался объект self

TeaVK [0.2.4] BAG FIX :<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:997)>

TeaVK [0.2.5] FIX CROP IMAGE | TELEGRAPH TITLE GEN

FIX CROP IMAGE | VK начали в API класть кропнутые изображения. Сделал сортировку на размер изображения. Увеличилось качество перепощенных изображений (Стоило в самом начале так делать)

FIX: cannot accses local varible "text_short" | Когда-то давно, я напартичил с неймингом и это вылилось в эту ошибку. В определении переменной использовал саму определяемую переменную