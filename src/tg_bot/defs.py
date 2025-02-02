import httpx
from sqlalchemy import create_engine, Column, Integer, String, text, inspect, MetaData, Table
from sqlalchemy.orm import declarative_base, sessionmaker
from schedule_model import Timetable, Base

# Настройки базы данных
TIMETABLE_DATABASE_URL = "postgresql+psycopg2://bot:bot123@labs-bot-postgres/labs"
engine_timetable = create_engine(TIMETABLE_DATABASE_URL)
SessionLocalTimeTable = sessionmaker(autocommit=False, autoflush=False, bind=engine_timetable)

QUEUE_DATABASE_URL = "postgresql+psycopg2://bot:bot123@labs-bot-postgres/labs"
engine_queue = create_engine(QUEUE_DATABASE_URL)
SessionLocalQueue = sessionmaker(autocommit=False, autoflush=False, bind=engine_queue)

# Функция для получения данных из базы
def get_timetable():
    with engine_timetable.connect() as connection:
        result = connection.execute(text("""
            SELECT *
            FROM timetable
            ORDER BY
              CASE
                WHEN day_of_week = 'Понедельник' THEN 1
                WHEN day_of_week = 'Вторник' THEN 2
                WHEN day_of_week = 'Среда' THEN 3
                WHEN day_of_week = 'Четверг' THEN 4
                WHEN day_of_week = 'Пятница' THEN 5
                WHEN day_of_week = 'Суббота' THEN 6
                WHEN day_of_week = 'Воскресенье' THEN 7
                ELSE 8
              END;
        """))

        timetable = []
        for row in result:
            timetable.append({
                'id': row[0],                # Порядковый номер столбца id
                'day_of_week': row[1],        # Порядковый номер столбца day_of_week
                'lesson_type_abbrev': row[2], # Порядковый номер столбца lesson_type_abbrev
                'subject': row[3],            # Порядковый номер столбца subject
                'numsubgroup': row[4],        # Порядковый номер столбца numsubgroup
                'start_time': row[5]
            })
        return timetable

def fetch_queues():
    # Инициализация метаданных
    metadata = MetaData()
    metadata.reflect(engine_queue)
    queue = []
    queue_name = []
    # Перебираем все таблицы в базе данных queue
    with engine_queue.connect() as connection:
        for table_name in metadata.tables:
            queue.append({"table_name": table_name})
            # Выполняем запрос к таблице для получения всех данных
            result = connection.execute(text(f"""
                        SELECT *
                        FROM public."{table_name}"
                        ORDER BY id ASC
                    """))
            # Проверяем, есть ли данные в таблице
            if result:
                for row in result:
                    queue.append({
                        'id': row[0],  # Порядковый номер столбца id
                        'username': row[1],  # Порядковый номер столбца username
                    })
            else:
                queue.append("Таблица пуста\n")

    return queue

def check_lesson(lesson: String):
    timetable = get_timetable()
    for item in timetable:
        if item['subject'] == lesson:
            return True
    return False

def add_queue(lesson):
    inspector = inspect(engine_queue)
    if not inspector.has_table(lesson):
        base = declarative_base()
        class Queue(base):
            __tablename__ = f"{lesson}"
            id = Column(Integer, primary_key=True)
            nickname = Column(String)

         # Создаем все таблицы, которые еще не существуют
        base.metadata.create_all(engine_queue)
        return "200"
    else:
        return "Already exist"

def add_person_to_queue(lesson, num, username):
    inspector = inspect(engine_queue)
    if inspector.has_table(lesson): #проверка на существование предмета
        base = declarative_base()
        class Queue(base):
            __tablename__ = f"{lesson}"
            id = Column(Integer, primary_key=True)
            nickname = Column(String)
        scession = SessionLocalQueue()
        user_exists = scession.query(Queue).filter_by(nickname=username).first()
        id_exists = scession.query(Queue).filter_by(id=num).first()
        if not user_exists: #проверка на то, что человек уже записан
            if not id_exists:
                add_person = Queue(
                    id= num,
                    nickname= username
                )
                db = SessionLocalQueue()
                db.add(add_person)
                db.commit()
                return "200"
            else:
                return "place_holded"
        else: return "Alr in queue"
    else:
        return "Doesn't exist"

async def set_group(group_num):
    print(group_num)
    api_url = f"https://iis.bsuir.by/api/v1/schedule?studentGroup={group_num}"
    engine = create_engine(TIMETABLE_DATABASE_URL)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    try:
        # Делаем GET-запрос к серверу
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)

        # Проверяем успешность запроса
        if response.status_code != 200:
            raise ValueError(f"Ошибка при получении данных: {response.status_code}")

        # Получаем JSON ответ
        data = response.json()

        # Подключаемся к базе данных
        db = SessionLocal()
        Base.metadata.create_all(bind=engine)

        try:
            for day, lessons in data['schedules'].items():  # Итерируемся по дням недели
                for lesson in lessons:  # Итерируемся по занятиям внутри каждого дня
                    # Фильтруем занятия по "lessonTypeAbbrev" == "ЛР"
                    if lesson.get("lessonTypeAbbrev") == "ЛР":
                        # Создаем запись для базы данных
                        db_lesson = Timetable(
                            day_of_week=day,  # День недели (например, 'Суббота')
                            lesson_type_abbrev=lesson["lessonTypeAbbrev"],
                            subject=lesson["subject"],
                            numsubgroup=lesson["numSubgroup"],
                            start_time=lesson["startLessonTime"]
                        )
                        db.add(db_lesson)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error occurred: {e}")


        finally:
            db.close()

    except httpx.HTTPError as e:
        raise ValueError(str(e))