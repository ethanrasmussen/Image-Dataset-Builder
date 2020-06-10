# dependencies
import pathlib
import time
from typing import List
import requests
# Selenium:
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


# selenium infinite scroll
def inf_scroll(driver, pause_time:int):
    # get scroll height
    last_height = driver.execute_script('return document.body.scrollHeight')
    while True:
        # scroll to bottom
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        # wait to load page
        time.sleep(pause_time)
        # get new scroll height
        new_height = driver.execute_script('return document.body.scrollHeight')
        # if heights are same, stop scrolling
        if new_height == last_height:
            break
        # else, update last height
        last_height = new_height


# create images/ directory if it does not already exist
def create_img_dir():
    imgdir = pathlib.Path('images/')
    imgdir.mkdir(parents=True, exist_ok=True)


# create urls/ directory if it does not already exist
def create_urls_dir():
    urldir = pathlib.Path('urls/')
    urldir.mkdir(parents=True, exist_ok=True)


# get urls for a list of search terms
def get_urls(classname:str, searchterms:List[str]):
    # create sub-dir in urls/ for class
    subdir = pathlib.Path(f'urls/{classname}')
    subdir.mkdir(parents=True, exist_ok=True)
    # use webdriver options to specify proper download location
    dl_path = pathlib.Path(__file__).parent.parent
    dl_path = dl_path/subdir
    options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': str(dl_path)}
    options.add_experimental_option('prefs', prefs)
    # create a webdriver & implicitly wait
    driver = webdriver.Chrome(options=options, executable_path='functions/chromedriver.exe')
    driver.implicitly_wait(30)
    # create a urls.txt file for each search term
    index = 1
    for searchterm in searchterms:
        # get Google Images search results page
        driver.get(f"https://www.google.com/search?q={searchterm}&tbm=isch")
        # scroll to bottom of page
        inf_scroll(driver, 3)
        # once bottom is reached, execute JS command
        with open('functions/get_img_urls.js', 'r') as f:
            javascript = f.read()
            javascript = javascript.replace('urls.txt', f'urls{index}.txt')
            driver.execute_script(javascript)
            time.sleep(5)
        index +=1
    driver.close()


# get images from a urls TXT file
def get_images_from_urls(classname: str):
    # notify user of process beginning
    print(f'Beginning to grab images for {classname}...')
    # create sub-dir in images/ for class
    subdir = pathlib.Path(f'images/{classname}')
    subdir.mkdir(parents=True, exist_ok=True)
    # get files from the url sub-directory
    urldir = pathlib.Path(f'urls/{classname}')
    # get all url.txt files
    files = [x.name for x in urldir.rglob('*.txt')]
    total_pics = 1
    for url_txt in files:
        print(f'\nOpening URL list {files.index(url_txt)+1} of {len(files)}...')
        # get all URLs from txt
        urls = open(f'urls/{classname}/{url_txt}')
        # get images from all urls
        for pic in urls:
            try:
                # request img from URL
                pic_request = requests.get(pic)
                if pic_request.status_code == 200:
                    #TODO: fix filepath for downloads
                    print(f'test: images/{classname}/{total_pics}.jpg')
                    fpath = pathlib.Path(__file__).parent.parent
                    fpath = fpath/f'images/{classname}/{total_pics}.jpg'
                    print(fpath)
                    #
                    with open(fpath, 'wb') as f:
                        f.write(pic_request.content)
                    print(f'Saved picture {urls.index(pic)+1} of {len(urls)}.')
            except:
                print(f'Failed to download image. Skipping...')
            total_pics +=1
        print('\n')


# complete process
def create_dataset(data):
    # create list of all classes
    classes = [x for x in data]
    # create image directory
    create_img_dir()
    # create urls directory
    create_urls_dir()
    # get URL txt files for each class
    for class_ in classes:
        searchterms = [x for x in data.get(class_)]
        get_urls(str(class_), searchterms)
    # get image files for each class
    for class_ in classes:
        get_images_from_urls(class_)