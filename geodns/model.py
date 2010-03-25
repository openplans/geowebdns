from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Unicode, DateTime, Column, MetaData, Integer
from geoalchemy import GeometryColumn, MultiPolygon
from geoalchemy import GeometryDDL
from geodns.config import engine
from simplejson import dumps, loads

metadata = MetaData(engine)
Base = declarative_base(metadata=metadata)

class Jurisdiction(Base):
    __tablename__ = 'jurisdiction'
    id = Column(Integer, primary_key=True)
    # Readable name, e.g., "Ward 4"
    name = Column(Unicode)
    # URI, e.g., http://muni.example.com/wards/4
    uri = Column(Unicode)
    # The type of entity this represents:
    type_uri = Column(Unicode)
    # When it was last updated:
    updated = Column(DateTime, default=datetime.now)
    # The geometry it represents; everything is a multipolygon:
    geom = GeometryColumn(MultiPolygon(2))
    # Someplace to stuff the properties:
    properties_json = Column(Unicode)

    @property
    def properties(self):
        """Arbitrary JSON-encodable properties; these aren't used
        internally anywhere, but do give you a location to drop in
        some information"""
        json = self.properties_json
        if not json:
            return None
        return loads(json)

    @properties.setter
    def set_properties(self, value):
        if value is None:
            self.properties_json = None
        else:
            self.properties_json = unicode(dumps(value))


GeometryDDL(Jurisdiction.__table__)
