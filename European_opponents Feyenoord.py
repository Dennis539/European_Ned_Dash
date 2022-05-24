# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 09:39:22 2022

@author: denni
"""

import requests
import bs4
import pandas as pd
from googlesearch import search

import spacy
import re
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time


os.chdir('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\Functions')

import overall_formulas
from overall_formulas import get_coordinates

os.chdir('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\Netherlands')

#%%
"""
The following part is a piece of code which will extract all of the european 
opponents of Feyenoord. 
"""
wiki_url = 'https://nl.wikipedia.org/wiki/Lijst_van_Europese_wedstrijden_van_Feyenoord'
res = requests.get(wiki_url)

soup = bs4.BeautifulSoup(res.text, 'html.parser')

soup = soup.find(id='bodyContent')
soup = soup.find("div", {"class": "mw-parser-output"})
soup = soup.find("div", {"style": "overflow-x: auto; white-space: nowrap;"})
resultaten = soup.find('tbody')

# No unique elements in which the tables were separated. through some trial &
# error figured out what the right table was. 
#resultaten = soup.find('table',{'class':'wikitable mw-collapsible mw-made-collapsible'})

Country = ''

# Iterating throught the list. Within the actual table, two
# rows must be skipped as these do not contain any information
# It is one shorter because the footer is also unimportant. 
Club = []
Played = []
Country = []
Ref = []
Win_list = []
Draw_list = []
Loss_list = []
country = ''

for match in range(2, len(resultaten.find_all('tr')) -1):
    x = resultaten.find_all('tr')[match]

    # This line will check whether the row indicates a country. The original
    # table on Wikipedia contains rows which will only contain the name of the
    # country in which the club resides. 
    try:
        x_0 = x.select('td')[0]
        x_1 = x.select('td')[1]
        ref = x_0.find('a')
        if 'Bestand' in str(ref):
            ref = x_0.find_all('a')[1]
        Club.append(x_0.getText())
        Played.append(x_1.getText())
        Country.append(country)
        Ref.append(ref['href'])
        
        win = x.select('td')[3]
        if win.getText() == '' or win.getText() == '\n':
            Win_list.append('0')
        
        else:
            Win_list.append(win.getText())
            
        draw = x.select('td')[4]
        if draw.getText() == '' or draw.getText() == '\n':
            Draw_list.append('0')
        
        else:
            Draw_list.append(draw.getText())
            
        loss = x.select('td')[5]
        if loss.getText() == '' or loss.getText() == '\n':
            Loss_list.append('0')
            
        else:
            Loss_list.append(loss.getText())
        
        
    except:
        country = x.getText()


df_tegenstanders = pd.DataFrame({'Club': Club, 'Played': Played, 'Country': Country, 
                                 'Ref': Ref, 'Win': Win_list, 'Draw': Draw_list, 
                                 'Loss': Loss_list})

df_tegenstanders['Original_club'] = 'Feyenoord'
df_tegenstanders['Original_club_country'] = 'The Netherlands'


#%%
for i in ['Played', 'Win', 'Draw', 'Loss']:
    if df_tegenstanders[i].dtype == 'int32' or df_tegenstanders[i].dtype == 'int64':
        continue
    df_tegenstanders[i] = df_tegenstanders[i].str.replace('×', '')
    df_tegenstanders[i] = df_tegenstanders[i].str.replace('x', '')
    df_tegenstanders[i] = df_tegenstanders[i].str.replace('\n', '')
    df_tegenstanders[i] = df_tegenstanders[i].str.replace(' ', '')
    df_tegenstanders[i] = df_tegenstanders[i].astype(int)

df_tegenstanders['Country'] = df_tegenstanders['Country'].str.replace(' ', '')
df_tegenstanders['Country'] = df_tegenstanders['Country'].str.replace('\n', '')

for i in range(len(df_tegenstanders)):
    if df_tegenstanders['Club'].loc[i][0] == ' ':
        df_tegenstanders.at[i, 'Club'] = df_tegenstanders.loc[i]['Club'][1:]
                
        
for i in range(len(df_tegenstanders)):
    if df_tegenstanders['Country'].loc[i][0] == ' ' or df_tegenstanders['Country'].loc[i][0] == '\xa0':
        df_tegenstanders.at[i, 'Country'] = df_tegenstanders.loc[i]['Country'][1:]
        

df_tegenstanders['Club'] = df_tegenstanders['Club'].str.replace('\n', '')

#%%
df_tegenstanders.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Stats tegenstanders\\Stats_tegenstanders_Feyenoord.xlsx')

#%%
df_tegenstanders = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Stats tegenstanders\\Stats_tegenstanders_Feyenoord.xlsx')
df_countries = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\df_countries.xlsx')

#%%
df_countries['Country'] = df_countries['Country'].apply(lambda x: x.split(' -')[0])
df_countries['Country_english'] = df_countries['Country_english'].apply(lambda x: x.split(' -')[0])
df_tegenstanders = df_tegenstanders.merge(df_countries, how ='left', left_on = ['Country'], right_on = ['Country'])


#%%
overall_formulas.get_url_list(df_tegenstanders)
#overall_formulas.Country_translation(df_tegenstanders)
df_tegenstanders[['Stadium', 'Stadium_link']] = ''

os.chdir('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\Functions')
import overall_formulas

overall_formulas.Get_wiki_links(df_tegenstanders)

df_tegenstanders[['Latitude', 'Longitude']] = ''
overall_formulas.Getting_coordinates(df_tegenstanders)
#%%
df_tegenstanders[['Latitude', 'Longitude']] = df_tegenstanders[['Latitude', 'Longitude']].astype(float)


#%%
df_tegenstanders.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\df_Feyenoord_loc.xlsx')

