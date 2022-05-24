# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 09:40:57 2022

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
wiki_url = 'https://nl.wikipedia.org/wiki/Lijst_van_Europese_wedstrijden_van_PSV'
res = requests.get(wiki_url)
soup = bs4.BeautifulSoup(res.text, 'html.parser')

soup = soup.find(id='bodyContent')
soup = soup.find("div", {"class": "mw-parser-output"})
# No unique elements in which the tables were separated. through some trial &
# error figured out what the right table was. 
resultaten = soup.find_all('table',{'class':'wikitable'})[2]

total = []
Country = ''

# Iterating throught the list. Within the actual table, the first row has the
# columnnames hence the loop starts at 1. It is one shorter because the footer 
# is also unimportant. 
for match in range(1, len(resultaten.find_all('tr')) -1):
    x = resultaten.find_all('tr')[match]
    x_0 = x.select('td')[0]
    x_1 = x.select('td')[1]

    
    # This line will check whether the row indicates a country. The original
    # table on Wikipedia contains a column called 'land' which will only contain
    # text if the row contains information on a country.
    if x_1.find('a'):
        Country = x_0.getText()
    
    else:
        clubs = []
        x_2 = x.select('td')[2]
        clubs.append(x_0.getText())
        clubs.append(x_2.getText())
        clubs.append(Country)
        ref = x_0.find('a')
        ref = ref['href']
        clubs.append(ref)
        win = x.select('td')[4]
        if win.getText() == '' or win.getText() == '\n':
            clubs.append('0')
        
        else:
            clubs.append(win.getText())
            
        draw = x.select('td')[5]
        if draw.getText() == '' or draw.getText() == '\n':
            clubs.append('0')
        
        else:
            clubs.append(draw.getText())
            
        loss = x.select('td')[6]
        if loss.getText() == '' or loss.getText() == '\n':
            clubs.append('0')
            
        else:
            clubs.append(loss.getText())
        
        total.append(clubs)
        
        
df_tegenstanders = pd.DataFrame(total, columns = ['Club', 'Played', 'Country', 
                                                  'Ref', 'Win', 'Draw', 'Loss'])
df_tegenstanders['Original_club'] = 'PSV'
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
df_tegenstanders.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Stats tegenstanders\\Stats_tegenstanders_PSV.xlsx')

df_tegenstanders = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Stats tegenstanders\\Stats_tegenstanders_PSV.xlsx')

#%%
df_countries = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\df_countries.xlsx')
df_countries['Country'] = df_countries['Country'].apply(lambda x: x.split(' -')[0])
df_countries['Country_english'] = df_countries['Country_english'].apply(lambda x: x.split(' -')[0])

df_tegenstanders = df_tegenstanders.merge(df_countries, how ='left', left_on = ['Country'], right_on = ['Country'])


#%%
df_feyenoord = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\df_Feyenoord_loc.xlsx')


#%%
df_tegenstanders = df_tegenstanders.merge(
    df_feyenoord[['Club', 'Stadium', 'Stadium_link', 'Latitude', 'Longitude']],
    how = 'left')


#%%
overall_formulas.get_url_list(df_tegenstanders)
#overall_formulas.Country_translation(df_tegenstanders)
overall_formulas.Get_wiki_links(df_tegenstanders)
overall_formulas.Getting_coordinates(df_tegenstanders)

df_tegenstanders[['Latitude', 'Longitude']] = df_tegenstanders[['Latitude', 'Longitude']].astype(float)


#%%
df_tegenstanders.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\df_PSV_loc.xlsx')

#%%
df_PSV = df_tegenstanders[['Club', 'Played', 'Country', 'Ref', 'Stadium', 'Stadium_link',
       'Latitude', 'Longitude', 'Link', 'Country_english']]

df_PSV['Original_club'] = 'PSV'

df_feyenoord = df_feyenoord[['Club', 'Played', 'Country', 'Ref', 'Stadium', 'Stadium_link',
       'Latitude', 'Longitude', 'Link', 'Country_english', 'Original_club']]



#%%
df_totaal = pd.concat([df_feyenoord, df_PSV])
df_totaal.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\Tegenstanders_totaal.xlsx')

# Kind of running into the problem of duplicate values. Therefore, also 
# creating a dataframe with unique club names. 
df_totaal_unique = df_totaal.drop_duplicates(subset = 'Club')
df_totaal_unique.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\Tegenstanders_totaal_unique.xlsx')















