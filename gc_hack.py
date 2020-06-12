# import requests
import re
import sqlite3
import time
from requests_html import HTMLSession
from itertools import permutations

# Initialize
gid = '249971030fb-5db4-45f2-a4ec-2e2312ca63d9'
gid = '6371353e6d45420-ab85-4673-88db-3c8e7082b65d'
gc_input_url = f'http://geocheck.org/geo_inputchkcoord.php?gid={gid}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
}
table_filename = 'rainbow.sqlite'
given_solution = 'N10°10.100, W10°10.100'
#                 N1010100W01010100

gc_filename = 'geocheck.sqlite'

conn_gc = sqlite3.connect(gc_filename)
c_gc = conn_gc.cursor()
# c_gc.execute("CREATE TABLE geocheck (gccode text, coord text, test text)")
conn_gc.commit()

# Generate coordinates
coords = []

digits = [7, 6, 2, 3, 1, 4]
p_iter = permutations(digits)
for p in p_iter:
    coords.append(f'N5057{p[0]}{p[1]}{p[2]}E00410{p[3]}{p[4]}{p[5]}')

# HTML query
session = HTMLSession()
response = session.get(gc_input_url, headers=headers)

# Open rainbow database
conn = sqlite3.connect(table_filename)
c = conn.cursor()

found = False
coords_index = 720
while not found:
    # TODO: If something fails, sleep and retry same coords
    # TODO: Get coords from table geocheck
    # Retrieve data for POST payload
    cachename = None
    gccode = None
    inputs = response.html.find('input')
    for i in inputs:
        if 'name' in i.attrs:
            if i.attrs['name'] == 'cachename':
                cachename = i.attrs['value']
            if i.attrs['name'] == 'gccode':
                gccode = i.attrs['value']

    # Retrieve number of failed attempts
    alert = response.html.find('.alert')
    if alert and 'You have exceeded the limit' in alert[0].text:
        print('Sleeping')
        time.sleep(70)
        response = session.get(gc_input_url, headers=headers)
        continue
    attempts_text = 'x attempts'
    attempts = response.html.find('.attemptred')
    if not attempts:
        attempts = response.html.find('.attemptyellow')
    if not attempts:
        attempts = response.html.find('.attemptnorm')
    if attempts:
        attempts_text = attempts[0].text
    else:
        attempts_text = 'x attempts'
        print('-------------')
        print(response.text)
        print('no alert, no attempts')
        exit()

    # Retrieve MD5 hash
    geoform = response.html.find('form', containing=['Enter this code'])[0]
    onsubmit_text = geoform.attrs['onsubmit']
    r = re.search("return validateChkCoordsForm\(this,'(.*)'\)", onsubmit_text)
    md5_code = r.group(1)

    # Find code value in rainbow table
    t = (md5_code,)
    c.execute("SELECT code from rainbow WHERE hash=?", t)
    code = c.fetchall()[0][0]

    # Save image (optional)
    image_filename = f'images\check_{code}.png'
    image_captcha = session.get('http://geocheck.org/geocheck_captcha.php', allow_redirects=True, headers=headers)
    with open(image_filename, 'wb') as f:
        f.write(image_captcha.content)

    # POST coordinates
    this_coord = coords[coords_index]

    # TODO: check if coord is available in db
    print(f'Testing coords {coords_index}: {this_coord} with code {code}', end='\r')

    payload = {'gid': gid,
               'cachename': cachename,
               'gccode': gccode,
               'coordOneField': this_coord,
               'usercaptcha': str(code)
               }
    gc_check_url = f'http://geocheck.org/geo_chkcoord.php?gid={gid}'
    response = session.post(gc_check_url, data=payload)
    result = response.html.find('.geo')
    # print(response.text)
    result_text = ''
    for r in result:
        result_text += r.text
    congrat_test = result_text.find('Congratulations')
    check_test = result_text.find('Check your coordinates')
    # print(result_text.splitlines()[:2])
    # print(f'test: {test}')
    if congrat_test >= 0:
        print(f'Testing coords {coords_index}: {this_coord} with code {code}: Found !!!')

        c_gc.execute("INSERT INTO geocheck VALUES (?, ?, ?)", (gccode, this_coord, 'SUCCESS'))
        conn_gc.commit()

        found = True
        print(result_text)
    elif check_test >= 0:
        print(f'Testing coords {coords_index}: {this_coord} with code {code}: Not found. {attempts_text}')

        c_gc.execute("INSERT INTO geocheck VALUES (?, ?, ?)", (gccode, this_coord, 'FAIL'))
        conn_gc.commit()

        sleep_time = 61
        r = re.search('made (\d+) attempt', attempts_text)
        if r:
            attempts_num = int(r.group(1))
            sleep_time = 60 + 1 + attempts_num
            if attempts_num > 9:
                sleep_time = 90
                coords_index -= 1
        print(f'Sleep time: {sleep_time}')
        print(f'Testing coords {coords_index+1}: {coords[coords_index+1]} : Sleeping {sleep_time}s.', end='\r')
        coords_index += 1
        time.sleep(sleep_time)
    else:
        print(f'Testing coords {coords_index}: {this_coord} with code {code}: Error. {attempts_text}')
        print(result_text)
        print(f'Testing coords {coords_index}: {this_coord} : Sleeping', end='\r')
        time.sleep(90)

conn.close()
conn_gc.close()
