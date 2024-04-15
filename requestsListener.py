from quart import Quart, request, jsonify
from quart_cors import cors

import queries
from timeIntervals import timeIntervals

app = Quart(__name__)
app = cors(app)

@app.route('/', methods=['GET'])
async def index():
    data = timeIntervals(queries.userTime()).allToJSON(True)
    if data:
        return jsonify(data)
    return ''

@app.route('/', methods=['POST'])
async def post():
    # Проверяем, что в запросе присутствует JSON-строка
    if request.is_json:
        # Получаем JSON-строку из запроса
        json_data = await request.get_json()
        
        # Здесь вы можете выполнить любую логику обработки полученных данных
        # В этом примере предполагается, что вы используете JSON-строку напрямую
        data = timeIntervals(json_data)
        queries.insert(data.toTSRange())
        return 'Insert complete', 200
    else:
        # Возвращаем ошибку, если запрос не содержит JSON-строку
        return jsonify({'error': 'Request must contain JSON data'}), 400

def start():
    app.run(port=5000)  # Установите порт на 5000

start()