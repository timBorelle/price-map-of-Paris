import requests
from bs4 import BeautifulSoup
import re

place_ids = str(32696) # + ',' + str(32697)
url = 'https://www.meilleursagents.com/annonces/achat/search/?item_types=ITEM_TYPE.APARTMENT,ITEM_TYPE.HOUSE&place_ids='+place_ids+'&page=1'
print(url)
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
response = requests.get(url, headers=HEADERS)
print("status_code : " + str(response.status_code))
if response.status_code == 200 or response.status_code == 301:
    print('200 : OK')
else:
    print('KO')
    exit(1)
soup = BeautifulSoup(response.content , "html.parser")
#print(soup.prettify())
#all_apart = soup.find('div', attrs={'class': "search-listing-result__content"})
all_apart = soup.find_all('div', attrs={'class': "listing-item__content"})
#listing_price = soup.select('.listing-price.margin-bottom')
#print('listing_price')
#print(listing_price)
#print(all_apart)
apart_dict = []
for apart in all_apart:
    listing_id = int(re.search('achat/(.+?)/', apart.a.get('href')).group(1))
    print(type(apart))      # <class 'bs4.element.Tag'>
    print("apart")
    #print(apart.a.find_all('div'))
    for d in apart.a.find_all('div'):
        #print()
        print("d: " + str(d))
        print("d[class] " + str(d["class"]))
        print("d.text " + str(d.text))
        if ' '.join(d["class"]) == "listing-price margin-bottom":
        #    print(d)
        #    print(d.text)
        #    price = int(d.text)
        #if d[0] == "listing-characteristic margin-bottom":
        #    area = int(0)
        #    room_count = int(0)
            #price = d.text
            price = int("".join(re.findall('\d+', d.text)))
        if ' '.join(d["class"]) == "listing-characteristic margin-bottom":
            print('before area')
            print(d.text)
            print(type(d.text))
            #print(re.search('-.*(\d+).*m', d.text).group(1))
            print(str(re.findall('- (\d+)', d.text)))
            area_string = str(re.findall('- (\d+)', d.text)[0])
            print(area_string)
            #print(re.search('(\d+) m', d.text))
            area = int(area_string)     # int(re.search('(\d+) m', d.text))
            print('area : ' + str(area))
            #print(re.findall('(\d+) pièces', d.text))
            if re.search('studio', d.text, flags=re.IGNORECASE):
                print("Studio found !")
                room_count = 2
            else:
                match = re.findall('(\d+).*pièces', d.text, flags=re.IGNORECASE)
                print(match[0])
                room_count = int(match[0])
    #print('listing_id : ' + str(listing_id))  
    #place_id = apart.f       # ex: 32696 (Paris 15)
    row = {'listing_id': listing_id, 'place_id': '', 'price': price, 'area': area, 'room_count': room_count}
    print('row : ' + str(row))
    apart_dict.append(row)
#price_list = [price.a.div for price in all_apart]
#print(price_list)
# extract from title item


print(len(all_apart))
