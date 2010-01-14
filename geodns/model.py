from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Unicode, DateTime, Column, MetaData, Integer
from geoalchemy import GeometryColumn, Point, LineString, MultiPolygon
from geoalchemy import GeometryDDL
from geodns.config import engine

metadata = MetaData(engine)
Base = declarative_base(metadata=metadata)

class Jurisdiction(Base):
    __tablename__ = 'jurisdiction'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    uri = Column(Unicode)
    type_uri = Column(Unicode)
    updated = Column(DateTime, default=datetime.now)
    geom = GeometryColumn(MultiPolygon(2))

GeometryDDL(Jurisdiction.__table__)
