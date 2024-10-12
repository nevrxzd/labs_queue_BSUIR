import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
from schedule_model import Base, Timetable

app = FastAPI()

# Настройки базы данных
DATABASE_URL = "postgresql+psycopg2://bot:bot123@localhost/timetable"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Pydantic модель для запроса
class Lesson(BaseModel):
    day_of_week: str
    lesson_type_abbrev: str
    subject: str
    numsubgroup: str
    start_time: str

@app.get("/fetch-timetable")
async def fetch_timetable():
    # URL сервера с расписанием
    api_url = "https://iis.bsuir.by/api/v1/schedule?studentGroup=324404"

    try:
        # Делаем GET-запрос к серверу
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)

        # Проверяем успешность запроса
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Ошибка при получении данных")

        # Получаем JSON ответ
        data = response.json()

        # Подключаемся к базе данных
        db = SessionLocal()

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
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", port=8001, log_level="info")