import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, MetaData, Table
from sqlalchemy.orm import declared_attr, declarative_base, sessionmaker, Session

load_dotenv()

DB_USER = os.getenv('DB_USER_LOGIN')
DB_PASS = os.getenv('DB_USER_PASSWORD')
DB_IP = os.getenv('DB_IP')
DB_NAME = os.getenv('DB_NAME')

# Создаем объект Engine для работы с базой данных SQLite


Base = declarative_base()
engine = create_engine(f'mssql+pyodbc://{DB_USER}:{DB_PASS}@{DB_IP}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server')

metadata = MetaData()
contractor_table = Table('NH_Контрагент', metadata, autoload_with=engine)


# Создаем класс для таблицы, используя отражение
class Contractor(Base):
    __table__ = contractor_table
    __mapper_args__ = {
        'primary_key': [contractor_table.c.Id]  # Укажите здесь ваш первичный ключ
    }


Session = sessionmaker(bind=engine)
session = Session()
