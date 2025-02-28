# habit_tracking_chatbot
Чат-бот для трекинга привычек (Telegram)

### Запуск бота
1) Сформировать на основании .env.example файл .env
- BOT_TOKEN - секретный токен Telegram-бота
- SECRET_PYJWT_ACCESS_KEY - секретный токен для генерации access-токена (любая строка)
- SECRET_PYJWT_REFRESH_KEY - секретный токен для генерации refresh-токена (любая строка)
- HOST - адрес сервера на котором разворачивается проект
2) Так как бот взаимодействует с Telegram через webhook, нужно установить SSL-сертификат на сервер. 
Для локального тестирования можно воспользоваться vk-tunnel
```shell
yarn vk-tunnel --insecure=1 --http-protocol=http --ws-protocol=ws --host=localhost --port=8000 --timeout=5000
```
3) Запуск через docker-compose
```shell
docker-compose up
```
4) Применение миграций через alembic
```shell
docker-compose exec app alembic upgrade head
```

### Запуск линтеров
1) black
```shell
black -l 120 -S --diff --check ./app
```
2) isort
```shell
isort --profile black --check-only --diff ./app
```
3) flake8
```shell
flake8 ./app
```