import os
from sqlalchemy import create_engine

engine = create_engine(
    'postgres://%(CONFIG_PG_USER)s:%(CONFIG_PG_PASSWORD)s@'
    '%(CONFIG_PG_HOST)s/%(CONFIG_PG_DBNAME)s' % os.environ,
    echo=True)
Session = sessionmaker(bind=engine)
session = Session()
