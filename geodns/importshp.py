import sys
import os
import argparse
import zipfile
import tempfile
import subprocess
import simplejson
from glob import glob
import tempita
from cmdutils.arg import add_verbose, create_logger
from cmdutils import CommandError

description = """\
Import .shp files
"""

parser = argparse.ArgumentParser(
    description=description)

add_verbose(parser, add_log=True)

parser.add_argument(
    'file', metavar='FILE',
    help="The file to import")

parser.add_argument(
    '--print-json', action='store_true',
    help="Print out the intermediate json")

parser.add_argument(
    '--print-json-row', action='store_true',
    help="Print out one row of the intermediate json")

parser.add_argument(
    '--row-python', metavar='PYTHON_CODE',
    help="Python code that contains a convert(row) function (literal string)")

parser.add_argument(
    '--row-pyfile', metavar='FILE.py',
    help="File with Python code that contains a convert(row) function (literal string)")

parser.add_argument(
    '--row-name', metavar='TEMPLATE',
    help="A template to fill in missing name columns")

parser.add_argument(
    '--row-uri', metavar='TEMPLATE',
    help="A template to fill in missing uri columns (per-jurisdiction URIs)")

parser.add_argument(
    '--type-uri', metavar='URI',
    help="The type_uri value")

parser.add_argument(
    '--commit', action='store_true',
    help="Commit rows after inserting (otherwise it'll roll back)")

parser.add_argument(
    '--row-by-row', action='store_true',
    help="Commit each row one-by-one")

parser.add_argument(
    '--reset-database', action='store_true',
    help="Drop and re-add all database tables")

def catch_error(func):
    def decorated(*args, **kw):
        try:
            return func(*args, **kw)
        except CommandError, e:
            print e
            sys.exit(2)
    return decorated

def temp_dir(name):
    p = os.path.join('/tmp/%s-%s' % (name, os.getpid()))
    os.mkdir(p)
    return p

@catch_error
def main():
    args = parser.parse_args()
    logger =  create_logger(args)
    if args.reset_database:
        return reset_database(logger)
    file_set = get_file_set(logger, args.file)
    file_set = file_set.convert_to_standard_projection(logger)
    json = file_set.create_json(logger)
    if 'features' in json:
        logger.debug('Getting "features" from json result (of keys %s)' % ', '.join(json.keys()))
        json = json['features']
    rows = []
    convert = None
    if args.row_python:
        args.row_python += '\n'
        ns = {}
        exec args.row_python in ns
        if 'convert' not in ns:
            raise CommandError("--row-python code does not contain:\n  def convert(row):")
        convert = ns['convert']
    elif args.row_pyfile:
        ns = {'__file__': args.row_pyfile}
        execfile(args.row_pyfile, ns)
        if 'convert' not in ns:
            raise CommandError("--row-python-file=%s does not contain:\n  def convert(row):"
                               % args.row_pyfile)
        convert = ns['convert']
    row_name_tmpl = None
    if args.row_name:
        row_name_tmpl = tempita.Template(
            args.row_name,
            name='--row-name')
    row_uri_tmpl = None
    if args.row_uri:
        row_uri_tmpl = tempita.Template(
            args.row_uri,
            name='--row-uri')
    for item in json:
        row = {}
        row['geom'] = create_geometry_wkt(item['geometry'])
        row['type'] = item['type']
        row.update(item['properties'])
        if convert is not None:
            row = convert(row)
            if row is None:
                continue
        if args.type_uri:
            row.setdefault('type_uri', args.type_uri)
        if 'name' not in row and row_name_tmpl is not None:
            row['name'] = row_name_tmpl.substitute(
                row=row)
        if 'uri' not in row and row_uri_tmpl is not None:
            row['uri'] = row_uri_tmpl.substitute(
                row=row)
        rows.append(row)
    if args.print_json:
        for index, row in rows:
            print_row(row, index=index)
        return
    if args.print_json_row:
        if rows:
            print_row(rows[0])
        else:
            print 'No rows'
        return
    insert_rows(logger, rows, commit=args.commit,
                one_by_one=args.row_by_row)

def reset_database(logger):
    from geodns.model import metadata
    logger.notify('Dropping all tables')
    metadata.drop_all()
    logger.notify('Recreating all tables')
    metadata.create_all()

def insert_rows(logger, rows, commit, one_by_one):
    #import logging
    #logging.basicConfig()
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
    from geodns.model import Jurisdiction
    from geodns.config import session
    from geoalchemy import WKTSpatialElement
    to_commit = []
    for row in rows:
        j = Jurisdiction(
            name=row['name'],
            uri=row['uri'],
            type_uri=row['type_uri'],
            geom=WKTSpatialElement(row['geom']),
            )
        if not commit:
            logger.debug('Adding Jurisdiction %r', j)
            session.add_all([j])
        else:
            if one_by_one:
                logger.debug('Immediately committing %r', j)
                session.add_all([j])
                session.commit()
            else:
                logger.debug('Deferring Jurisdiction %r', j)
                to_commit.append(j)
    if to_commit and commit:
        session.add_all(to_commit)
        logger.notify('COMMIT')
        session.commit()
    elif not commit:
        logger.notify('ROLLBACK')
        session.rollback()

def print_row(row, index=None):
    if index is not None:
        print 'Row %5i' % index
        print '-'*9
    for name in sorted(row):
        if name == 'geom':
            continue
        print '%-15s: %s' % (name, row[name])
    geom = row['geom']
    if len(geom) > 30:
        geom = geom[:20] + '...' + geom[-10:]
    print '%-15s: %s' % ('geom', geom)

def create_geometry_wkt(json_geom):
    t = json_geom['type'].upper()
    coords = []
    incoming = json_geom['coordinates']
    if t == 'POLYGON':
        t = 'MULTIPOLYGON'
        incoming = [incoming]
    for polygon in incoming:
        polygon_proc = []
        for ring in polygon:
            ring_proc = []
            if ring and isinstance(ring[0], float):
                x, y = ring
                print 'Got a weird ring %r' % t, ring
                continue
                #proc_shape.append('%s %s' % (x, y))
                #continue
            for x, y in ring:
                ring_proc.append('%s %s' % (x, y))
            if ring_proc:
                polygon_proc.append('(%s)' % ', '.join(ring_proc))
            ## FIXME: just eliminate empty rings?
        if polygon_proc:
            coords.append('(%s)' % (', '.join(polygon_proc)))
        ## FIXME: just eliminate empty polygons?
    if coords:
        coords = '(%s)' % (', '.join(coords))
    else:
        coords = ' EMPTY'
    return t + coords

def get_file_set(logger, filename):
    if (os.path.isdir(os.path.basename(filename))
        and os.path.exists(filename+'.shp')):
        logger.debug('Using %r equivalent %r' % (filename, filename+'.shp'))
        filename += '.shp'
    if os.path.exists(filename) and filename.endswith('.shp'):
        return FileSet.from_shp(filename)
    if os.path.exists(filename) and filename.endswith('.zip'):
        dir = unpack_zip(filename)
        logger.info('Unpacking %s into %s' % (filename, dir))
        shps = glob(os.path.join(dir, '*/*.shp')) + glob(os.path.join(dir, '*.shp'))
        if not shps:
            raise CommandError('No .shp files in %s (unpacked to %s)'
                               % (filename, dir))
        if len(shps) > 1:
            raise CommandError('Ambiguous shapes: %s'
                               % ', '.join(shps))
        logger.debug('Found .shp file: %s' % shps[0])
        return FileSet.from_shp(shps[0])
    else:
        raise CommandError(
            'Cannot figure out what kind of file %s is' % filename)

def unpack_zip(filename):
    zip = zipfile.ZipFile(filename, 'r')
    tmp = temp_dir('geodns-importshp')
    zip.extractall(tmp)
    return tmp

class FileSet(object):
    def __init__(self, shp, dbf, prj, shx):
        self.name = os.path.splitext(os.path.basename(shp))[0]
        self.shp = shp
        self.dbf = dbf
        self.prj = prj
        self.shx = shx

    @classmethod
    def from_shp(cls, shp):
        base = os.path.splitext(shp)[0]
        return cls(
            shp=shp,
            dbf=base+'.dbf',
            prj=base+'.prj',
            shx=base+'.shx')

    def new(self):
        new_dir = temp_dir('geodns-new-import')
        return self.__class__(
            shp=os.path.join(new_dir, self.name+'.shp'),
            dbf=os.path.join(new_dir, self.name+'.dbf'),
            prj=os.path.join(new_dir, self.name+'.prj'),
            shx=os.path.join(new_dir, self.name+'.shx'),
            )

    def convert_to_standard_projection(self, logger):
        new_file_set = self.new()
        cmd = ['ogr2ogr', '-t_srs', 'EPSG:4326', '-f', 'ESRI Shapefile',
               new_file_set.shp, self.shp]
        logger.info('Running %s' % ' '.join(cmd))
        proc = subprocess.Popen(cmd)
        proc.communicate()
        if proc.returncode:
            logger.info('Command %s returned code %s' % (' '.join(cmd), proc.returncode))
        return new_file_set

    def create_json(self, logger):
        fid, tmp = tempfile.mkstemp(prefix='geodns-convert-json', suffix='.json')
        os.close(fid)
        # Hrm, ogr2ogr won't get me write to this without deleting first:
        os.unlink(tmp)
        try:
            cmd = ['ogr2ogr', '-f', 'GeoJSON', tmp, self.shp]
            logger.info('Running %s' % ' '.join(cmd))
            proc = subprocess.Popen(cmd)
            proc.communicate()
            if proc.returncode:
                logger.info('Command %s returned code %s' % (' '.join(cmd), proc.returncode))
            with open(tmp, 'rb') as fp:
                return simplejson.load(fp)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

if __name__ == '__main__':
    main()

