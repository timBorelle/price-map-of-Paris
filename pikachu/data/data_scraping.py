import requests
from bs4 import BeautifulSoup
import re
import psycopg2
from datetime import datetime
import time

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = {
        """
        CREATE TABLE IF NOT EXISTS aparts (
            listing_id INTEGER PRIMARY KEY,
            place_id INTEGER NOT NULL,
            price INTEGER,
            area INTEGER NOT NULL,
            room_count INTEGER NOT NULL,
            publication_date DATE NOT NULL
        )
        """
    }
    conn = None
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect("host=localhost dbname=meilleursagents user=meilleursagents password=meilleursagents")
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # commit the changes
        conn.commit()
        print("Table created.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            # close communication with the PostgreSQL database server
            conn.close()

def scraping_and_inserting_data():
    conn = psycopg2.connect("host=localhost dbname=meilleursagents user=meilleursagents password=meilleursagents")
    cur = conn.cursor()
    page_index = 1
    url = 'https://www.meilleursagents.com/annonces/achat/paris-75000/?item_types=ITEM_TYPE.APARTMENT,ITEM_TYPE.HOUSE'
    # custom headers (in order to avoid error 403)
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    apart_dict = []
    while True:
        full_url = url + '&page=' + str(page_index)
        print(full_url)
        response = requests.get(full_url, headers=HEADERS)
        print("page_index: " + str(page_index))
        if response.status_code == 200:             # or response.status_code == 301
            print('200 : OK')
        else:
            print(f'KO : {response.status_code}')
            cur.close()
            conn.close()
            exit(1)
        soup = BeautifulSoup(response.content , "html.parser")
        all_apart = soup.find_all('div', attrs={'class': "listing-item__content"})
        for apart in all_apart:
            listing_id = int(re.search('achat/(.+?)/', apart.a.get('href')).group(1))
            for d in apart.a.find_all('div'):
                if ' '.join(d["class"]) == "text--muted text--small":
                    district_number = int("".join(re.findall('\d+', d.text)))
                    place_id = 32681 + district_number
                if ' '.join(d["class"]) == "listing-price margin-bottom":
                    if re.search('.*Prix non communiqué.*', d.text, flags=re.IGNORECASE):
                        price = None                # "Prix non communiqué"
                    else:
                        price = int("".join(re.findall('\d+', d.text)))
                if ' '.join(d["class"]) == "listing-characteristic margin-bottom":
                    if re.findall('(\d+) *m', d.text):
                        area = int(re.findall('(\d+) *m', d.text)[0])
                    else:
                        area = -1                   # if the area is not specified in the title of the ad
                    if re.search('studio', d.text, flags=re.IGNORECASE):
                        room_count = 1
                    else:
                        if re.findall('(\d+) *pièces', d.text, flags=re.IGNORECASE):
                            room_count = int(re.findall('(\d+) *pièces', d.text, flags=re.IGNORECASE)[0])
                        else:
                            room_count = -1         # if the room count is not specified in the title of the ad
            publication_date = datetime.today().strftime('%Y-%m-%d')
            command = """
                INSERT INTO aparts (listing_id, place_id, price, area, room_count, publication_date)
                VALUES(%s,%s,%s,%s,%s,%s)
                ON CONFLICT (listing_id) DO UPDATE SET
                (place_id, price, area, room_count) = (EXCLUDED.place_id, EXCLUDED.price, EXCLUDED.area, EXCLUDED.room_count) 
            """
            cur.execute(command, (listing_id, place_id, price, area, room_count, publication_date))
            conn.commit()
        page_index += 1
        time.sleep(10)

create_tables()
scraping_and_inserting_data()
