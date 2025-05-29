# Legal AI Backend

Бэкенд для веб-приложения юридического ИИ-ассистента. Реализован на Django и Django REST Framework. Предоставляет API для регистрации, авторизации, работы с чатами, файлами, шаблонами документов, платежами и профилем пользователя.

## 🎞️ Установка

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/yourusername/legal-ai-backend.git
cd legal-ai-backend
```

### 2. Создайте и активируйте виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # для Windows: venv\Scripts\activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения

Создайте файл `.env` и добавьте туда настройки:

```
DEBUG=True
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGIN_WHITELIST=http://localhost:3000

POSTGRES_DB=legal_ai
POSTGRES_USER=legaluser
POSTGRES_PASSWORD=securepassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

OPENAI_API_KEY=your_openai_api_key
```

### 5. Примените миграции

```bash
python manage.py migrate
```

### 6. Запустите сервер разработки

```bash
python manage.py runserver
```

## ⚙️ Основные компоненты

| Приложение  | Назначение                             |
| ----------- | -------------------------------------- |
| `users`     | Регистрация, JWT-авторизация, профиль  |
| `chat`      | Работа с диалогами, сообщениями, ИИ    |
| `documents` | Документы, шаблоны, генерация PDF      |
| `payments`  | Пополнение баланса, операции           |
| `files`     | Хранение и доступ к загруженным файлам |

## 🔐 Авторизация

Используется JWT (djangorestframework-simplejwt).

* Авторизация через `POST /api/token/`
* Обновление токена через `POST /api/token/refresh/`
* Все приватные эндпоинты требуют заголовка:

```
Authorization: Bearer <access_token>
```

## 📂 Структура проекта

```
legal_ai/
├── users/            # Пользователи и профили
├── chat/             # Сообщения, диалоги, OpenAI
├── documents/        # Шаблоны и документы
├── files/            # Загрузка и хранение файлов
├── payments/         # Работа с оплатами и балансом
├── core/             # Настройки проекта
└── manage.py
```

## 🧪 Примеры API

* Получить профиль:

```
GET /api/userprofile/
Authorization: Bearer <token>
```

* Отправить сообщение в чат:

```
POST /api/messages/
{
  "dialog_id": 1,
  "text": "Что делать при увольнении по собственному желанию?"
}
```

* Загрузить файл:

```
POST /api/files/
Content-Type: multipart/form-data
```

## 📌 Дополнительно

* Все файлы хранятся в `chat_files/`
* CORS включен для фронтенда (`localhost:3000`)
* Поддержка OpenAI GPT-4o в `chat.views.send_message`

## 📜 Лицензия

MIT License. Используйте и дорабатывайте свободно.
