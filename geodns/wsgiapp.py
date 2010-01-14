from webob.dec import wsgify
from webob import exc
from webob import Response
from simplejson import dumps
from decimal import Decimal
from geodns.model import Jurisdiction, metadata
from geodns.config import session, engine
from geoalchemy import WKTSpatialElement

class Application(object):
    def __init__(self):
        pass

    @wsgify
    def __call__(self, req):
        if req.path_info_peek() == 'api1':
            return self.api1(req)
        if req.path_info == '/.internal/update_fetch':
            return self.update_fetch(req)
        else:
            return self.not_found(req)

    @wsgify
    def update_fetch(self, req):
        assert req.environ.get('toppcloud.internal')
        metadata.create_all()
        return Response(
            'ok', content_type='text/plain')

    @wsgify
    def api1(self, req):
        if req.method != 'GET':
            raise exc.HTTPMethodNotAllowed('Only GET is allowed', allow='GET')
        lat = Decimal(req.GET['lat'])
        long = Decimal(req.GET['long'])
        result = self.query((lat, long), type=req.GET['type'])
        return Response(
            dumps(result),
            content_type='application/json')
    
    def query(self, coords, type):
        from sqlalchemy.sql import expression
        from sqlalchemy.sql import select
        ## FIXME: this is a long-winded way of doing the select:
        point = "POINT(%s %s)" % (coords[1], coords[0])
        point = WKTSpatialElement(point)
        s = select([Jurisdiction.__table__], expression.func.ST_Intersects(
            Jurisdiction.geom, point))
        conn = engine.connect()
        s = conn.execute(s, point=point, srid=4326)
        results = []
        for row in s:
            results.append(dict(
                type=row.type_uri,
                name=row.name,
                uri=type))
        return {'results': results}
    
        
