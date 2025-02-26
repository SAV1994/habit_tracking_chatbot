# habit_tracking_chatbot
Чат-бот для трекинга привычек (Telegram)


#### Запуск линтеров
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