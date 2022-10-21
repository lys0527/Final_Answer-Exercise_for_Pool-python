import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd

url = 'https://r.gnavi.co.jp/area/jp/japanese/rs/?sc_lid=cp_home_genre_japanese'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15'
header = {
      'User-Agent': user_agent
  }

name_tags= []
number_tags=[]
pref_tags= []
city_tags= []
add_num_tags= []
building_tags= []
url_tags= []
ssl_check= []
mail_tags= []

shop_data = []

columns = ['店舗名','電話番号','メールアドレス','都道府県','市区町村','番地','建物名','URL','SSL']
df = pd.DataFrame(columns=columns)


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
    ' '

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
    return ' '
def  GetBuilding(address):
  if add2_g:
    if len(add2_g) == 2:
      building = add2_g[1]
                  #building_tags.append(building)
      return building
    else:
      return ' '


#GetURL
def GetURL(shoppage):
  find_official_url = shoppage.find('a', class_='url go-off',href=True)
  if find_official_url:
    # official_url = find_official_url['href']
    # get_url = requests.request("GET", official_url)
    # global HP_url
    # HP_url = get_url.url
    return ' '
  else:
    return " "

#CheckSSL
def CheckSSL(shoppage):
    https = '^https?:\/\/'
    # if re.match(https, HP_url):
    return ' '
    # else: 
    #     return ' '

#GetMail
def GetMail(shoppage):
  find_email_address = shoppage.find('a[href^=mailto]')
  ext_email = re.findall('\:(.*)\"',str(find_email_address))
  if ext_email:
      return ext_email
  else:
      return ' '

def GetInfo(url):
  time.sleep(3)
  response = requests.get(url, headers = header)
  page = BeautifulSoup(response.content, 'html.parser')
  href_tags = page.find_all('a', class_= 'style_titleLink__oiHVJ',href=True)
  # i = 0
  for href in href_tags:
    #i += 1
    each_url = href['href']
    shoppage = GetPage(each_url)
    shop_name = GetName(shoppage)
    name_tags.append(shop_name)

    shop_number = GetNumber(shoppage)
    number_tags.append(shop_number)
    address = GetAddress(shoppage)
    if address:
      pref = GetPref(address)
      pref_tags.append(pref)
      city = GetCity(address)
      city_tags.append(city)
      add_num = GetAddressNumber(address)
      add_num_tags.append(add_num)
      building = GetBuilding(address)
      building_tags.append(building)
    HPURL = GetURL(shoppage)
    url_tags.append(HPURL)
    SSL = CheckSSL(shoppage)
    ssl_check.append(SSL)
    mail_address = GetMail(shoppage)
    mail_tags.append(mail_address)

    shop_info = [shop_name,shop_number,mail_address,pref,city, add_num,building,HPURL,SSL]
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
d = pd.DataFrame(shop_data_csv, columns = columns)
d.to_csv("1-1.csv", index = False, encoding="shift-jis")

