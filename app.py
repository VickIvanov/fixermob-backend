import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import json

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для мобильных приложений

# Конфигурация
UPLOAD_FOLDER = 'uploads'
PROTOCOLS_FOLDER = 'protocols'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'jpg', 'jpeg', 'png'}

# Создаем необходимые папки
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROTOCOLS_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'videos'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'photos'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'screenshots'), exist_ok=True)

# Файл для хранения данных о протоколах
PROTOCOLS_DB = 'protocols_db.json'

def load_protocols():
    """Загружает список протоколов из файла"""
    if os.path.exists(PROTOCOLS_DB):
        with open(PROTOCOLS_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_protocols(protocols):
    """Сохраняет список протоколов в файл"""
    with open(PROTOCOLS_DB, 'w', encoding='utf-8') as f:
        json.dump(protocols, f, ensure_ascii=False, indent=2)

def allowed_file(filename):
    """Проверяет, разрешен ли тип файла"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_pdf(protocol_id, protocol_type, device_id, files_info):
    """Генерирует PDF протокол (моковая версия)"""
    pdf_path = os.path.join(PROTOCOLS_FOLDER, f'{protocol_id}.pdf')
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Заголовок
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Протокол осмотра")
    
    # Информация о протоколе
    y = height - 100
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Номер протокола: {protocol_id}")
    y -= 25
    c.drawString(50, y, f"Тип протокола: {protocol_type}")
    y -= 25
    c.drawString(50, y, f"ID устройства: {device_id}")
    y -= 25
    c.drawString(50, y, f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    y -= 40
    
    # Информация о файлах
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Загруженные файлы:")
    y -= 25
    c.setFont("Helvetica", 10)
    
    for i, file_info in enumerate(files_info, 1):
        filename = file_info.get('filename', 'Неизвестно')
        size = file_info.get('size', 0)
        size_mb = size / (1024 * 1024)
        c.drawString(50, y, f"{i}. {filename} ({size_mb:.2f} MB)")
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50
    
    c.save()
    return pdf_path

@app.route('/api/protocols/video', methods=['POST'])
def upload_video():
    """Загрузка видео протокола"""
    if 'video' not in request.files:
        return jsonify({'error': 'Видео файл не найден'}), 400
    
    if 'device_id' not in request.form:
        return jsonify({'error': 'device_id обязателен'}), 400
    
    device_id = request.form['device_id']
    video_file = request.files['video']
    
    if video_file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if not allowed_file(video_file.filename):
        return jsonify({'error': 'Недопустимый тип файла'}), 400
    
    # Генерируем уникальный ID протокола
    protocol_id = str(uuid.uuid4())
    
    # Сохраняем видео
    filename = secure_filename(video_file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower()
    saved_filename = f"{protocol_id}.{file_extension}"
    video_path = os.path.join(UPLOAD_FOLDER, 'videos', saved_filename)
    video_file.save(video_path)
    
    # Получаем размер файла
    file_size = os.path.getsize(video_path)
    
    # Создаем запись о протоколе
    protocol = {
        'id': protocol_id,
        'type': 'video',
        'device_id': device_id,
        'date': datetime.now().isoformat(),
        'files': [{
            'filename': filename,
            'saved_filename': saved_filename,
            'size': file_size,
            'path': video_path
        }],
        'pdf_path': None
    }
    
    # Генерируем PDF
    pdf_path = generate_pdf(protocol_id, 'Протокол с видео', device_id, protocol['files'])
    protocol['pdf_path'] = pdf_path
    
    # Сохраняем протокол
    protocols = load_protocols()
    protocols.append(protocol)
    save_protocols(protocols)
    
    return jsonify({
        'success': True,
        'protocol_id': protocol_id,
        'message': 'Видео успешно загружено',
        'pdf_url': f'/api/protocols/{protocol_id}/pdf'
    }), 200

@app.route('/api/protocols/photos', methods=['POST'])
def upload_photos():
    """Загрузка фото протокола (несколько файлов)"""
    if 'photos' not in request.files:
        return jsonify({'error': 'Фото файлы не найдены'}), 400
    
    if 'device_id' not in request.form:
        return jsonify({'error': 'device_id обязателен'}), 400
    
    device_id = request.form['device_id']
    photos = request.files.getlist('photos')
    
    if not photos or photos[0].filename == '':
        return jsonify({'error': 'Файлы не выбраны'}), 400
    
    # Генерируем уникальный ID протокола
    protocol_id = str(uuid.uuid4())
    
    files_info = []
    for photo in photos:
        if photo.filename == '':
            continue
        
        if not allowed_file(photo.filename):
            continue
        
        filename = secure_filename(photo.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        saved_filename = f"{protocol_id}_{len(files_info)}.{file_extension}"
        photo_path = os.path.join(UPLOAD_FOLDER, 'photos', saved_filename)
        photo.save(photo_path)
        
        file_size = os.path.getsize(photo_path)
        files_info.append({
            'filename': filename,
            'saved_filename': saved_filename,
            'size': file_size,
            'path': photo_path
        })
    
    if not files_info:
        return jsonify({'error': 'Не удалось загрузить ни одного файла'}), 400
    
    # Создаем запись о протоколе
    protocol = {
        'id': protocol_id,
        'type': 'photos',
        'device_id': device_id,
        'date': datetime.now().isoformat(),
        'files': files_info,
        'pdf_path': None
    }
    
    # Генерируем PDF
    pdf_path = generate_pdf(protocol_id, 'Протокол с фото', device_id, files_info)
    protocol['pdf_path'] = pdf_path
    
    # Сохраняем протокол
    protocols = load_protocols()
    protocols.append(protocol)
    save_protocols(protocols)
    
    return jsonify({
        'success': True,
        'protocol_id': protocol_id,
        'message': f'Загружено {len(files_info)} фото',
        'pdf_url': f'/api/protocols/{protocol_id}/pdf'
    }), 200

@app.route('/api/protocols/screenshots', methods=['POST'])
def upload_screenshots():
    """Загрузка скриншотов протокола (несколько файлов)"""
    if 'screenshots' not in request.files:
        return jsonify({'error': 'Скриншоты не найдены'}), 400
    
    if 'device_id' not in request.form:
        return jsonify({'error': 'device_id обязателен'}), 400
    
    device_id = request.form['device_id']
    screenshots = request.files.getlist('screenshots')
    
    if not screenshots or screenshots[0].filename == '':
        return jsonify({'error': 'Файлы не выбраны'}), 400
    
    # Генерируем уникальный ID протокола
    protocol_id = str(uuid.uuid4())
    
    files_info = []
    for screenshot in screenshots:
        if screenshot.filename == '':
            continue
        
        if not allowed_file(screenshot.filename):
            continue
        
        filename = secure_filename(screenshot.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        saved_filename = f"{protocol_id}_{len(files_info)}.{file_extension}"
        screenshot_path = os.path.join(UPLOAD_FOLDER, 'screenshots', saved_filename)
        screenshot.save(screenshot_path)
        
        file_size = os.path.getsize(screenshot_path)
        files_info.append({
            'filename': filename,
            'saved_filename': saved_filename,
            'size': file_size,
            'path': screenshot_path
        })
    
    if not files_info:
        return jsonify({'error': 'Не удалось загрузить ни одного файла'}), 400
    
    # Создаем запись о протоколе
    protocol = {
        'id': protocol_id,
        'type': 'screenshots',
        'device_id': device_id,
        'date': datetime.now().isoformat(),
        'files': files_info,
        'pdf_path': None
    }
    
    # Генерируем PDF
    pdf_path = generate_pdf(protocol_id, 'Протокол со скриншотами', device_id, files_info)
    protocol['pdf_path'] = pdf_path
    
    # Сохраняем протокол
    protocols = load_protocols()
    protocols.append(protocol)
    save_protocols(protocols)
    
    return jsonify({
        'success': True,
        'protocol_id': protocol_id,
        'message': f'Загружено {len(files_info)} скриншотов',
        'pdf_url': f'/api/protocols/{protocol_id}/pdf'
    }), 200

@app.route('/api/protocols', methods=['GET'])
def get_protocols():
    """Получение списка протоколов для устройства"""
    device_id = request.args.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id обязателен'}), 400
    
    protocols = load_protocols()
    
    # Фильтруем протоколы по device_id
    device_protocols = [p for p in protocols if p.get('device_id') == device_id]
    
    # Форматируем ответ
    result = []
    for protocol in device_protocols:
        date_obj = datetime.fromisoformat(protocol['date'])
        result.append({
            'id': protocol['id'],
            'type': protocol['type'],
            'date': date_obj.strftime('%d.%m.%Y %H:%M:%S'),
            'number': protocol['id'][:8].upper(),  # Первые 8 символов как номер
            'pdf_url': f'/api/protocols/{protocol["id"]}/pdf'
        })
    
    # Сортируем по дате (новые первые)
    result.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify({
        'success': True,
        'protocols': result
    }), 200

@app.route('/api/protocols/<protocol_id>/pdf', methods=['GET'])
def download_pdf(protocol_id):
    """Скачивание PDF протокола"""
    protocols = load_protocols()
    
    protocol = next((p for p in protocols if p['id'] == protocol_id), None)
    
    if not protocol:
        return jsonify({'error': 'Протокол не найден'}), 404
    
    if not protocol.get('pdf_path') or not os.path.exists(protocol['pdf_path']):
        return jsonify({'error': 'PDF файл не найден'}), 404
    
    return send_file(
        protocol['pdf_path'],
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'protocol_{protocol_id}.pdf'
    )

@app.route('/', methods=['GET'])
def index():
    """Главная страница для тестирования"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FixerMob Backend API</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .status { 
                padding: 15px;
                background: #4CAF50;
                color: white;
                border-radius: 5px;
                margin: 20px 0;
            }
            .endpoint {
                background: #f9f9f9;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #2196F3;
                border-radius: 4px;
            }
            code {
                background: #e8e8e8;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 FixerMob Backend API</h1>
            <div class="status">
                ✅ Сервер работает! API доступно на порту 5001
            </div>
            
            <h2>Доступные endpoints:</h2>
            
            <div class="endpoint">
                <strong>GET /api/health</strong><br>
                Проверка работоспособности API<br>
                <a href="/api/health" target="_blank">Попробовать →</a>
            </div>
            
            <div class="endpoint">
                <strong>POST /api/protocols/video</strong><br>
                Загрузка видео протокола<br>
                Параметры: <code>device_id</code>, <code>video</code> (file)
            </div>
            
            <div class="endpoint">
                <strong>POST /api/protocols/photos</strong><br>
                Загрузка фото протокола<br>
                Параметры: <code>device_id</code>, <code>photos</code> (files)
            </div>
            
            <div class="endpoint">
                <strong>POST /api/protocols/screenshots</strong><br>
                Загрузка скриншотов протокола<br>
                Параметры: <code>device_id</code>, <code>screenshots</code> (files)
            </div>
            
            <div class="endpoint">
                <strong>GET /api/protocols?device_id={id}</strong><br>
                Получение списка протоколов<br>
                <a href="/api/protocols?device_id=TEST" target="_blank">Попробовать →</a>
            </div>
            
            <div class="endpoint">
                <strong>GET /api/protocols/{id}/pdf</strong><br>
                Скачивание PDF протокола
            </div>
            
            <p style="margin-top: 30px; color: #666;">
                📖 Полная документация API находится в файле <code>API_DOCUMENTATION.md</code>
            </p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности API"""
    return jsonify({'status': 'ok', 'message': 'API работает'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

