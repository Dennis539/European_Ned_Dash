# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 20:14:10 2022

@author: denni
"""
import os
os.chdir('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\Voetbal_dashboard')

import pandas as pd
import requests
import bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from googlesearch import search
from haversine import haversine, Unit
import matplotlib.pyplot as plt


os.chdir('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\Functions')

import overall_formulas
from overall_formulas import get_coordinates

os.chdir('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\Netherlands')

df_totaal = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\Tegenstanders_totaal.xlsx')
df_totaal['Original_club_country'] = 'Netherlands'
#%%
"""
Creating a subset which contains all of the clubs of the given country. 
"""
df_clubs = df_totaal.drop_duplicates(
    subset = ['Original_club', 
              'Original_club_country'])[['Original_club', 
                                         'Original_club_country']].reset_index()
#df_clubs = pd.DataFrame(list(df_totaal['Original_club'].unique()), columns = ['Original_club'])
df_clubs[['Link', 'Stadium_link', 'Stadium', 'Longitude', 'Latitude']] = ''



#%%
chrome_path = 'C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Selenium\\chromedriver.exe'
chrome_options = Options()
#chrome_options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=chrome_path, options = chrome_options)

for i in range(len(df_clubs)):
    print(i)
    driver.get('http://duckduckgo.com')
    search_input = driver.find_element_by_id('search_form_input_homepage')
    query = f'{df_clubs.loc[i]["Original_club"]} wiki'
    search_input.send_keys(query)        
    search_input.send_keys(Keys.ENTER)

    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        if 'en.wikipedia.org' in elem.get_attribute('href'):
            url_club = elem.get_attribute('href')
            df_clubs.at[i, 'Link'] = url_club
            break


    try:
        res = requests.get(df_clubs.loc[i]['Link'])
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        soup_body_content = soup.find('div', {'id': 'bodyContent'})
        soup_parser = soup_body_content.find('div', {'id': 'mw-parser-output'})
        
        soup_infocard = soup_body_content.find('table', {'class': 'infobox vcard'})
        soup_infocard
        
        iterable = iter(range(1,10))
        for j in soup_infocard.find_all('th'):
            if j.getText() == 'Ground' or j.getText() == 'Stadium':
                num = next(iterable)
                break
            next(iterable)
            
        stadium_tag = soup_infocard.find_all('td')[num]
        
        link = stadium_tag.find('a')
        link = link.get_attribute_list('href')[0]
        stadium = stadium_tag.getText()
        
        df_clubs.at[i, 'Stadium_link'] = link
        df_clubs.at[i, 'Stadium'] = stadium

    except:
        print(df_clubs.loc[i]['Link'])
        
        
    if str(df_clubs.loc[i]['Latitude']) != '' and str(df_clubs.loc[i]['Latitude']) != 'nan':
        continue
        
        
    if str(df_clubs.loc[i]['Stadium_link']) == '' or str(df_clubs.loc[i]['Stadium_link']) == 'nan':
        for query in search(df_clubs.loc[i]['Club'] + ' ' +
                            df_clubs.loc[i]['Country_english'] + ' coordinates latitude.to', 
                            tld = 'co.in', num = 5, stop = 5, pause = 2):
            url = query
            overall_formulas.get_coordinates(url, df_clubs, i)
    
    else:
        try:
            
            url = f'http://en.wikipedia.org/{df_clubs.loc[i]["Stadium_link"]}'
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
            df_clubs.at[i, 'Latitude'] = lat
            df_clubs.at[i, 'Longitude'] = lon
            
        except:
            for query in search(df_clubs.loc[i]['Stadium'] + ' ' +
                                df_clubs.loc[i]['Club'] + ' coordinates latitude.to', 
                                tld = 'co.in', num = 5, stop = 5, pause = 2):
                print(i)
                url = query
                overall_formulas.get_coordinates(url, df_clubs, i)

driver.close()


#%%
df_clubs[['Latitude', 'Longitude']] = df_clubs[['Latitude', 'Longitude']].astype(float)

df_clubs.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\df_clubs.xlsx')

df_totaal_merge = df_totaal[
    ['Club', 'Played', 'Country', 'Latitude', 'Longitude','Original_club', 
     'Original_club_country']].merge(df_clubs, how = 'left', on = 'Original_club')
        


df_totaal_merge['Distance'] = ''
#%%
for i in range(len(df_totaal_merge)):
    coord_home = (df_totaal_merge.loc[i]['Latitude_y'], df_totaal_merge.loc[i]['Longitude_y'])
    coord_away = (df_totaal_merge.loc[i]['Latitude_x'], df_totaal_merge.loc[i]['Longitude_x'])
    df_totaal_merge.at[i, 'Distance'] = haversine(coord_home, coord_away)

df_totaal_merge['Distance'] = df_totaal_merge['Distance'].astype(float)
df_totaal_merge['Distance'] = round(df_totaal_merge['Distance'], 2)

df_totaal_merge.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\df_totaal_distances.xlsx')



#%%
club_dict = {}
for i in df_totaal_merge['Original_club'].unique():
    df_top = df_totaal_merge[
        df_totaal_merge['Original_club'] == i][
            ['Club', 'Original_club', 'Distance']].sort_values(
                'Distance', ascending = False).head()
                
    club_dict[i] = df_top[['Club', 'Original_club', 'Distance']]
    
    

    






