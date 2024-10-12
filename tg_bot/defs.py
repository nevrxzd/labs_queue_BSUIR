from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, text, inspect, MetaData, Table
from sqlalchemy.orm import declarative_base

# Настройки базы данных
TIMETABLE_DATABASE_URL = "postgresql+psycopg2://bot:bot123@localhost/timetable"
engine_timetable = create_engine(TIMETABLE_DATABASE_URL)
SessionLocalTimeTable = sessionmaker(autocommit=False, autoflush=False, bind=engine_timetable)

QUEUE_DATABASE_URL = "postgresql+psycopg2://bot:bot123@localhost/queue"
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
                        'username': row[1],  # Порядковый номер столбца day_of_week
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
    if inspector.has_table(lesson):
        base = declarative_base()
        class Queue(base):
            __tablename__ = f"{lesson}"
            id = Column(Integer, primary_key=True)
            nickname = Column(String)
        scession = SessionLocalQueue()
        user_exists = scession.query(Queue).filter_by(nickname=username).first()
        id_exists = scession.query(Queue).filter_by(id=num).first()
        if not user_exists:
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


