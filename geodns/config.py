import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

s = 'postgres://'
if os.environ.get('CONFIG_PG_USER'):
    s += os.environ['CONFIG_PG_USER']
    if os.environ.get('CONFIG_PG_PASSWORD'):
        s += ':' + os.environ['CONFIG_PG_PASSWORD']
    s += '@'
s += os.environ.get('CONFIG_PG_HOST') or 'localhost'
s += '/' + os.environ['CONFIG_PG_DBNAME']

engine = create_engine(s, echo=True)
Session = sessionmaker(bind=engine)
session = Session()
