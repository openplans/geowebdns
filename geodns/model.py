from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Unicode, DateTime, Column, MetaData, Integer
from geoalchemy import GeometryColumn, Point, LineString, MultiPolygon
from geoalchemy import GeometryDDL
from geodns.config import engine
from simplejson import dumps, loads

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
    properties_json = Column(Unicode)

    @property
    def properties(self):
        json = self.properties_json
        if not json:
            return None
        return loads(json)

    @properties.setter
    def properties(self, value):
        if value is None:
            self.properties_json = None
        else:
            self.properties_json = unicode(dumps(value))

GeometryDDL(Jurisdiction.__table__)
