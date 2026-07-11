from flask import Blueprint, render_template, redirect, url_for, request
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

main_bp = Blueprint('main', __name__)

ATTRACTIONS = [
    {
        "id": 1,
        "name": "Университет Innopolis",
        "desc": "Главный кампус Университета Иннополис.",
        "long_desc": "Университет Иннополис — ведущий российский IT-вуз, основан в 2012 году. Здесь готовят специалистов в области ИИ, робототехники и кибербезопасности. Кампус включает современные лаборатории, библиотеку и общежития.",
        "address": "Университетская улица, 1",
        "lat": 55.753686,
        "lng": 48.743306,
        "image": "university.jpg",
        "audio": "audio/university.mp3"
    },
    {
        "id": 2,
        "name": "Шишкин Парк",
        "desc": "Зеленый парк с аллеями и фонтанами.",
        "long_desc": "Шишкин Парк — любимое место отдыха. Назван в честь художника. Здесь можно прогуляться, посидеть у фонтана или устроить пикник. Парк — площадка для городских праздников.",
        "address": "None",
        "lat": 55.752951,
        "lng": 48.740155,
        "image": "park.jpg",
        "audio": "audio/park.mp3"
    },
    {
        "id": 3,
        "name": "Технопарк имени А.С.Попова",
        "desc": "Инновационный центр для стартапов.",
        "long_desc": "Технопарк имени Попова — площадка для развития технологических стартапов. Здесь расположены офисы IT-компаний, коворкинги, лаборатории и акселерационные программы.",
        "address": "Университетская улица, 7",
        "lat": 55.751315,
        "lng": 48.751962,
        "image": "popov.jpg",
        "audio": "audio/popov.mp3"
    },
    {
        "id": 4,
        "name": "#Иннополис",
        "desc": "Главная площадь с флагом.",
        "long_desc": "Площадь #Иннополис — центральное место города, где установлен государственный флаг. Здесь проходят городские мероприятия, парады и праздничные гуляния.",
        "address": "#Иннополис flag",
        "lat": 55.751057,
        "lng": 48.753526,
        "image": "flag.jpg",
        "audio": "audio/flag.mp3"
    },
    {
        "id": 5,
        "name": "Бассейн",
        "desc": "Крытый бассейн для всех.",
        "long_desc": "Современный крытый бассейн открыт для всех желающих — как для студентов, так и для жителей города. Здесь проводятся занятия по плаванию, аквааэробике и соревнования.",
        "address": "Спортивная улица, 107",
        "lat": 55.751427,
        "lng": 48.742417,
        "image": "pool.jpg",
        "audio": "audio/pool.mp3"
    },
    {
        "id": 6,
        "name": "Лицей Иннополис",
        "desc": "Школа для одаренных детей.",
        "long_desc": "Лицей Иннополис — учебное заведение для талантливых детей с углублённым изучением математики, информатики и естественных наук. Здесь созданы все условия для развития интеллектуальных способностей.",
        "address": "Квантовый бульвар, 1",
        "lat": 55.747976,
        "lng": 48.746845,
        "image": "lyceum.jpg",
        "audio": "audio/lyceum.mp3"
    },
    {
        "id": 7,
        "name": "Технопарк имени Н.И.Лобачевского",
        "desc": "Технопарк на улице Лобачевского.",
        "long_desc": "Технопарк Лобачевского — ещё один инновационный кластер, специализирующийся на математическом моделировании, Big Data и искусственном интеллекте.",
        "address": "Университетская улица, 5",
        "lat": 55.752222,
        "lng": 48.749513,
        "image": "lobach1evskiy.jpg",
        "audio": "audio/lobachevskiy.mp3"
    },
    {
        "id": 8,
        "name": "Технопарк 1",
        "desc": "Технопарк на Университетской.",
        "long_desc": "Under construction",
        "address": "Университетская улица, 11",
        "lat": 55.753261,
        "lng": 48.750663,
        "image": "build.jpg",
        "audio": "audio/technopark1.mp3",
        "status": "construction"
    },
    {
        "id": 9,
        "name": "Пешеходник",
        "desc": "Локальный мем.",
        "long_desc": "Пешеходник — неофициальное название одного из переходов, ставшего городской достопримечательностью благодаря необычному расположению и местному фольклору.",
        "address": "None",
        "lat": 55.751252,
        "lng": 48.750673,
        "image": "crossroad.jpg",
        "audio": "audio/crossroad.mp3"
    },
    {
        "id": 10,
        "name": "Технопарк 2",
        "desc": "Технопарк на Центральной.",
        "long_desc": "Under construction",
        "address": "Центральная улица, 199",
        "lat": 55.753585,
        "lng": 48.752711,
        "image": "build.jpg",
        "audio": "audio/technopark2.mp3",
        "status": "construction"
    }
]

def format_attractions_for_ai():
    attractions_text = "Достопримечательности Иннополиса:\n"
    for attraction in ATTRACTIONS:
        attractions_text += f"- {attraction['name']}: {attraction['desc']} (адрес: {attraction['address']})\n"
    return attractions_text

@main_bp.route('/')
def index():
    return redirect(url_for('main.index_chat'))

@main_bp.route('/index', methods=['GET', 'POST'])
def index_chat():
    ai_response = None
    error_message = None
    
    if request.method == 'POST':
        user_query = request.form.get('user_query', '').strip()
        
        if not user_query:
            error_message = "Пожалуйста, введите вопрос."
        else:
            try:
                ai_response = query_ai_assistant(user_query)
            except Exception as e:
                error_message = f"Ошибка при запросе к нейросети: {str(e)}"
    
    return render_template("index.html", ai_response=ai_response, error_message=error_message, attractions=ATTRACTIONS)

@main_bp.route('/chat', methods=['POST'])
def chat():
    user_query = request.form.get('user_query', '').strip()
    ai_response = None
    error_message = None
    
    if not user_query:
        error_message = "Пожалуйста, введите вопрос."
    else:
        try:
            ai_response = query_ai_assistant(user_query)
        except Exception as e:
            error_message = f"Ошибка при запросе к нейросети: {str(e)}"
    
    return render_template("index.html", ai_response=ai_response, error_message=error_message, attractions=ATTRACTIONS)

def query_ai_assistant(user_query):
    API_URL = os.getenv("NEURO_API_URL", "https://geovpn.2bd.net:23238")
    CLIENT_API_KEY = os.getenv("CLIENT_API_KEY")
    
    if not CLIENT_API_KEY:
        raise ValueError("CLIENT_API_KEY не найдена в переменных окружения")
    
    headers = {"X-API-Key": CLIENT_API_KEY, "Content-Type": "application/json"}
    
    attractions_context = format_attractions_for_ai()
    
    system_instruction = (
        "Ты - дружелюбный и полезный ассистент для туристов в городе Иннополис. "
        "Отвечай кратко и красиво на русском языке. "
        "Используй эмодзи для оформления. "
        "Если вопрос о достопримечательностях, предоставь полезную информацию из доступного списка."
    )
    
    full_prompt = f"{system_instruction}\n\n{attractions_context}\n\nВопрос пользователя: {user_query}"
    
    payload = {
        "provider": "groq",
        "prompt": full_prompt,
        "system_instruction": system_instruction,
    }
    
    try:
        response = requests.post(
            f"{API_URL}/v1/chat/text",
            json=payload,
            headers=headers,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('content', 'Не удалось получить ответ от нейросети.')
        else:
            raise Exception(f"API ошибка: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка соединения с API: {str(e)}")

@main_bp.route('/map')
@main_bp.route('/map/<int:attraction_id>')
def map_view(attraction_id=None):
    return render_template("map.html", attractions=ATTRACTIONS, target_id=attraction_id)

@main_bp.route('/streetview')
def streetview_view():
    return render_template("streetview.html", attractions=ATTRACTIONS)

@main_bp.route('/reviews')
def reviews_page():
    reviews = [
                (1, 'alex', 5, 'Отличный университет! Очень современный.'),
                (1, 'maria', 4, 'Красивый кампус, но дорогой.'),
                (2, 'ivan', 3, 'Парк хороший, но маловат.'),
                (3, 'elena', 5, 'Технопарк просто супер!'),
                (3, 'alex', 4, 'Отличное место для стартапов.'),
                (4, 'maria', 5, 'Главная площадь – душа города.'),
                (5, 'ivan', 4, 'Бассейн чистый, но дорогой.'),
                (6, 'elena', 5, 'Лицей – мечта для детей.'),
                (7, 'alex', 3, 'Технопарк Лобачевского – обычный офисник.'),
                (8, 'maria', 4, 'Строят, но будет круто.'),
                (9, 'ivan', 5, 'Пешеходник – мем, но прикольно.'),
                (10, 'elena', 2, 'Технопарк 2 – серый и скучный.'),
            ]

    review_data = []
    for attraction_id, user, rating, text in reviews:
        review_data.append({
            'attraction_id': attraction_id,
            'attraction_name': ATTRACTIONS[attraction_id-1],
            'username': user,
            'rating': rating,
            'text': text,
            'created_at': '2026-07-10'
        })
    return render_template('reviews.html', reviews=review_data, attractions=ATTRACTIONS)

@main_bp.route('/tour/<int:attraction_id>')
def tour_guide(attraction_id):
    attraction = next((a for a in ATTRACTIONS if a['id'] == attraction_id), None)
    if not attraction:
        return redirect(url_for('index'))
    current_index = next((i for i, a in enumerate(ATTRACTIONS) if a['id'] == attraction_id), -1)
    return render_template('tour.html',
                           attraction=attraction,
                           attractions=ATTRACTIONS,
                           current_index=current_index)