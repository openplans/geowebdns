import cgi
import os
import string
from webob.dec import wsgify
from webob import exc
from webob import Response
from simplejson import dumps
from decimal import Decimal
from geowebdns.model import Jurisdiction, metadata
from geowebdns.config import session, engine
from sqlalchemy.sql import expression
from sqlalchemy.sql import select
import silversupport.secret


def only_get(func):
    """Decorator to require a GET request and throw an HTTP error if not"""
    def decorated(*args, **kw):
        req = args[-1]
        if req.method != 'GET':
            raise exc.HTTPMethodNotAllowed('Only GET is allowed', allow='GET')
        return func(*args, **kw)
    return decorated

class Application(object):
    """This object represents the entire application"""
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
        if req.path_info in ('/', '/index.html'):
            return self.index(req)
        if req.path_info == '/.internal/update_fetch':
            return self.update_fetch(req)
        else:
            raise exc.HTTPNotFound()

    @wsgify
    def update_fetch(self, req):
        """This is called when the application is deployed; it makes
        sure the tables are created"""
        assert req.environ.get('silverlining.internal')
        metadata.create_all()
        return Response(
            'ok', content_type='text/plain')

    @wsgify
    @only_get
    def api1(self, req):
        # FIXME: should throw a 400 Bad request as appropriate:
        lat = Decimal(req.GET['lat'])
        long = Decimal(req.GET['long'])
        result = self.query(req, (lat, long), types=req.GET.getall('type'))
        return Response(
            dumps(result),
            content_type='application/json')

    @wsgify
    @only_get
    def api1_types(self, req):
        s = select([Jurisdiction.type_uri], distinct=True).order_by(Jurisdiction.type_uri)
        conn = engine.connect()
        results = [row.type_uri for row in conn.execute(s)]
        return Response(
            dumps(results),
            content_type='application/json')
    
    @wsgify
    @only_get
    def index(self, req):
        template = get_template('index.html')
        google_key = silversupport.secret.get_key('google.api_key')
        content = template.substitute(google_api_key=google_key)
        return Response(content, content_type='text/html')


    def query(self, req, coords, types):
        ## FIXME: This seems crude; it feels like it should also be
        ## quoted, but is at the moment safe because the coordinates
        ## are coerced into decimal:
        point = "POINT(%s %s)" % (coords[1], coords[0])
        ## This is a failed attempt at the query (more GeoAlchmey
        ## based): (I think the problem is a bug in geoalchemy, with
        ## points that are constructed outside of the database/engine)
        #point = WKTSpatialElement(point)
        #s = select([Jurisdiction.__table__], expression.func.ST_Intersects(
        #    Jurisdiction.geom, point))
        #conn = engine.connect()
        #s = conn.execute(s, point=point, srid=4326)
        type_comparisons = []
        for type in types:
            type_comparisons.append(
                Jurisdiction.type_uri == unicode(type))
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

TEMPLATES = os.path.join(os.path.dirname(__file__), 'templates')

def get_template(name):
    source = open(os.path.join(TEMPLATES, name)).read()
    return string.Template(source)

KML_TEMPLATE = get_template('placemarks.kml')
