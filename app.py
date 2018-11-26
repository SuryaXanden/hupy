import re
import json
import requests
from flask import Flask, redirect, url_for, request, render_template, jsonify
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41 Safari/537.36'}
budget = 0.0
item = ''
results = set()
#^ empty results set

def atd(img,link,price,title): #function to append data to the results set
    global results
    results.add((img,link,price,title))
    return

def makeList(): #converting the results set into a list
    global results
    results = [list(i) for i in results]
    return

def sortByPrice(): #function to sort the results set based on the items' price
    global results
    try:
        results = sorted(results, key=lambda x: x[2])
    except:
        pass
    return

def sanitizeAmazon(tempap): #function to sanitize the "Price" attribute from Amazon's result
    san = re.sub(r"\,", '', tempap, 0, re.MULTILINE)
    san = float(san)
    return san

def makeJSON():
    global results
    makeList()
    sortByPrice()
    JSON = dict()
    scraped_item = 0    
    if len(results) > 0 :
        for i in results:
            scraped_item += 1
            try:
                JSON[scraped_item] = {  "img" : str(i[0]),
                                    "link" : str(i[1]),
                                    "price" : float(i[2]),
                                    "title" : str(i[3])
                                }
            except:
                pass
            results = json.dumps(JSON)
    else:
        pass
    return

def ip():
    global budget,item
    budget = float(budget)
    budget = float(budget * 1.1) #uncomment 
    item = item.strip()
    return (item,budget)

def FPNum(ip):
    point = 0
    extracted = ''
    # ^ defaults
    
    for num in ip:
        if num >= '0' and num <= '9':
            extracted += num
        if num is '.':
            point += 1
            if point < 2:
                extracted += num
            else:
                break
    
    return float(extracted)

def genrateFlipkartResultDivSelectorLists(div):
    check_title = []
    check_price = []
    check_link = []
    for nod in range(2,div+2):
        for subdiv in range(1,5):
            
            check_title.append(str('div > div > div > div > div > div > div:nth-of-type(' + str(nod) + ') > div > div:nth-of-type(' + str(subdiv) + ') > div > a > div:nth-of-type(1) > div > div > img'))            
            check_link.append(str('div > div > div > div > div > div > div:nth-of-type(' + str(nod) + ') > div > div:nth-of-type(' + str(subdiv) + ') > div > a'))
            check_price.append(str('div > div > div > div > div > div > div:nth-of-type(' + str(nod) + ') > div > div:nth-of-type(' + str(subdiv) + ') > div > a > div > div'))

    return(check_link,check_price,check_title)

## <--- Scraping logic --->
## AMAZON
def amazon():
    global headers
    item,budget = ip()
    url = str("https://www.amazon.in/s/ref=sr_st_price-asc-rank?keywords="+ str(item) + '  ' + str(budget) + '')
    # url = str("https://www.amazon.in/s/ref=sr_st_price-asc-rank?keywords="+ str(item) + ' below ' + str(budget) + '')
    page = requests.get(url,headers)
    soup = BeautifulSoup(page.content,'html.parser')

    main_ul = soup.find('ul', id = 's-results-list-atf')
    # lis = main_ul.findAll('li')

    try:
        for li in main_ul:
            maindiv = li.div.div
            a_tag = maindiv.div.a
            link = str(a_tag['href'])
            if not (link is None):
                img = str(a_tag.img['src'])
                title = str(a_tag.img['alt'])
                if not (img is None):
                    checking = (
                                    maindiv.div.div.find_next_sibling('div').div.find_next_sibling('div').div.div.a.get_text()
                                ).strip().split(" ")
                price = float(sanitizeAmazon(str(checking[0])))
                if price <= budget:
                    atd(img,link,price,title)
    except:
        pass
    return
## FLIPKART
def flipkart():
    global headers
    # url = str("https://www.flipkart.com/search?sort=relevance&q="+ str(item) + ' below ' + str(budget) + '')
    url = str("https://www.flipkart.com/search?sort=relevance&q="+ str(item) + '  ' + str(budget) + '')
    page = requests.get(url,headers)
    soup = BeautifulSoup(page.content,'html.parser')

    mainDiv = soup.find('div', id = 'container')
    check_link, check_price, check_title = genrateFlipkartResultDivSelectorLists(2)
    try:
        links = []
        for sel in check_link:
            link = mainDiv.select(sel)[0]
            link = str('flipkart.com'+ link['href'])
            links.append(link)
        
        prices = []
        for sel in check_price:
            price = mainDiv.select(sel)[2]
            price = FPNum(price.get_text())
            prices.append(price)

        titles = []
        for sel in check_title:
            title = mainDiv.select(sel)[0]
            titles.append(str(title['alt']))

        for i in range(len(links)):
            if prices[i] <= budget:
                atd('img1a.flixcart.com/www/linchpin/fk-cp-zion/img/fk-logo_9fddff.png',links[i],prices[i],titles[i])
    except:
        pass            
    return
## SNAPDEAL
def snapdeal():
    global headers
    url = str("https://www.snapdeal.com/search?sort=rlvncy&keyword="+ str(item) + '   ' + str(budget) + '')
    # url = str("https://www.snapdeal.com/search?sort=rlvncy&keyword="+ str(item) + ' below ' + str(budget) + '')
    page = requests.get(url,headers)
    soup = BeautifulSoup(page.content,'html.parser')
    
    mainDiv = soup.find('div', id = 'products')
    try:    
        images = []
        for it in mainDiv.select('section:nth-of-type(1) > div > div:nth-of-type(2) > a > picture > img'):
            images.append(it['src'])
        for it in mainDiv.select('section:nth-of-type(2) > div > div:nth-of-type(2) > a > picture > img'):
            images.append(it['data-src'])

        links = []
        for it in mainDiv.select('section:nth-of-type(1) > div > div:nth-of-type(2) > a'):
            links.append(it['href'])
        for it in mainDiv.select('section:nth-of-type(2) > div > div:nth-of-type(2) > a '):
            links.append(it['href'])

        prices = []
        prices1 = mainDiv.select('section:nth-of-type(1) > div > div:nth-of-type(3) > div > a > div > div > span:nth-of-type(2)')
        prices.append((prices1[0].get_text()[5:]).replace(',',''))
        prices.append((prices1[2].get_text()[5:]).replace(',',''))
        prices.append((prices1[5].get_text()[5:]).replace(',',''))
        prices.append((prices1[7].get_text()[5:]).replace(',',''))
        
        prices2 = mainDiv.select('section:nth-of-type(2) > div > div:nth-of-type(3) > div > a > div > div > span:nth-of-type(2)')
        prices.append((prices2[0].get_text()[5:]).replace(',',''))
        prices.append((prices2[2].get_text()[5:]).replace(',',''))
        prices.append((prices2[5].get_text()[5:]).replace(',',''))
        prices.append((prices2[7].get_text()[5:]).replace(',',''))

        for all in range(len(prices)):
            prices[all] = float(prices[all])

        titles = []
        for it in mainDiv.select('section:nth-of-type(1) > div > div:nth-of-type(2) > a > picture > img'):
            titles.append(it['title'])
        for it in mainDiv.select('section:nth-of-type(2) > div > div:nth-of-type(2) > a > picture > img'):
            titles.append(it['title'])

        for i in range(len(links)):
            if prices[i] <= budget:
                atd(images[i],links[i],prices[i],titles[i])
    except:
        pass
    return
##<---FLOW--->
def flow():
    # Invoke scrape functions
    ip()
    global item,budget,results
    #comment these
    # item = 'shoes'
    # budget = '2000'
    dummy = amazon()
    dummy = flipkart()
    dummy = snapdeal()
    # PROCESS
    makeJSON()
    return jsonify(results)
    results = []
#flow()

@app.route("/")
def index():
    try:
        x = request.args.get('x')
        prod = request.args.get('prod')
        price = request.args.get('price')
        if(x):
            if(x == '1CE15CS145'):
                if(prod):
                    if(price):
                        if prod not in ('prod','Prod','PROD') and price not in ('price','Price','PRICE'):
                            global item,budget,results
                            item = prod
                            budget = price                        
                            flow()
                            if not (results is None):
                                return(results)
                            elif len(results) is 0:
                                return("Nothing :(")
                        else:
                            return ("DUMMY!")
            else:
                return('Invalid Secret Key!')
        else:
            return "Usage: URL/?x=SECRET&prod=PRODUCT&price=PRICE<br> With no tailing '/'<br><br>"
    except:
        return('Request Dead')

if __name__ == '__main__':
<<<<<<< HEAD:app.py
    app.run()
=======
    app.run(debug=True)
>>>>>>> c0045295ce59e3f7e0b615d24386197ca2c6c651:app.py
