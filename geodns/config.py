import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.environ['CONFIG_PG_SQLALCHEMY'], echo=True)
Session = sessionmaker(bind=engine)
session = Session()
