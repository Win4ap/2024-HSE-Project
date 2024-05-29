# Delivery: Fast&Smart
Проект первокурсников ВШЭ СПБ ПАДИИ. Мы реализуем приложение для курьеров, агрегаторов и частных лиц, которое будет посредником между заказчиком и курьером. Из фичей - аукционные заказы.

## Содержание
- [Технологии](#технологии)
- [Использование](#использование)
- [FAQ](#faq)
- [To do](#to-do)
- [Команда проекта](#команда-проекта)

## Технологии
- Kivy
- plyer
- SQlite3
- FastAPI
- RSA

## Использование
### Локально
Загрузите все пакеты из requirements.txt:
```sh
pip3.12 install -r requirements.txt
pip3.12 install python-multipart
pip3.12 install pysqlite3
```
Для запуска сервера локально (из директории server):
```sh
python3.12 server.py
```
Само приложение (из директории 2024-HSE-Project):
```sh
python3.12 src/main.py
```

### В облаке (на примере Ubuntu 22.04)
Создайте докер-образ, предварительно поменяйте IP в server/constants.py на 0.0.0.0:
```sh
docker build -t dfs .
```
Запустите докер-контейнер:
```sh
docker run -itd -p YOUR-PUBLIC-IP:1233:1233 dfs
```
Проверить статус контейнера:
```sh
docker ps
```

Автоматизация перезапуска контейнера:
```sh
nano /etc/systemd/system/dfs.service
```
В файл запишите следующие строки, не забудьте поменять CONTAINER-ID, можете его найти там же, где проверяли статус контейнера:
```
[Unit]
Description=SOMETHING
Requires=docker.service
After=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker start -a CONTAINER-ID
ExecStop=/usr/bin/docker stop CONTAINER-ID
TimeoutSec=5

[Install]
WantedBy=multi-user.target
```
Перезапустите демон и включите автозагрузку следующими командами:
```sh
systemctl daemon-reload
systemctl start dfs.service
systemctl enable dfs.service
```
Проверить состояние скрипта и логи сервера можете командой:
```sh
systemctl status dfs.service
```

## FAQ 
### Зачем вы разработали этот проект?
Командный опыт написания проекта, работа с git, ну и закрыть первый курс...

### Почему выбрали тот или иной фрейм?
Понятная документация или требование кого-то из кураторов/менторов/комиссии.

## To do
- Cделать нормальный дизайн
- Отрефакторить код, хочется больше readability

## Команда проекта
- [Артемий Афоничев](https://t.me/id2705) — Front-End, связь с Back-End
- [Игорь Бердов](https://t.me/whuliss) — Front-End, тестирование
- [Даниил Долгих](https://t.me/d1e_for_it) — Серверная часть, БД

Указаны только основные задачи, были и дополнительные, список которых можно восстановить по коммитам.