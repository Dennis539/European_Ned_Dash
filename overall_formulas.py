# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 19:00:40 2022

@author: denni
"""
import pandas as pd
import requests
import bs4
import re
from googlesearch import search

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

def get_coordinates(url, df_tegenstanders, i):
    if 'latitude.to' in url:
        try:
            res = requests.get(url)
            soup =  bs4.BeautifulSoup(res.text, 'html.parser')
            soup_2 = soup.find('p', {'class': 'desc'})
            for j in soup_2.find_all('meta'):
                var = j.get_attribute_list('itemprop')[0].capitalize()
                value = j.get_attribute_list('content')[0]
                df_tegenstanders.at[i, var] = value
            return 'Next'
                
        except:
            pass
        
    elif 'latlong.net' in url:
        try:
            res = requests.get(url)
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            soup_2 = soup.find('div', {'class': 'rightcol shadow rounded'})  
            iterable = iter([0,1,2,3])
            num = 0
            for j in soup_2.find_all('tr'):
                num = next(iterable)
    
                if num == 1:
                    text = j.getText()
                    text = text.replace('Latitude', '')
                    df_tegenstanders.at[i, 'Latitude'] = text
                elif num == 2:
                    text = j.getText()
                    text = text.replace('Longitude', '')
                    df_tegenstanders.at[i, 'Longitude'] = text
                    break
            return 'Next'
        
        except:
            pass

    elif 'findlatitudeandlongitude' in url:
        try:
            res_met = requests.get(url)
            soup_met = bs4.BeautifulSoup(res_met.text, 'html.parser')
            soup_met_lat = soup_met.find('span', {'id': 'lat_dec'})
            latitude = soup_met_lat.find('span', {'class': 'value'}).getText()        
            soup_met_lon = soup_met.find('span', {'id': 'lon_dec'})
            longitude = soup_met_lon.find('span', {'class': 'value'}).getText() 
            df_tegenstanders.at[i, 'Latitude'] = latitude
            df_tegenstanders.at[i, 'Longitude'] = longitude
            return 'Next'
        
        except:
            pass

    else:
        return 'Not_next'
    
def get_url_list(df_tegenstanders):
    url_list = []
    for i in range(len(df_tegenstanders)):
        try:
            url = 'http://nl.wikipedia.org' + df_tegenstanders.loc[i]['Ref']
            res = requests.get(url)
            soup =  bs4.BeautifulSoup(res.text, 'html.parser')
            panel = soup.find('div', {'id', 'mw-panel'})
            nav_bar = soup.find('nav', {'id': 'p-lang'})
            box = nav_bar.find('div', {'class': 'vector-menu-content'})
            link = box.find('li', {'class', re.compile('interlanguage-link interwiki-en')})
            link = link.find('a')
        
            link = link.get_attribute_list('href')[0]
            url_list.append(link)
            
        except:
            url_list.append(url)
    
    df_tegenstanders['Link'] = url_list
    
    
def Country_translation(df_tegenstanders):
    """
    Used to translate the Dutch countries in the list to English countries. 
    """
    chrome_path = 'C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Selenium\\chromedriver.exe'
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=chrome_path, options = chrome_options)

    current_country = ''
    translation = ''
    for i in range(len(df_tegenstanders)):
        country = df_tegenstanders.loc[i]['Country']
        if current_country == country:
            df_tegenstanders.at[i, 'Country_english'] = translation        
            continue
        
        else:
            try:
                driver.get('http://duckduckgo.com')
                search_input = driver.find_element_by_id('search_form_input_homepage')
                query = f'{country} naar engels'
                
                search_input.send_keys(query)        
                search_input.send_keys(Keys.ENTER)
                
                translation = driver.find_element_by_xpath(
                    "//div[@class='module--translations-translatedtext js-module--translations-translatedtext']").text
        
                df_tegenstanders.at[i, 'Country_english'] = translation
                
            except:
                print('Nothing found')
                print(country)
                translation = df_tegenstanders.loc[i]['Country']
                df_tegenstanders.at[i, 'Country_english'] = translation

                
            current_country = country

    driver.close()
    
    
    
def Get_wiki_links(df_tegenstanders):
    """
    A lot of wikipedia pages from football clubs also contain information about
    the stadium in which they play. The script below will assess whether there is
    a page of the club their stadium exists. If no stadium is found the column 
    will remain empty. 
    """
    for url in range(len(df_tegenstanders)):
        if str(df_tegenstanders.loc[url]['Stadium']) != 'nan' and str(df_tegenstanders.loc[url]['Stadium']) != '':
            continue
        
        try:
            res = requests.get(df_tegenstanders.loc[url]['Link'])
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            
            # A lot of Wikipedia pages have a information box on the right side of
            # the page. In this case, information about the clubs, including their
            # stadium, can be found over here. The main goal here is to obtain this. 
            soup_body_content = soup.find('div', {'id': 'bodyContent'})
            soup_parser = soup_body_content.find('div', {'id': 'mw-parser-output'})
            
            soup_infocard = soup_body_content.find('table', {'class': 'infobox vcard'})
            soup_infocard
            
            # After the information on this card has been selected, the script will
            # iterate through the page. If it finds the word Ground of Stadium,
            # you will know that the stadium name will be behind that. 

            check_image = soup_infocard.find('td', {'class': 'infobox-image'})
            try:
                check_image.getText()
                Image = 'Yes'
                
            except:
                Image = 'No'
            
            iterable = iter(range(1,10))
            for i in soup_infocard.find_all('th'):
                if i.getText() == 'Ground' or i.getText() == 'Stadium':
                    if Image == 'Yes':
                        num = next(iterable)
                        break
                    
                    if Image == 'No':
                        break
                    
                num = next(iterable)
                
            stadium_tag = soup_infocard.find_all('td')[num]
            stadium = stadium_tag.getText()
            df_tegenstanders.at[url, 'Stadium'] = stadium
            
            
            link = stadium_tag.find('a')
            link = link.get_attribute_list('href')[0]
            
            if '/wiki/' not in link:
                print('ruig')
                1/0
                
            df_tegenstanders.at[url, 'Stadium_link'] = link
        
        except:
            print(df_tegenstanders.loc[url]['Link'])
        
        time.sleep(0.1)

def Getting_coordinates(df_tegenstanders):
    """
    The moment of truth. The information previously gathered will be combined to
    find the Longitude and Latitude of the clubs. First, the script will assess
    whether a Stadium has actually been found. If not, a Google search for the 
    coordinates of the club will be performed. 
    Else, the Wikipedia page of the stadium will be opened. If it does and it is
    possible to see the coordinates over there, the coordinates will be saved. 
    If not, a Google search with the stadium name will be performed. 
    """
    
    for i in range(len(df_tegenstanders)):
        if str(df_tegenstanders.loc[i]['Latitude']) != '' and str(df_tegenstanders.loc[i]['Latitude']) != 'nan':
            continue
        
        
        if str(df_tegenstanders.loc[i]['Stadium_link']) == '' or str(df_tegenstanders.loc[i]['Stadium_link']) == 'nan':
            for query in search(df_tegenstanders.loc[i]['Club'] + ' ' +
                                df_tegenstanders.loc[i]['Country_english'] + ' coordinates latitude.to', 
                                tld = 'co.in', num = 5, stop = 5, pause = 2):
                url = query
                get_coordinates(url, df_tegenstanders, i)
        
        else:
            try:
                
                url = f'http://en.wikipedia.org/{df_tegenstanders.loc[i]["Stadium_link"]}'
                res = requests.get(url)
                soup = bs4.BeautifulSoup(res.text, 'html.parser')
                
                coord = soup.find('span', {'id': 'coordinates'})
                coord_link_class = coord.find('a', {'class': 'external text'})
                coord_link = coord_link_class['href']
                
                res = requests.get('http:' + coord_link)
                soup = bs4.BeautifulSoup(res.text, 'html.parser')
                soup2 = soup.find('span', {'class': 'geo h-geo'})
                
                lat = soup2.find('span', {'class': "latitude p-latitude"}).getText()
                lon = soup2.find('span', {'class': "longitude p-longitude"}).getText()
                df_tegenstanders.at[i, 'Latitude'] = lat
                df_tegenstanders.at[i, 'Longitude'] = lon
                
            except:
                try:
                    url = f'http://en.wikipedia.org/{df_tegenstanders.loc[i]["Stadium_link"]}'
                    res = requests.get(url)
                    
                    soup = bs4.BeautifulSoup(res.text, 'html.parser')
                    coord = soup.find('span', {'class': 'plainlinks nourlexpansion'})
                    coord_link_class = coord.find('a', {'class': 'external text'})
                    coord_link = coord_link_class['href']
                    
                    res = requests.get('http:' + coord_link)
                    soup = bs4.BeautifulSoup(res.text, 'html.parser')
                    soup2 = soup.find('span', {'class': 'geo h-geo'})
                    
                    lat = soup2.find('span', {'class': "latitude p-latitude"}).getText()
                    lon = soup2.find('span', {'class': "longitude p-longitude"}).getText()
                    df_tegenstanders.at[i, 'Latitude'] = lat
                    df_tegenstanders.at[i, 'Longitude'] = lon
                
                except:
                    for query in search(df_tegenstanders.loc[i]['Stadium'] + ' ' +
                                        df_tegenstanders.loc[i]['Club'] + ' coordinates latitude.to', 
                                        tld = 'co.in', num = 5, stop = 5, pause = 2):
                        print(i)
                        url = query
                        get_coordinates(url, df_tegenstanders, i)
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    