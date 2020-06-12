import requests
from lxml.html import fromstring
from itertools import cycle
import traceback

# https://www.scrapehero.com/how-to-rotate-proxies-and-ip-addresses-using-python-3/

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr'):
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            if proxy.split(':')[1] in ['8080', '80', '443', '8000', '1080']:
                proxies.add(proxy)
    return proxies

proxies = get_proxies()
print(proxies)
print(len(proxies))
proxy_pool = cycle(proxies)


url = 'http://195.234.45.110/gc/mb-jette/go.php'
for i in range(1, 21):
    #Get a proxy from the pool
    proxy = next(proxy_pool)
    print("Request #%d"%i)
    try:
        response = requests.get(url, proxies={"http": proxy, "https": proxy})
        print(response)
    except:
        #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
        #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
        print("Skipping. Connnection error")