from lxml import html
import re
import time
import os
import urllib
import warnings
import type_uris

CACHE_DIR = os.path.join(os.environ['HOME'], '.httplib2-cache')
if not os.path.exists(CACHE_DIR):
    try:
        os.makedirs(CACHE_DIR)
    except OSError:
        # No good using $HOME, let's try a temp location:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            CACHE_DIR = os.tempnam()
        os.makedirs(CACHE_DIR)

########################################
## Community Board stuff:
########################################

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
    row['type_uri'] = type_uris.COMMUNITY_BOARD
    return row

########################################
## Assembly Districts
########################################

def import_assembly(row):
    n = int(row['AssemDist'])
    row['name'] = 'Assembly District %s' % n
    row['uri'] = 'http://assembly.state.ny.us/mem/?ad=%s' % n
    row['type_uri'] = type_uris.NY_ASSEMBLY_DISTRICT
    return row



########################################
## Cities
########################################
def import_dc(row):
    # Washington, DC
    rows = []
    row['name'] = 'Washington, DC'
    row['uri'] = row['WEB_URL']
    row['type_uri'] = type_uris.GOV_MAIN_SITE
    rows.append(row)

    row = row.copy()
    row['uri'] = 'http://api.dc.gov/open311/v2/'
    row['type_uri'] = type_uris.OPEN311_API
    rows.append(row)
    return rows

def import_file_sfoutline(row):
    # San Francisco
    rows = []
    row['name'] = 'San Francisco'
    row['uri'] = 'https://open311.sfgov.org/dev/V1/'
    row['type_uri'] = type_uris.OPEN311_API
    rows.append(row)

    row = row.copy()
    row['uri'] = 'http://www.sfgov.org/'
    row['type_uri'] = type_uris.GOV_MAIN_SITE
    rows.append(row)
    return rows

########################################
## Boroughs
########################################

# I could link to president offices or something, but eh...
borough_links = {
    'Manhattan': 'http://en.wikipedia.org/wiki/Manhattan',
    'The Bronx': 'http://en.wikipedia.org/wiki/The_Bronx',
    'Brooklyn': 'http://en.wikipedia.org/wiki/Brooklyn',
    'Queens': 'http://en.wikipedia.org/wiki/Queens',
    'Staten Island': 'http://en.wikipedia.org/wiki/Staten_Island',
    }

def import_borough(row):
    row['name'] = row['BoroName']
    row['uri'] = borough_links[row['name']]
    row['type_uri'] = type_uris.NYC_BOROUGH
    return row

########################################
## City Council
########################################

def import_city_council(row):
    n = int(row['CounDist'])
    row['uri'] = 'http://council.nyc.gov/d%s/html/members/home.shtml' % n
    row['name'] = 'New York City Council District %s' % n
    row['type_uri'] = type_uris.NYC_COUNCIL
    return row

########################################
## Congressional District
########################################

def import_congressional_district(row):
    n = row['CongDist']
    row['name'] = 'New York Congressional District %s' % n
    url = 'http://www.house.gov/house/MemberWWW_by_State.shtml'
    page = forced_cache_get(url)
    page = html.fromstring(page, base_url=url)
    lis = page.cssselect('li')
    ord_re = re.compile(r'%s(?:st|nd|rd|th)' % n, re.I)
    for li in lis:
        if 'New York' not in li.text_content():
            continue
        if ord_re.search(li.text_content()):
            anchors = li.cssselect('a')
            if not anchors:
                print 'Weird li: %s' % html.tostring(li)
            else:
                row['uri'] = anchors[0].get('href')
                break
    else:
        print 'No uri found for %s district' % n
    row['type_uri'] = type_uris.CONGRESSIONAL_DISTRICT
    return row

########################################
## Educational District
########################################

def import_election_district(row):
    n = row['ElectDist']
    row['name'] = 'New York Election District %s' % n
    ## FIXME: obviously this is fake; I can't find any useful district information:
    row['uri'] = 'http://example.com/ny-election-district/%s' % n
    row['type_uri'] = type_uris.NYC_ELECTION_DISTRICT
    return row

########################################
## Health Area
########################################

def import_health_area(row):
    n = row['HealthArea']
    row['name'] = 'New York Health Area %s' % n
    ## FIXME: no URLs found:
    row['uri'] = 'http://example.com/nyc-health-area/%s' % n
    row['type_uri'] = type_uris.NYC_HEALTH_AREA
    return row

########################################
## Health Center
########################################

def import_health_center(row):
    n = row['HCentDist']
    row['name'] = 'New York Health Center District %s' % n
    row['uri'] = 'http://example.com/nyc-health-center/%s' % n
    row['type_uri'] = type_uris.NYC_HEALTH_CENTER
    return row

########################################
## Municipal Court Districts
########################################

## FIXME: there's a second court in both Manhattan and Brooklyn:
borough_court_links = {
    'The Bronx': 'http://www.nycourts.gov/courts/nyc/criminal/generalinfo.shtml#BRONX COUNTY',
    'Brooklyn': 'http://www.nycourts.gov/courts/nyc/criminal/generalinfo.shtml#KINGS COUNTY',
    'Manhattan': 'http://www.nycourts.gov/courts/nyc/criminal/generalinfo.shtml#NEW YORK COUNTY',
    'Queens': 'http://www.nycourts.gov/courts/nyc/criminal/generalinfo.shtml#QUEENS COUNTY',
    'Staten Island': 'http://www.nycourts.gov/courts/nyc/criminal/generalinfo.shtml#RICHMOND COUNTY',
    }

def import_municipal_district(row):
    row['name'] = 'Municipal Court District %s' % row['MuniCourt']
    row['uri'] = borough_court_links[row['BoroName']]
    row['type_uri'] = type_uris.MUNICIPAL_COURT_DISTRICT
    return row

########################################
## Police Precinct
########################################

def import_police_precinct(row):
    n = row['Precinct']
    row['uri'] = 'http://www.nyc.gov/html/nypd/html/precincts/precinct_%03i.shtml' % n
    row['name'] = 'New York City Police Precinct %s' % n
    row['type_uri'] = type_uris.POLICE_PRECINCT
    return row

########################################
## School District
########################################

def import_school_district(row):
    n = row['SchoolDist']
    row['name'] = 'New York School District %s' % n
    ## FIXME: I'm sure there's a better link, but I haven't found it:
    row['uri'] = 'http://example.com/nyc-school-district/%s' % n
    row['type_uri'] = type_uris.SCHOOL_DISTRICT
    return row

########################################
## State Senate
########################################

def import_state_senate(row):
    n = row['StSenDist']
    row['name'] = 'New York State Senate District %s' % n
    row['uri'] = 'http://www.nysenate.gov/district/%s' % n
    row['type_uri'] = type_uris.STATE_SENATE
    return row

########################################
## Definitions
########################################

import_routines = {
    # Assembly Districts:
    'nyad_09bav': import_assembly,
    # Boroughs:
    'nybb_09bav': import_borough,
    # City Council:
    'nycc_09bav': import_city_council,
    # Community Districts:
    'nycd_09bav': import_community_board,
    # Congressional District:
    'nycg_09bav': import_congressional_district,
    # Election District:
    'nyed_09bav': import_election_district,
    # Health Areas:
    'nyha_09bav': import_health_area,
    # Health Center District:
    'nyhc_09bav': import_health_center,
    # Municipal Court District:
    'nymc_09bav': import_municipal_district,
    # Police Precinct:
    'nypp_09bav': import_police_precinct,
    # School District:
    'nysd_09bav': import_school_district,
    # State Senate:
    'nyss_09bav': import_state_senate,

    # Cities:
    'DCBndyPly': import_dc,

    }

for _name, _func in import_routines.items():
    globals()['import_file_%s' % _name] = _func
