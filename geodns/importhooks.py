from lxml import html
import re
import time
import os
import urllib

CACHE_DIR = os.path.join(os.environ['HOME'], '.httplib2-cache')

boroughs = {
    1: 'Manhattan',
    2: 'Bronx',
    3: 'Brooklyn',
    4: 'Queens',
    5: 'Staten Island',
    }

base_community_url = 'http://www.nyc.gov/html/cau/html/cb/cb_%s.shtml'

def forced_cache_get(url):
    """The particular site in question doesn't do caching, and it is
    otherwise too slow, so we are forcing a cache"""
    fn = os.path.join(CACHE_DIR, urllib.quote(url, ''))
    if os.path.exists(fn):
        with open(fn, 'rb') as fp:
            return fp.read()
    content = urllib.urlopen(url).read()
    with open(fn, 'wb') as fp:
        fp.write(content)
    return content

_whitespace_re = re.compile(r'[\n\s]+')
_whitespace_min_re = re.compile(r'[ \t]+')
def norm_string(s, newline=True):
    if newline:
        return _whitespace_re.sub(' ', s.strip())
    else:
        return _whitespace_min_re.sub(' ', s.strip())

def import_community_board(row):
    """For data from: http://www.nyc.gov/html/dcp/html/bytes/dwndistricts.shtml"""
    b_id = str(row['BoroCD'])[0]
    borough = boroughs[int(b_id)]
    b_num = int(str(row['BoroCD'])[1:])
    community_url = base_community_url % borough.lower().replace(' ', '')
    body = forced_cache_get(community_url)
    page = html.fromstring(body, base_url=community_url)
    els = page.cssselect('table.cb_head')
    for el in els:
        if el.text_content().strip() == 'Community Board %s' % b_num:
            body = el.getnext()
            break
    else:
        #warnings.warn(
        #    "Could not find element %r (from %s)" %
        #    ('Community Board %s' % b_num,
        #     ', '.join([repr(html.tostring(e)) for e in els])))
        print 'Could not get info about %s Community Board %s' % (borough, b_num)
        body = None
    if body is not None:
        props = {'source_url': community_url,
                 'source_date': time.strftime('%Y%m%d-%H%M%S')}
        row['properties'] = {'board_info': props}
        els = body.cssselect('a[href^="mailto:"]')
        if els:
            props['email'] = els[0].get('href')[len('mailto:'):]
        els = [el for el in body.cssselect('a') if el.text_content().lower().replace(' ', '') == 'website']
        if els:
            props['website'] = els[0].get('href')
        els = [el for el in body.cssselect('td') if norm_string(el.text_content()).startswith('CB Address:')]
        if els:
            text = norm_string(html.tostring(els[0]))
            text = text.replace('<br>', '\n')
            text = norm_string(re.sub(r'<.*?>', '', text), False)
            assert text.startswith('CB Address:')
            text = text[len('CB Address:'):].strip()
            match = re.search(r'Email|Web\s+site', text)
            if match:
                text = text[:match.start()]
            props['contact'] = text
    row['name'] = '%s Community Board #%s' % (borough, b_num)
    row['uri'] = 'http://open311.org/community-board/%s/%s' % (borough.lower(), b_num)
    row['type_uri'] = 'http://open311.org/community-board'
    return row

