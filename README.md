# Delivery: Fast&Smart
Проект первокурсников ВШЭ СПБ ПАДИИ. Мы реализуем приложение для курьеров, агрегаторов и частных лиц, которое будет посредником между заказчиком и курьером. Из фичей - аукционные заказы.

## Содержание
- [Технологии](#технологии)
- [Использование](#использование)
- [FAQ](#faq)
- [[#To do]]
- [[#Команда проекта]]

## Технологии
- Kivy
- plyer
- SQlite3
- FastAPI
- RSA

## Использование
Загрузите все пакеты из requirements.txt:
```
pip3.12 install -r requirements.txt
```
Для запуска сервера (из директории server):
```
python3.12 server.py
```
Само приложение (из директории 2024-HSE-Project):
```
python3.12 src/main.py
```

## FAQ 
### Зачем вы разработали этот проект?
Командный опыт написания проекта, работа с git, ну и закрыть первый курс...

### Почему выбрали тот или иной фрейм?
Понятная документация или требование кого-то из кураторов/менторов/комиссии.

## To do
- [ ] Сделать нормальный дизайн
- [ ] Отрефакторить код, хочется больше readability
- [ ] Пофиксить баги с вылетами
- [ ] Интегрировать карту Яндекса

## Команда проекта
- [Артемий Афоничев](https://t.me/id2705) — Front-End, связь с Back-End
- [Игорь Бердов](https://t.me/whuliss) — Front-End, тестирование
- [Даниил Долгих](https://t.me/d1e_for_it) — Серверная часть, БД
Указаны только основные задачи, были и дополнительные, список которых можно восстановить по коммитам.