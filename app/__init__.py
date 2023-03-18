from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

engine = create_engine('sqlite:///trades.db', echo=False, connect_args={'check_same_thread': False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine)
