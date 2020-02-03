from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import basedir
import os

engine = create_engine('sqlite:///' + os.path.join(basedir, 'DB.db'),
                       convert_unicode=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)
