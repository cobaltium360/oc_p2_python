import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


category_url = []

product_url = []

data = []

columns = [
    "product_page_url",
    "universal_product_code (upc)",
    "title",
    "price_including_tax",
    "price_excluding_tax",
    "number_available",
    "product_description",
    "category",
    "review_rating",
    "image_url"
]

def red(text):
    print(f"\033[31m{text}\033[0m")

def green(text):
    print(f"\033[32m{text}\033[0m")

def get_element_page(url):
    try :

        #valeur par défault pour éviter les erreurs comme sur le livre http://books.toscrape.com/catalogue/alice-in-wonderland-alices-adventures-in-wonderland-1_5/index.html sans descriptions
        page_url = ""
        upc_value = ""
        h1_value = ""
        price_include_value = ""
        price_exclude_value = ""
        remainning_value = ""
        description = ""
        category = ""
        rating = ""
        img_src = ""


        page_url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        upc_element = soup.find('th', text='UPC')
        if upc_element:
            upc_value = upc_element.find_next_sibling('td').text
        h1_element = soup.find('h1')
        if h1_element:
            h1_value = h1_element.text
        price_include_element = soup.find('th', text='Price (incl. tax)')
        if price_include_element:
            price_include_value = price_include_element.find_next_sibling('td').text
        price_exclude_element = soup.find('th', text='Price (excl. tax)')
        if price_exclude_element:
            price_exclude_value = price_exclude_element.find_next_sibling('td').text
        remainning_element = soup.find('th', text='Availability')
        if remainning_element:
            remainning_value = remainning_element.find_next_sibling('td').text
        product_description_div = soup.find('div', id='product_description')
        if product_description_div:
            description = product_description_div.find_next_sibling('p').text
        ul_breadcrumb = soup.find('ul', class_='breadcrumb')
        if ul_breadcrumb:
            a_tags = ul_breadcrumb.find_all('a')
            if len(a_tags) >= 3:
                category = a_tags[2].text
        p_star_rating = soup.find('p', class_='star-rating')
        if p_star_rating:
            class_value = p_star_rating.get('class')
            if class_value[1] == "Five":
                rating = 5
            if class_value[1] == "Four":
                rating = 4
            if class_value[1] == "Three":
                rating = 3
            if class_value[1] == "Two":
                rating = 2
            if class_value[1] == "One":
                rating = 1
        div_item_active = soup.find('div', class_='item active')
        if div_item_active:
            img_tag = div_item_active.find('img')
            if img_tag:
                img_src = img_tag.get('src')
                img_src = img_src.replace("../../", "http://books.toscrape.com/")
        new_value = [page_url,upc_value,h1_value,price_include_value,price_exclude_value,remainning_value,description,category,rating,img_src]
        data.append(new_value)
    except ValueError:
        red("Une érreur est survenue, merci de réessayer.")
        
def get_links_product(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        div_container = soup.find_all('div', class_='image_container')
        for div in div_container:
            first_a_tag = div.find('a')
            if first_a_tag:
                href_value = first_a_tag.get('href')
                href_value = href_value.replace("../../../" , "http://books.toscrape.com/catalogue/")
                product_url.append(href_value)
        next_element = soup.find('li', class_="next")
        if next_element:
            next_href = next_element.find('a')['href']
            last_slash_index = url.rfind('/')
            new_url = url[:last_slash_index+1] +next_href
            get_links_product(new_url)
    except ValueError:
        red("Une érreur est survenue, merci de réessayer.")
        
def get_link_category():
    response = requests.get("http://books.toscrape.com/index.html")
    soup = BeautifulSoup(response.content, 'html.parser')
    ul_element = soup.find('ul', class_='nav-list')
    if ul_element:
        a_tags = ul_element.find_all('a')
        skip_first = True
        for tag in a_tags:
            if skip_first:
                skip_first = False
                continue
            href_value = tag['href']
            href_value = "http://books.toscrape.com/" + href_value
            category_url.append(href_value)
            
def dowload_images():
    for value in data:
        image_url = value[9]
        last_slash_index = image_url.rfind('/')
        name_image = image_url[last_slash_index+1:]
        response = requests.get(image_url)
        with open(f"images/{name_image}", 'wb') as file:
            file.write(response.content)

def remove_jpg():
    path = './images/'
    files = os.listdir(path)
    jpg_files = []
    for file in files:
        if file.lower().endswith(".jpg"):
            jpg_files.append(file)
    for jpg in jpg_files:
        file_path = os.path.join(path, jpg)
        os.remove(file_path)

def remove_csv():
    path = './data/'
    files = os.listdir(path)
    csv_files = []
    for file in files:
        if file.lower().endswith(".csv"):
            csv_files.append(file)
    for csv in csv_files:
        file_path = os.path.join(path, csv)
        os.remove(file_path)

def create_folder():
    if not os.path.exists("./images/"):
        os.makedirs("./images/")
        green("Folder images created !")
    if not os.path.exists("./data/"):
        os.makedirs("./data/")
        green("Folder data created !")

def download_category():
    category_array = []
    for category in data:
        name_category = category[7].replace(" ", "_")
        if name_category not in category_array:
            category_array.append(name_category)
    for category in category_array:
        data_save = []
        for info in data:
            name_category = info[7].replace(" ", "_")
            if category == name_category:
                data_save.append(info)
        df = pd.DataFrame(data_save, columns=columns)
        df.to_csv(f"./data/{category}.csv", index=False)

def main():
    
    print("""
  _                    _                                                  _                
 | |                  | |                                                (_)               
 | |__    ___    ___  | | __ ___     ___   ___  _ __  __ _  _ __   _ __   _  _ __    __ _  
 | '_ \  / _ \  / _ \ | |/ // __|   / __| / __|| '__|/ _` || '_ \ | '_ \ | || '_ \  / _` | 
 | |_) || (_) || (_) ||   < \__ \   \__ \| (__ | |  | (_| || |_) || |_) || || | | || (_| | 
 |_.__/  \___/  \___/ |_|\_\|___/   |___/ \___||_|   \__,_|| .__/ | .__/ |_||_| |_| \__, | 
                                                           | |    | |                __/ | 
                                                           |_|    |_|               |___/ 
                                                                                
                                                                                  \033[34mby théo.\033[0m    
    """)
    create_folder()
    img = input("Remove old images? (y or n) : ")
    if img == "y":
        remove_jpg()
    old_data = input("Remove old data ? (y or n) : ")
    if old_data == "y":
        remove_csv()
    green("\n1 - Scrap a book\n2 - Scrap books from category\n3 - Scrap all website\n4 - Exit\n")
    choose = input("Choose options : ")
    
    if choose == "1":
        url = input("Enter url of the book : ")
        get_element_page(url)
        download_category()
        dowload_images()
        green("Done !")
    
    elif choose == "2":
        url = input("Enter url of category : ")
        green("Fetching data...")
        get_links_product(url)
        for link in product_url:
            get_element_page(link)
        download_category()
        dowload_images()
        number = len(product_url)
        green(f"{number} books found !")
    
    elif choose == "3":
        green("Fetching data...")
        get_link_category()
        for url in category_url:
            get_links_product(url)
        for link in product_url:
            get_element_page(link)
        green("downloading data...")
        download_category()
        dowload_images()
        number = len(product_url)
        green(f"{number} books found !")

    elif choose == "4":
        green("See you later :) !")
        exit()
    
    else:
        red("Invalid choice. Please choose a valid option.")
if __name__ == '__main__':
    main()