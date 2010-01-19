boroughs = {
    1: 'Manhattan',
    2: 'Bronx',
    3: 'Brooklyn',
    4: 'Queens',
    5: 'Staten Island',
    }


def import_community_board(row):
    b_id = str(row['BoroCD'])[0]
    borough = boroughs[int(b_id)]
    b_num = int(str(row['BoroCD'])[1:])
    row['name'] = '%s Community Board #%s' % (borough, b_num)
    row['uri'] = 'http://open311.org/community-board/%s/%s' % (borough.lower(), b_num)
    row['type_uri'] = 'http://open311.org/community-board'
    return row

