import cgi
import string
from webob.dec import wsgify
from webob import exc
from webob import Response
from simplejson import dumps
from decimal import Decimal
from geodns.model import Jurisdiction, metadata
from geodns.config import session, engine
from geoalchemy import WKTSpatialElement
from sqlalchemy.sql import expression
from sqlalchemy.sql import select

def only_get(func):
    def decorated(*args, **kw):
        req = args[-1]
        if req.method != 'GET':
            raise exc.HTTPMethodNotAllowed('Only GET is allowed', allow='GET')
        return func(*args, **kw)
    return decorated

class Application(object):
    def __init__(self):
        pass

    @wsgify
    def __call__(self, req):
        if req.path_info == '/api1/types':
            return self.api1_types(req)
        if req.path_info.startswith('/api1/kml/'):
            return self.api1_kml(req)
        if req.path_info_peek() == 'api1':
            return self.api1(req)
        if req.path_info == '/.internal/update_fetch':
            return self.update_fetch(req)
        else:
            raise exc.HTTPNotFound()

    @wsgify
    def update_fetch(self, req):
        assert req.environ.get('toppcloud.internal')
        metadata.create_all()
        return Response(
            'ok', content_type='text/plain')

    @wsgify
    @only_get
    def api1(self, req):
        lat = Decimal(req.GET['lat'])
        long = Decimal(req.GET['long'])
        result = self.query(req, (lat, long), types=req.GET.getall('type'))
        return Response(
            dumps(result),
            content_type='application/json')

    @wsgify
    @only_get
    def api1_types(self, req):
        s = select([Jurisdiction.type_uri], distinct=True)
        conn = engine.connect()
        s = conn.execute(s)
        results = []
        for row in s:
            results.append(row.type_uri)
        return Response(
            dumps(results),
            content_type='application/json')
    
    def query(self, req, coords, types):
        ## FIXME: I keep going back and form on this:
        point = "POINT(%s %s)" % (coords[1], coords[0])
        #point = WKTSpatialElement(point)
        #s = select([Jurisdiction.__table__], expression.func.ST_Intersects(
        #    Jurisdiction.geom, point))
        #conn = engine.connect()
        #s = conn.execute(s, point=point, srid=4326)
        type_comparisons = []
        for type in types:
            type_comparisons.append(
                Jurisdiction.type_uri == type)
        s = session.query(Jurisdiction).filter(
            expression.and_(
                expression.func.ST_Intersects(Jurisdiction.geom, expression.func.GeomFromText(point, 4326)),
                expression.or_(*type_comparisons)))
        results = []
        for row in s:
            results.append(dict(
                type=row.type_uri,
                name=row.name,
                uri=row.uri,
                properties=row.properties,
                kml_uri="%s/api1/kml/%s" % (req.application_url, row.id)))
        return {'results': results}

    @wsgify
    @only_get
    def api1_kml(self, req):
        assert req.path_info_pop() == 'api1'
        assert req.path_info_pop() == 'kml'
        id = int(req.path_info.lstrip('/'))
        s = select([Jurisdiction.__table__], Jurisdiction.id==id)
        conn = engine.connect()
        s = list(conn.execute(s))[0]
        kml_inner = session.scalar(s.geom.kml)
        kml = KML_TEMPLATE.substitute(
            name=cgi.escape(s.name),
            uri=cgi.escape(s.uri),
            polygons=kml_inner)
        return Response(
            kml,
            content_type='application/vnd.google-earth.kml+xml')

KML_TEMPLATE = string.Template("""\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>${name}</name>
      <description>${name}: ${uri}</description>
${polygons}
    </Placemark>
  </Document>
</kml>""")
