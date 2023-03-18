"""
This module contains the models for the application
"""
from sqlalchemy import Column, Integer, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from app import engine

Base = declarative_base()


class Trades(Base):
    """
    Trades model for the application
    """
    __tablename__ = 'trade'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(Text)
    price = Column(Float)
    order_id = Column(Text)
    quantity = Column(Float)


Base.metadata.create_all(engine)
