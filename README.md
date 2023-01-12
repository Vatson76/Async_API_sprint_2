# Проектная работа

Ссылка на проект: https://github.com/Vatson76/Async_API_sprint_2

## Как запустить проект:
Создайте env файл в той же директории, где описан его example файл

Запустите docker-compose командой:
```
docker-compose up -d
```
Создайте миграции и соберите статику командой:
```
make setup
```
Загрузите первоначальные данные из sqlite в postgres командой. После этого сработает сервис ETL
(Данные необходимо занести за 10 минут, иначе сервис ETL умрет (т.к. получит критическое кол-во ошибок для работы))
на загрузку в ElasticSearch:
```
make load_data
```
Создайте суперпользователя Django:
```
make admin
```
Команда для подключения к серверу redis:
```
make redis
```
## Запуск в браузере
- Открытие административного сайта - http://127.0.0.1:80/admin/
- Api - http://127.0.0.1:80/api/v1/
- Страница с документацией http://127.0.0.1:80/api/openapi
- Путь к сервису авторизации http://127.0.0.1:80/auth

## Запуск тестов
Перейдите в папку fastapi_solution/tests/functional и выполните команду docker-compose up -d


### Над проектом работали:

https://github.com/Vatson76 - тимлид

- Функциональные тесты. film
- Функциональные тесты. search
- SOLID
- Reviews

https://github.com/valerycode

- Функциональные тесты. person
- Функциональные тесты. genre
- SOLID
- Reviews

https://github.com/KaterinaSolovyeva (Закончила обучение)


Все задачи перенесены в issues и закрыты
