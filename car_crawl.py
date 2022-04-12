import requests

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
}

autohome_base_url   =   'https://car.autohome.com.cn/diandongche/'
autohome_brand_dict =   {'Tesla'    :   'brand-133.html',
                         'Porche'   :   'brand-40.html' , 
                         'VW'       :   'brand-1.html'  ,
                         'LI Auto'  :   'brand-345.html',
                         'ZEEKR'    :   'brand-456.html',
                         'NIO'      :   'brand-284.html',
                         'XPENG'    :   'brand-275.html',
                         'MB'       :   'brand-36.html' ,
                         'BMW'      :   'brand-15.html'
                         }

if __name__ == '__main__':
    url = autohome_base_url + autohome_brand_dict['Tesla']
    response = requests.get(url = url, headers = headers)
    print(response.text)