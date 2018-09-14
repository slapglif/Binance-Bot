from datetime import datetime, timedelta
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

Base = declarative_base()
engine = create_engine('sqlite:///trades.db', echo=False, connect_args={'check_same_thread': False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine)
db = Session()


class Trade(Base):

    __tablename__ = 'trade'

    id = Column(Integer, primary_key=True)
    pair = Column(String(2000))
    price = Column(String(2000))
    orderId = Column(String(2000))
    quantity = Column(String(2000))

    @staticmethod
    def get_or_create(pair):
        setup = db.query(Trade).filter_by(pair=pair).first()
        if setup is None:
            entry = Trade(pair=pair)
            db.add(entry)
            db.commit()
        setup = db.query(Trade).filter_by(pair=pair).first()
        return setup

    @staticmethod
    def find(pair):
        setup = Session().query(Trade).filter_by(pair=pair).first()
        return setup


Base.metadata.create_all(engine)
