import copy
import requests
from bs4 import BeautifulSoup
import re
import os

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
}

autohome_base_url   =   'https://car.autohome.com.cn/diandongche/'
autohome_brand_dict =   {'Tesla'            :   'brand-133.html',
                         'Porche'           :   'brand-40.html' , 
                         'Volkswagen'       :   'brand-1.html'  ,
                         'ZEEKR'            :   'brand-456.html',
                         'NIO'              :   'brand-284.html',
                         'XPENG'            :   'brand-275.html',
                         'Mercedes-Benz'    :   'brand-36.html' ,
                         'BMW'              :   'brand-15.html' ,
                         'BYD'              :   'brand-75.html' ,
                         'AITO'             :   'brand-509.html',
                         'ARCFOX'           :   'brand-272.html',
                         'Honda'            :   'brand-14.html' ,
                         'TOYOTA'           :   'brand-3.html'  ,
                         'Marvel-R'         :   'brand-438.html',
                         'Ford'             :   'brand-8.html'  ,
                         'Polestar'         :   'brand-308.html',
                         'Audi'             :   'brand-33.html' ,
                         'Volvo'            :   'brand-70.html' ,
                         'Hyandai'          :   'brand-12.html' ,
                         'WULING'           :   'brand-114.html',
                         'WM Motor'         :   'brand-291.html',
                         'Chery'            :   'brand-487.html',
                         'Ora'              :   'brand-331.html',
                         'Hozonauto'        :   'brand-309.html',
                         'Cadillac'         :   'brand-47.html' ,
                         'Lexus'            :   'brand-52.html' ,
                         'Leapmotor'        :   'brand-318.html',
                         'GEELY'            :   'brand-25.html' ,
                         'Jaguar'           :   'brand-44.html' ,
                         'Geometry'         :   'brand-373.html',
                         'GAC AION'         :   'brand-313.html',
                         'HiPhi'            :   'brand-383.html',
                         'Hongqi'           :   'brand-91.html' ,
                         'Hycan'            :   'brand-376.html',
                         'Smart'            :   'brand-45.html' ,
                         'Venucia'          :   'brand-122.html',
                         'Mazda'            :   'brand-58.html' ,
                         'Skyworth'         :   'brand-400.html',
                         'Aiways'           :   'brand-327.html'
                         }

class Brand:

    def __init__(self, name="None", url="None", model_tree=[]):
        self.name = name
        self.url = url
        self.model_tree = model_tree
        
    def __str__(self):
        brand_str = f"Brand: {self.name}\nURL: {self.url}\nModels:\n\n"
        for model in self.model_tree:
            brand_str = brand_str + model.__str__()
        return brand_str
    
class Model:
    
    def __init__(self, name="None", type="None", endurance=[0,0], power=[0, 0], 
                 price_range=[0, 0], score=0.0, charging_time=[0.0, 0.0],
                 version_tree=[]):
        self.name = name
        self.type = type
        self.endurance = endurance
        self.power = power
        self.price_range = price_range
        self.score = score
        self.charging_time = charging_time
        self.version_tree = version_tree
        
    def __str__(self):
        model_str = f"\tModel: {self.name}\n\tType: {self.type}\n\tHorse Power: {self.power[0]} ~ {self.power[1]}\n\t"
        model_str = model_str + f"Price Range: RMB {self.price_range[0]} ~ {self.price_range[1]} * 10000\n\t"
        model_str = model_str + f"Score: {self.score} / 5.0\n\t"
        model_str = model_str + f"Endurance: {self.endurance[0]}km ~ {self.endurance[1]}km\n\t"
        model_str = model_str + f"Charging Time: Fast Charging {self.charging_time[0]}H, Slow Charging {self.charging_time[1]}H\n\t"
        model_str = model_str + f"Versions:\n\n"
        for version in self.version_tree:
            model_str = model_str + version.__str__()
        return model_str
            
class Version:
    def __init__(self, name="None", price=0.0, url="None"):
        self.name = name
        self.price = price
        self.url = url
        
    def __str__(self):
        version_str = f"\t\tVersion: {self.name}\n\t\tPrice: {self.price} * 10000\n\t\tURL: {self.url}\n\n"
        return version_str
    
class Form:
    def __init__(self, user="X", type=0, size=0, endurance=[0, 0], 
                 price_range=[0.0, 0.0]):
        self.user = user
        self.type = type
        self.size = size
        self.endurance = endurance
        self.price_range = price_range
        
    def __str__(self):
        if self.type == 0:
            type_str = "Not Specified"
        elif self.type == 1:
            type_str = "SUV"
        else:
            type_str = "Sedan"
            
        if self.size == 0:
            size_str = "Not Specified"
        elif self.size == 1:
            size_str = "Subcompact"
        elif self.size == 2:
            size_str = "Compact"
        elif self.size == 3:
            size_str = "Mid-size"
        else:
            size_str = "Large"
            
        form_str = f"Your Name: {self.user}\nType: {type_str}\nSize: {size_str}\nEndurance: {str(self.endurance[0])} ~ {str(self.endurance[1])}\nPrice: RMB {str(self.price_range[0])} ~ {str(self.price_range[1])} * 10000"
        return form_str
        
def request_brand(brand):
    """Request the data for one brand

    Args:
        brand (string): brand name
    """
    # Set URL
    url = autohome_base_url + autohome_brand_dict[brand]
    # Request URL
    response = requests.get(url = url, headers = headers)
    # Call BS
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract the list of models
    all_models = soup.find_all('div', class_='list-cont')
    all_model_verions = soup.find_all('div', class_='intervalcont')
    
    model_tree = []
    for model in all_models:
        # Initialize Values
        model_name = "None"
        endurance_list = [0, 0]
        power_list = [0, 0]
        charging_time_list = [0, 0]
        model_type = "None"
        model_score = 0.0
        price_range_list = [0.0, 0.0]
        # Scrape the titles, which are the names of Models
        model_name = model.find('a', class_='font-bold').string
        print(f'Scraping {model_name}')
        # Scrape the specs
        model_all_specs = model.find_all('span', class_='info-gray')
        # Categorize the specs
        for spec in model_all_specs:
            # print(spec)
            if "公里" in spec.get_text():
                endurance_str = re.findall(r'\d+', spec.string)
                if len(endurance_str) == 1:
                    endurance_list = [int(endurance_str[0]), int(endurance_str[0])]
                else:
                    endurance_list = [int(endurance_str[0]), int(endurance_str[1])]
            elif "马力" in spec.get_text():
                power_str = re.findall(r'\d+', spec.string)
                if len(power_str) == 1:
                    power_list = [int(power_str[0]), int(power_str[0])]
                else:
                    power_list = [int(power_str[0]), int(power_str[1])]
            elif "充" in spec.get_text():
                charging_time_str = re.findall(r'\d+\.\d+', spec.string)
                
                if charging_time_str == []:
                    charging_time_str = re.findall(r'\d+', spec.string)
                
                if "快充" in spec.get_text():
                    if len(charging_time_str) == 1:
                        charging_time_list = [float(charging_time_str[0]), 0.0]
                    else:
                        charging_time_list = [float(charging_time_str[0]), float(charging_time_str[1])]
                else:
                    charging_time_list = [0.0, float(charging_time_str[0])]
            elif spec.get_text()=='':
                pass
            else:
                model_type = spec.get_text()
                # print(model_type)
        # Scrape the scores. 0.0 is used for unknown scores
        model_score = model.find('span', class_='score-number')
        if model_score == None:
            model_score = 0.0
        else:
            model_score = float(model_score.string)
        # Scrape the price range of the model
        price_range_str = re.findall(r'\d+\.\d+',model.find('span', class_='font-arial').string)
        if len(price_range_str) == 1:
            price_range_list = [float(price_range_str[0]), float(price_range_str[0])]
        else:
            price_range_list = [float(price_range_str[0]), float(price_range_str[1])]
        model_object = Model(name=model_name, type=model_type, endurance=endurance_list,
                        power=power_list, charging_time=charging_time_list, score=model_score,
                        price_range=price_range_list,
                        version_tree=[])
        model_tree.append(model_object)

    model_idx = 0
    for model in all_model_verions:
        version_tree = []
        all_versions = model.find_all('ul', class_='interval01-list')
        for version in all_versions:
            version_all_info = version.find_all('div', class_='interval01-list-cars-infor')
            version_all_price = version.find_all('div', class_='interval01-list-guidance')
            for version_idx in range(0, len(version_all_info)):
                version_info = version_all_info[version_idx].find('a')
                # Scrape Version Name
                version_name = version_info.get_text()
                # Scrape Version URL
                version_url = version_info.get('href')
                # Scrape Version Price
                version_price = version_all_price[version_idx].find('div')
                version_price = re.findall(r'\d+\.\d+',version_price.get_text())
                version_price = float(version_price[0])
                # Generate Version Object
                version_object = Version(name=version_name, price=version_price, url=version_url)
                version_tree.append(version_object)
        # Assign to the Model
        model_tree[model_idx].version_tree = version_tree
        model_idx = model_idx + 1
        
    brand_object = Brand(name=brand, url=url, model_tree=model_tree)
    return brand_object
    
def save_brand_tree(brand_tree, cache_file):
    print('Saving brand tree to cache file')
    print('Tree Start', file=cache_file)
    for brand in brand_tree:
        print(f'Saving {brand.name}')
        print("Brand Node Start", file=cache_file)
        print(brand.name, file=cache_file)
        print(brand.url, file=cache_file)
        if len(brand.model_tree) != 0:
            for model in brand.model_tree:
                print("Model Node Start", file=cache_file)
                print(model.name, file=cache_file)
                print(model.type, file=cache_file)
                print(model.endurance[0], file=cache_file)
                print(model.endurance[1], file=cache_file)
                print(model.power[0], file=cache_file)
                print(model.power[1], file=cache_file)
                print(model.price_range[0], file=cache_file)
                print(model.price_range[1], file=cache_file)
                print(model.score, file=cache_file)
                print(model.charging_time[0], file=cache_file)
                print(model.charging_time[1], file=cache_file)
                if len(model.version_tree) != 0:
                    for version in model.version_tree:
                        print("Version Node Start", file=cache_file)
                        print(version.name, file=cache_file)
                        print(version.price, file=cache_file)
                        print(version.url, file=cache_file)
                        print("Version Node End", file=cache_file)
                print("Model Node End", file=cache_file)
        print("Brand Node End", file=cache_file)
    print('Tree End', file=cache_file)
    
def load_brand_tree(cache_file):
    brand_tree = []
    line = cache_file.readline().strip()
    if line == "Tree Start":
        while(1):
            brand_node = load_brand_nodes(cache_file)
            if brand_node == []:
                break
            brand_tree.append(brand_node)
        return brand_tree
    else:
        return []
    
                        
def load_brand_nodes(cache_file):
    model_tree = []
    line = cache_file.readline().strip()
    if line == 'Brand Node Start':
        brand_name = cache_file.readline().strip()
        brand_url = cache_file.readline().strip()
        while(1):
            model_node = load_model_nodes(cache_file)
            if model_node == []:
                break
            model_tree.append(model_node)
        brand_node = Brand(name=brand_name, url=brand_url, model_tree=model_tree)
        return brand_node
    else:
        return []
    
def load_model_nodes(cache_file):
    version_tree = []
    line = cache_file.readline().strip()
    if line == 'Model Node Start':
        model_name = cache_file.readline().strip()
        model_type = cache_file.readline().strip()
        model_endurance = [0, 0]
        model_endurance[0] = int(cache_file.readline().strip())
        model_endurance[1] = int(cache_file.readline().strip())
        model_power = [0, 0]
        model_power[0] = int(cache_file.readline().strip())
        model_power[1] = int(cache_file.readline().strip())
        model_price_range = [0, 0]
        model_price_range[0] = float(cache_file.readline().strip())
        model_price_range[1] = float(cache_file.readline().strip())
        model_score = float(cache_file.readline().strip())
        model_charging_time = [0.0, 0.0]
        model_charging_time[0] = float(cache_file.readline().strip())
        model_charging_time[1] = float(cache_file.readline().strip())
        while(1):
            version_node = load_version_nodes(cache_file=cache_file)
            if version_node == []:
                break
            version_tree.append(version_node)
        model_node = Model(name=model_name, type=model_type, endurance=model_endurance, power=model_power,
                           price_range=model_price_range, score=model_score, charging_time=model_charging_time,
                           version_tree=version_tree)
        return model_node
    else:
        return []
    
def load_version_nodes(cache_file):
    line = cache_file.readline().strip()
    if line == 'Version Node Start':
        version_name = cache_file.readline().strip()
        version_price = float(cache_file.readline().strip())
        version_url = cache_file.readline().strip()
        cache_file.readline().strip()
        version_node = Version(name=version_name, price=version_price, url=version_url)
        return version_node
    else:
        return []
    
def form_construct():
    os.system('cls')
    
    print("----------------------------------------------")
    print("Now let's talk about your dream car")
    print("----------------------------------------------")
    # Input User Name
    user_str = input("What's your name? ")
    # Input Type of Car
    while True:
        print('\n')
        print('Q1. What is the type of your dream car')
        print('0: Not Specified')
        print('1: SUV')
        print('2: Sedan')
        type_str = input('Your answer: ')
        try:
            type_int = int(type_str)
            if type_int > 2 or type_int < 0:
                print('Invalid input, please retry.')
            else:
                break
        except:
            print('Invalid input, please retry.')
    # Input Size of Car
    while True:
        print('\n')
        print('Q2. What is size of your dream car?')
        print('0: Not Specified')
        print('1: Subcompact')
        print('2: Compact')
        print('3: Mid-size')
        print('4: Large')
        size_str = input('Your answer: ')
        try:
            size_int = int(size_str)
            if size_int > 4 or size_int < 0:
                print('Invalid input, please retry.')
            else:
                break
        except:
            print('Invalid input, please retry.')
    # Input Endurance of Car
    while True:
        print('\n')
        min_endu_str = input('Q3.1. What is the minimal endurance (kilometer) of your dream car? ')
        try:
            min_endurance = float(min_endu_str)
            if min_endurance < 0:
                print('Invalid input, please retry.')
            else:
                break
        except:
            print('Invalid input, please retry.')
    while True:
        print('\n')
        max_endu_str = input('Q3.2. What is the maximal endurance (kilometer) of your dream car? ')
        try:
            max_endurance = float(max_endu_str)
            if max_endurance < min_endurance:
                print('Invalid input, please retry.')
            else:
                break
        except:
            print('Invalid input, please retry.')
    # Input Price Range of Car
    while True:
        print('\n')
        min_price_str = input('Q4.1. What is the minimal price (10000 RMB) of your dream car? ')
        try:
            min_price = float(min_price_str)
            if min_price < 0:
                print('Invalid input, please retry.')
            else:
                break
        except:
            print('Invalid input, please retry.')
    while True:
        print('\n')
        max_price_str = input('Q4.2. What is the maximal price (10000 RMB) of your dream car? ')
        try:
            max_price = float(max_price_str)
            if max_price < min_price:
                print('Invalid input, please retry.')
            else:
                break
        except:
            print('Invalid input, please retry.')
            
    input_form = Form(user=user_str, type=type_int, size=size_int, endurance=[min_endurance, max_endurance], 
                       price_range=[min_price, max_price])
    return input_form

def submit_form():
    while True:
        input_form = form_construct()
        os.system('cls')
        print('Your Dream Car:')
        print("----------------------------------------------")
        print(input_form)
        print("----------------------------------------------")
        print('\n')
        print('Do you confirm the information above?')
        print('0: Yes, I confirm')
        print('1: No, I want to cancel')
        print('\n')
        confirm_str = input('Your answer: ')
        try:
            confirm_int = int(confirm_str)
            if confirm_int > 1 or confirm_int < 0:
                print('Invalid input, please retry.')
            else:
                if confirm_int == 1:
                    exit_code = 1
                else:
                    exit_code = 0
                break
        except:
            print('Invalid input, please retry.')
    
    return input_form, exit_code

def handle_form(input_form, exit_code, brand_tree):
    if exit_code == 1:
        return [], exit_code
    else:
        matched_brand_tree = []
        for brand in brand_tree:
            matched_model_tree = []
            for model in brand.model_tree:
                # Compare type
                if (input_form.type == 1) and ("SUV" not in model.type):
                    continue
                elif (input_form.type == 2) and ("车" not in model.type):
                    continue
                
                if (input_form.size == 1) and ("小型" not in model.type):
                    continue
                elif (input_form.size == 2) and ("紧凑型" not in model.type):
                    continue
                elif (input_form.size == 3) and ("中型" not in model.type):
                    continue
                elif (input_form.size == 4) and ("中大型" not in model.type):
                    continue
                # Compare Endurance
                if (input_form.endurance[0] > model.endurance[1]):
                    continue
                elif (input_form.endurance[1] < model.endurance[0]):
                    continue
                # Compare Price
                if (input_form.price_range[0] > model.price_range[1]):
                    continue
                elif (input_form.price_range[1] < model.price_range[0]):
                    continue
                matched_model_tree.append(model)
            
            # Append the brand to matched_brand_tree 
            # if the matched_model_tree is not empty
            if len(matched_model_tree) > 0:
                temp_brand = copy.deepcopy(brand)
                temp_brand.model_tree = matched_model_tree
                matched_brand_tree.append(temp_brand)
        return matched_brand_tree, exit_code
        
def sort_result(matched_brand_tree):
    sorted_brand_tree = []
    for brand in matched_brand_tree:
        for model in brand.model_tree:
            if sorted_brand_tree == []:
                temp_brand = Brand()
                temp_brand = copy.deepcopy(brand)
                temp_brand.model_tree = [model]
                sorted_brand_tree.append(temp_brand)
            else:
                for index in range(0, len(sorted_brand_tree)):
                    if (sorted_brand_tree[index].model_tree[0].score < model.score) or (index == (len(sorted_brand_tree) - 1)):
                        temp_brand = Brand()
                        temp_brand = copy.deepcopy(brand)
                        temp_brand.model_tree = [model]
                        sorted_brand_tree.insert(index, temp_brand)
                        break
    return sorted_brand_tree

def display_result(sorted_brand_tree):
    index = 0
    while True:
        os.system('cls')
        print(f"----------------------------------------------")
        print(f"Candidates of you dream car")
        print(f"----------------------------------------------")
        print(sorted_brand_tree[index])
        print(f"Page {index+1} / {len(sorted_brand_tree)}")
        if index == 0:
            print("+: to the next page")
            print("0: to the home page")
        elif (index == len(sorted_brand_tree) - 1):
            print("-: to the previous page")
            print("0: to the home page")
        else:
            print("+: to the next page")
            print("-: to the previous page")
            print("0: to the home page")
        cmd_str = input("Input Command: ")
        
        if cmd_str == '+':
            if (index < len(sorted_brand_tree) - 1):
                index = index + 1
        elif cmd_str == '-':
            if (index > 0):
                index = index - 1
        elif cmd_str == '0':
            return 
        
def init():
    brand_tree = []
    if os.path.exists('cache.txt') is True:
        cache_file = open('cache.txt', 'r')
        brand_tree = load_brand_tree(cache_file=cache_file)
        cache_file.close()
    else:
        cache_file = open('cache.txt', 'w')
        for brand in autohome_brand_dict:
            print(f'Requesting {brand}')
            brand_object = request_brand(brand)
            brand_tree.append(brand_object)
        save_brand_tree(brand_tree=brand_tree, cache_file=cache_file)
        cache_file.close()
        cache_file = open('cache.txt', 'r')
        brand_tree = load_brand_tree(cache_file=cache_file)
        cache_file.close()
    return brand_tree

def home():
    while True:
        os.system('cls')
        print("----------------------------------------------")
        print("Welcome! Let's find out your dream electric cars")
        print("(that are available in China)")
        print("----------------------------------------------")
        print("0: Start")
        print("1: Exit")
        cmd_str = input("Input Command: ")
        if cmd_str == '0':
            return 0
        elif cmd_str == '1':
            return 1
    
    
def run(brand_tree):
    # Ask user for specific needs on their dream electric car
    user_form, exit_code = submit_form()
    # Find all the matched models
    matched_brand_tree, exit_code = handle_form(input_form=user_form, exit_code=exit_code, brand_tree=brand_tree)
    if exit_code == 1:
        return
    # Print the matched models to file
    print_file = open('matched.txt', 'w')
    print(len(matched_brand_tree))
    for brand in matched_brand_tree:
        print(brand, file=print_file)
    print_file.close()
    # Print the sorted matched module to file
    print_file = open('sorted.txt', 'w')
    sorted_brand_tree = sort_result(matched_brand_tree)
    for brand in sorted_brand_tree:
        print(brand, file=print_file)
    print_file.close()
    # Display result
    display_result(sorted_brand_tree)

if __name__ == '__main__':
    # Crawl and scrape data
    brand_tree = init()
    print_file = open('print.txt', 'w')
    for brand in brand_tree:
        print(brand, file=print_file)
        
    print_file.close()

    while True:
        home_cmd = home()
        if home_cmd == 0:
            run(brand_tree)
        elif home_cmd == 1:
            break