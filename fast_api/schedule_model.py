from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Timetable(Base):
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String, index=True)
    lesson_type_abbrev = Column(String, index=True)
    subject = Column(String)
    numsubgroup = Column(String)
    start_time = Column(String)