# API Документация для мобильного приложения

## Базовый URL
```
http://your-server-ip:5001
```

## Формат запросов

Все запросы на загрузку файлов используют `multipart/form-data`.

---

## 1. Загрузка видео протокола

**Endpoint:** `POST /api/protocols/video`

**Параметры:**
- `device_id` (form-data, string, обязательный) - Уникальный идентификатор телефона
- `video` (file, обязательный) - Видео файл (mp4, mov, avi)

**Пример запроса (cURL):**
```bash
curl -X POST http://localhost:5001/api/protocols/video \
  -F "device_id=ABC123XYZ" \
  -F "video=@/path/to/video.mp4"
```

**Пример запроса (JavaScript/Fetch):**
```javascript
const formData = new FormData();
formData.append('device_id', 'ABC123XYZ');
formData.append('video', videoFile);

fetch('http://your-server:5001/api/protocols/video', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**Пример запроса (React Native):**
```javascript
const uploadVideo = async (videoUri, deviceId) => {
  const formData = new FormData();
  formData.append('device_id', deviceId);
  formData.append('video', {
    uri: videoUri,
    type: 'video/mp4',
    name: 'video.mp4',
  });

  const response = await fetch('http://your-server:5001/api/protocols/video', {
    method: 'POST',
    body: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return await response.json();
};
```

**Успешный ответ (200):**
```json
{
  "success": true,
  "protocol_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Видео успешно загружено",
  "pdf_url": "/api/protocols/550e8400-e29b-41d4-a716-446655440000/pdf"
}
```

**Ошибки:**
- `400` - Отсутствует файл или device_id
- `400` - Недопустимый тип файла

---

## 2. Загрузка фото протокола

**Endpoint:** `POST /api/protocols/photos`

**Параметры:**
- `device_id` (form-data, string, обязательный) - Уникальный идентификатор телефона
- `photos` (files, обязательный) - Массив фото файлов (jpg, jpeg, png)

**Пример запроса (cURL):**
```bash
curl -X POST http://localhost:5001/api/protocols/photos \
  -F "device_id=ABC123XYZ" \
  -F "photos=@/path/to/photo1.jpg" \
  -F "photos=@/path/to/photo2.jpg"
```

**Пример запроса (React Native):**
```javascript
const uploadPhotos = async (photoUris, deviceId) => {
  const formData = new FormData();
  formData.append('device_id', deviceId);
  
  photoUris.forEach((uri, index) => {
    formData.append('photos', {
      uri: uri,
      type: 'image/jpeg',
      name: `photo_${index}.jpg`,
    });
  });

  const response = await fetch('http://your-server:5001/api/protocols/photos', {
    method: 'POST',
    body: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return await response.json();
};
```

**Успешный ответ (200):**
```json
{
  "success": true,
  "protocol_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Загружено 3 фото",
  "pdf_url": "/api/protocols/550e8400-e29b-41d4-a716-446655440000/pdf"
}
```

---

## 3. Загрузка скриншотов протокола

**Endpoint:** `POST /api/protocols/screenshots`

**Параметры:**
- `device_id` (form-data, string, обязательный) - Уникальный идентификатор телефона
- `screenshots` (files, обязательный) - Массив скриншотов (jpg, jpeg, png)

**Пример запроса (React Native):**
```javascript
const uploadScreenshots = async (screenshotUris, deviceId) => {
  const formData = new FormData();
  formData.append('device_id', deviceId);
  
  screenshotUris.forEach((uri, index) => {
    formData.append('screenshots', {
      uri: uri,
      type: 'image/png',
      name: `screenshot_${index}.png`,
    });
  });

  const response = await fetch('http://your-server:5001/api/protocols/screenshots', {
    method: 'POST',
    body: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return await response.json();
};
```

**Успешный ответ (200):**
```json
{
  "success": true,
  "protocol_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Загружено 5 скриншотов",
  "pdf_url": "/api/protocols/550e8400-e29b-41d4-a716-446655440000/pdf"
}
```

---

## 4. Получение списка протоколов

**Endpoint:** `GET /api/protocols?device_id={device_id}`

**Параметры:**
- `device_id` (query parameter, string, обязательный) - Уникальный идентификатор телефона

**Пример запроса:**
```javascript
const getProtocols = async (deviceId) => {
  const response = await fetch(
    `http://your-server:5001/api/protocols?device_id=${deviceId}`,
    {
      method: 'GET',
    }
  );

  return await response.json();
};
```

**Успешный ответ (200):**
```json
{
  "success": true,
  "protocols": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "type": "video",
      "date": "15.12.2024 14:30:25",
      "number": "550E8400",
      "pdf_url": "/api/protocols/550e8400-e29b-41d4-a716-446655440000/pdf"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "type": "photos",
      "date": "14.12.2024 10:15:30",
      "number": "660E8400",
      "pdf_url": "/api/protocols/660e8400-e29b-41d4-a716-446655440001/pdf"
    }
  ]
}
```

**Типы протоколов:**
- `video` - Протокол с видео
- `photos` - Протокол с фото
- `screenshots` - Протокол со скриншотами

---

## 5. Скачивание PDF протокола

**Endpoint:** `GET /api/protocols/{protocol_id}/pdf`

**Параметры:**
- `protocol_id` (path parameter, string, обязательный) - ID протокола

**Пример запроса (React Native):**
```javascript
const downloadPDF = async (protocolId) => {
  const response = await fetch(
    `http://your-server:5001/api/protocols/${protocolId}/pdf`,
    {
      method: 'GET',
    }
  );

  // В React Native для скачивания файла используйте библиотеку типа react-native-fs
  // или сохраните blob в файловую систему
  const blob = await response.blob();
  // Далее сохраните blob в файл на устройстве
};
```

**Успешный ответ (200):**
- Content-Type: `application/pdf`
- Файл возвращается как attachment для скачивания

**Ошибки:**
- `404` - Протокол не найден
- `404` - PDF файл не найден

---

## 6. Проверка работоспособности API

**Endpoint:** `GET /api/health`

**Пример запроса:**
```javascript
fetch('http://your-server:5001/api/health')
  .then(response => response.json())
  .then(data => console.log(data));
```

**Успешный ответ (200):**
```json
{
  "status": "ok",
  "message": "API работает"
}
```

---

## Полный пример использования в React Native

```javascript
import { Platform } from 'react-native';

const API_BASE_URL = 'http://your-server-ip:5001';

// Получаем уникальный ID устройства
const getDeviceId = async () => {
  // Используйте библиотеку типа react-native-device-info
  // или генерируйте и сохраняйте UUID при первом запуске
  const DeviceInfo = require('react-native-device-info');
  return await DeviceInfo.getUniqueId();
};

// Загрузка видео
const uploadVideoProtocol = async (videoUri) => {
  const deviceId = await getDeviceId();
  const formData = new FormData();
  formData.append('device_id', deviceId);
  formData.append('video', {
    uri: videoUri,
    type: 'video/mp4',
    name: 'video.mp4',
  });

  const response = await fetch(`${API_BASE_URL}/api/protocols/video`, {
    method: 'POST',
    body: formData,
  });

  return await response.json();
};

// Загрузка фото
const uploadPhotosProtocol = async (photoUris) => {
  const deviceId = await getDeviceId();
  const formData = new FormData();
  formData.append('device_id', deviceId);
  
  photoUris.forEach((uri, index) => {
    formData.append('photos', {
      uri: uri,
      type: 'image/jpeg',
      name: `photo_${index}.jpg`,
    });
  });

  const response = await fetch(`${API_BASE_URL}/api/protocols/photos`, {
    method: 'POST',
    body: formData,
  });

  return await response.json();
};

// Загрузка скриншотов
const uploadScreenshotsProtocol = async (screenshotUris) => {
  const deviceId = await getDeviceId();
  const formData = new FormData();
  formData.append('device_id', deviceId);
  
  screenshotUris.forEach((uri, index) => {
    formData.append('screenshots', {
      uri: uri,
      type: 'image/png',
      name: `screenshot_${index}.png`,
    });
  });

  const response = await fetch(`${API_BASE_URL}/api/protocols/screenshots`, {
    method: 'POST',
    body: formData,
  });

  return await response.json();
};

// Получение списка протоколов
const getProtocols = async () => {
  const deviceId = await getDeviceId();
  const response = await fetch(
    `${API_BASE_URL}/api/protocols?device_id=${deviceId}`
  );
  return await response.json();
};

// Скачивание PDF
const downloadProtocolPDF = async (protocolId) => {
  const response = await fetch(
    `${API_BASE_URL}/api/protocols/${protocolId}/pdf`
  );
  
  // Используйте react-native-fs для сохранения файла
  const RNFS = require('react-native-fs');
  const path = `${RNFS.DocumentDirectoryPath}/protocol_${protocolId}.pdf`;
  
  const blob = await response.blob();
  // Конвертируйте blob в base64 и сохраните
  // или используйте другую библиотеку для работы с файлами
  
  return path;
};
```

---

## Важные замечания

1. **Уникальный ID устройства:** Используйте библиотеку `react-native-device-info` для получения уникального ID устройства, или генерируйте UUID при первом запуске приложения и сохраняйте его в AsyncStorage.

2. **Разрешения:** Убедитесь, что приложение запрашивает необходимые разрешения:
   - Камера (для видео и фото)
   - Хранилище (для сохранения файлов)
   - Сеть (для отправки на API)

3. **Обработка ошибок:** Всегда обрабатывайте ошибки сети и проверяйте статус ответа.

4. **Безопасность:** В продакшене используйте HTTPS и добавьте аутентификацию.

