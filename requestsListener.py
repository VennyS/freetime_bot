from quart import Quart, request, jsonify
from quart_cors import cors

import queries
from timeIntervals import timeIntervals

import io
import json

app = Quart(__name__)
app = cors(app)

# Изменить с учетом telegramid
@app.route('/', methods=['GET'])
async def index():
    telegramid = request.args.get('telegramid')
    data = timeIntervals(queries.userTime(telegramid)).allToJSON(True)
    if data:
        return jsonify(data)
    return 'null'

# Изменить с учетом telegramid
@app.route('/', methods=['POST'])
async def post():
    # Читаем данные из запроса
    data = await request.data
    # Создаем файлоподобный объект io.BytesIO для чтения данных
    data_stream = io.BytesIO(data)
    # Декодируем данные в строку
    data_string = data_stream.read().decode('utf-8')
    # Пытаемся преобразовать строку JSON в словарь
    try:
        json_data = json.loads(data_string)
    except json.JSONDecodeError:
        # Если данные не являются корректной JSON строкой, возвращаем ошибку
        return jsonify({'error': 'Invalid JSON data'}), 400

    # Здесь вы можете выполнить любую логику обработки полученных данных
    # В этом примере предполагается, что вы используете данные напрямую
    data = timeIntervals(json_data)
    queries.insertIntervals(data.telegramid, data.intervalsToTSRange())

    return 'Insert complete', 200

def start():
    app.run(port=5000)  # Установите порт на 5000

start()