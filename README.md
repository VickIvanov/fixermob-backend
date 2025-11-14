# FixerMob Backend

Бэкенд для кросс-платформенного мобильного приложения "Протоколы осмотра".

## Установка и запуск

### 1. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Запуск сервера

```bash
python app.py
```

Сервер запустится на `http://localhost:5001`

## Структура проекта

```
fixermob-backend/
├── app.py                 # Основной файл приложения
├── requirements.txt       # Зависимости Python
├── API_DOCUMENTATION.md   # Документация API для мобильного приложения
├── README.md             # Этот файл
├── uploads/              # Загруженные файлы (создается автоматически)
│   ├── videos/
│   ├── photos/
│   └── screenshots/
├── protocols/            # Сгенерированные PDF протоколы (создается автоматически)
└── protocols_db.json     # База данных протоколов (создается автоматически)
```

## API Endpoints

### 1. Загрузка видео протокола
`POST /api/protocols/video`
- Параметры: `device_id` (form-data), `video` (file)

### 2. Загрузка фото протокола
`POST /api/protocols/photos`
- Параметры: `device_id` (form-data), `photos` (files, массив)

### 3. Загрузка скриншотов протокола
`POST /api/protocols/screenshots`
- Параметры: `device_id` (form-data), `screenshots` (files, массив)

### 4. Получение списка протоколов
`GET /api/protocols?device_id={device_id}`

### 5. Скачивание PDF протокола
`GET /api/protocols/{protocol_id}/pdf`

### 6. Проверка работоспособности
`GET /api/health`

Подробная документация API находится в файле `API_DOCUMENTATION.md`.

## Тестирование API

### Проверка работоспособности:
```bash
curl http://localhost:5001/api/health
```

### Пример загрузки видео (требуется реальный файл):
```bash
curl -X POST http://localhost:5001/api/protocols/video \
  -F "device_id=TEST_DEVICE_123" \
  -F "video=@/path/to/video.mp4"
```

## Примечания

- Все загруженные файлы сохраняются в папке `uploads/`
- PDF протоколы генерируются автоматически и сохраняются в папке `protocols/`
- Данные о протоколах хранятся в JSON файле `protocols_db.json`
- В продакшене рекомендуется использовать базу данных вместо JSON файла
- Для продакшена также рекомендуется добавить аутентификацию и использовать HTTPS

