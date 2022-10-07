import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
from IPython.display import display
import sys



url = 'https://r.gnavi.co.jp/area/jp/japanese/rs/?sc_lid=cp_home_genre_japanese'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15'
header = {
      'User-Agent': user_agent
  }

shop_data = []
columns = ['店舗名','電話番号','都道府県','市区町村','番地','建物名','URL','SSL','メールアドレス']

  # GetSoup()
def GetPage (url):
  time.sleep(3)
  response = requests.get(url, headers = header)
  page = BeautifulSoup(response.content, 'html.parser')
  #print(page)
  return page

page = GetPage(url)
GetPage(url)

# GetInfo (takes: soup, returns: Info)
#GetName
def GetName(shoppage):
    find_name = shoppage.find(id='info-name')
    shop_name = find_name.text.replace(' ','').replace('\xa0',' ')
    return shop_name

#GetNumber
def GetNumber(shoppage):
    shop_number = shoppage.find('li', class_='contact-phone').text[3:]
    return shop_number

#GetAddress
def GetAddress(shoppage):
  get_address = shoppage.find('p', class_='adr slink').text
  address = get_address.replace(' ', '').replace('\n', '')
  return address

#pref  
def GetPref(address):
  pref = re.search('\w*県|\東京都|\w*府|\w*道', address).group()
  return pref

def GetCity(address):
  #city
  split = re.split('[県都府道]',address)
  add_others = split[1]
  global add1_g
  add1_g = re.split(r'(^[^\d]+)', add_others)[1:]   
  if add1_g:   
    if len(add1_g) == 2:
      city= add1_g[0]
      return city
    else:
      return ''
  else:
    '住所なし'

def GetAddressNumber(address):
  if add1_g:
    if len(add1_g) == 2:
      add1_c = add1_g[1].replace('\xa0', ' ')
      global add2_g
      add2_g = re.split('[ ]',add1_c)
      add_num = add2_g[0]
      return add_num
    else:
      return add1_g[0]
  else:
    return '住所なし'

def  GetBuilding(address):
  if add2_g:
    if len(add2_g) == 2:
      building = add2_g[1]
                  #building_tags.append(building)
      return building
    else:
      return 'ビルなし'

#GetURL
def GetURL(shoppage):
  find_official_url = shoppage.find('a', class_='sv-of double',href=True)
  if find_official_url:
    official_url = find_official_url['href']
    get_url = requests.request("GET", official_url)
    global HP_url
    HP_url = get_url.url
    return HP_url
  else:
    return "なし"

#CheckSSL
def CheckSSL(shoppage):
    https = '^https?:\/\/'
    if re.match(https, HP_url):
        return 'True'
    else: 
        return 'False'

#GetMail
def GetMail(shoppage):
  find_email_address = shoppage.find('a[href^=mailto]')
  ext_email = re.findall('\:(.*)\"',str(find_email_address))
  if ext_email:
      return ext_email
  else:
      return 'なし'

def GetInfo(url):
  time.sleep(3)
  response = requests.get(url, headers = header)
  page = BeautifulSoup(response.content, 'html.parser')
  href_tags = page.find_all('a', class_= 'style_titleLink__oiHVJ',href=True)
  for href in href_tags:
    each_url = href['href']
    shoppage = GetPage(each_url)
    shop_name = GetName(shoppage)
    shop_number = GetNumber(shoppage)
    address = GetAddress(shoppage)
    if address:
      pref = GetPref(address)
      add_num = GetAddressNumber(address)
      building = GetBuilding(address)

    HPURL = GetURL(shoppage)
    SSL = CheckSSL(shoppage)
    mail_address = GetMail(shoppage)


    shop_info = [shop_name,shop_number,pref,city, add_num,building,HPURL,SSL,mail_address]
    shop_data.append(shop_info)
  return shop_data
    
def main ():
  page_number = 3
  GetInfo(url) 
  i = 0
  for i in range(page_number):
      i += 1
      next_page_element  = page.find('a', tabindex="0", href = True)
      next_url_base = next_page_element['href']
      time.sleep(5)
      next_url = 'https://r.gnavi.co.jp'+ next_url_base + '?p=' + str(i+1)
      updated_shop_data = GetInfo(next_url)

      if len(updated_shop_data) == 50:
        break


main()
shop_data_csv = shop_data[0:50]
d2 = pd.DataFrame(shop_data_csv, columns = columns)
d2.to_csv("1-6.csv")

