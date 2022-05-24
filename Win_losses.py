# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 18:26:53 2022

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
# Az Alkmaar
wiki_url = 'https://nl.wikipedia.org/wiki/AZ_in_Europa'
res = requests.get(wiki_url)
soup = bs4.BeautifulSoup(res.text, 'html.parser')

soup = soup.find(id='bodyContent')
soup = soup.find("div", {"class": "mw-parser-output"})
# No unique elements in which the tables were separated. through some trial &
# error figured out what the right table was. 
resultaten = soup.find_all('table',{'class':'wikitable'})[3]


df_game_stats = {'Competition': [],
                 'Opponent': [],
                 'Goals_scored': [],
                 'Goals_conceded': []}

for i in range(1, len(resultaten.find_all('tr'))):
    row = resultaten.find_all('tr')[i]

    
    for j in range(len(row.find_all('td'))):
        cell = row.find_all('td')[j]
        
        if len(row.find_all('a')) == 3:
            competition = row.find_all('a')[0].getText()
            competition = competition.replace('\n', '')
        
        try:
            cell.find('a').attrs['class'][0] == 'image'
            opponent_index = j + 1
            match_index = j + 5
            match_played = row.find_all('td')[match_index].getText()
            opponent_played = row.find_all('td')[opponent_index].getText()
            break
        
        except:
            continue
    
    home_score = match_played.split('-')[0]
    home_score = home_score.split(' ')[-1]


    #There has been a game which has not been played by Feyenoord due to a 
    # punishment from the UEFA. 
    if len(match_played.split('-')) < 2:
        continue
    
    away_score = match_played.split('-')[1]
    away_score = away_score.split(' ')[0]
    away_score = away_score.replace('\n', '')
    df_game_stats['Competition'].append(competition)
    df_game_stats['Goals_scored'].append(home_score)
    df_game_stats['Goals_conceded'].append(away_score)
    df_game_stats['Opponent'].append(opponent_played)
    
df_game_stats_az = pd.DataFrame(df_game_stats)

#%%
# Feyenoord
wiki_url = 'https://nl.wikipedia.org/wiki/Lijst_van_Europese_wedstrijden_van_Feyenoord'
res = requests.get(wiki_url)
soup = bs4.BeautifulSoup(res.text, 'html.parser')

soup = soup.find(id='bodyContent')
soup = soup.find("div", {"class": "mw-parser-output"})
# No unique elements in which the tables were separated. through some trial &
# error figured out what the right table was. 
resultaten = soup.find_all('table',{'class':'wikitable'})[0]

df_game_stats = {'Competition': [],
                 'Goals_scored': [],
                 'Goals_conceded': [],
                 'Clubs': []}

unique_comp = []

for i in range(1, len(resultaten.find_all('tr'))):
    row = resultaten.find_all('tr')[i]
    
    
    if len(row.find_all('a')) == 4 or len(row.find_all('a')) == 5:
        competition = row.find_all('td')[1].getText()
        competition = competition.replace('\n', '')
        unique_comp.append(competition)
    
    for j in range(len(row.find_all('td'))):
        comp_search = row.find_all('td')[j].getText()
        comp_search = comp_search.replace('\n', '')
        if comp_search in unique_comp:
            print('kees')
            competition = row.find_all('td')[j].getText()
    
    for j in range(len(row.find_all('td'))):
        cell = row.find_all('td')[j]
        try:
            cell.find('a').attrs['class'][0] == 'image'
            club_index = j + 1
            match_index = j + 2
            match_played = row.find_all('td')[match_index].getText()
            opponent = row.find_all('td')[club_index].getText()
            break
        
        except:
            continue
    
    home_score = match_played.split('-')[0]
    home_score = home_score.split(' ')[-1]


    #There has been a game which has not been played by Feyenoord due to a 
    # punishment from the UEFA. 
    if len(match_played.split('-')) < 2:
        continue
    
    away_score = match_played.split('-')[1]
    away_score = away_score.split(' ')[0]
    away_score = away_score.replace('\n', '')
    df_game_stats['Competition'].append(competition)
    df_game_stats['Goals_scored'].append(home_score)
    df_game_stats['Goals_conceded'].append(away_score)
    df_game_stats['Clubs'].append(opponent)

df_game_stats_feyenoord = pd.DataFrame(df_game_stats)
df_game_stats_feyenoord = df_game_stats_feyenoord[df_game_stats_feyenoord['Goals_scored'] != '']


#%%
# fc Twente
wiki_url = 'https://nl.wikipedia.org/wiki/Lijst_van_Europese_wedstrijden_van_FC_Twente'
res = requests.get(wiki_url)
soup = bs4.BeautifulSoup(res.text, 'html.parser')

soup = soup.find(id='bodyContent')
soup = soup.find("div", {"class": "mw-parser-output"})
# No unique elements in which the tables were separated. through some trial &
# error figured out what the right table was. 
df_game_stats = {'Competition': [],
                 'Goals_scored': [],
                 'Goals_conceded': [],
                 'Opponent': []}
for num in range(len(soup.find_all('table',{'class':'wikitable', 'style': 'font-size:95%; text-align: center;'}))):
    
    resultaten = soup.find_all('table',{'class':'wikitable', 'style': 'font-size:95%; text-align: center;'})[num]
    
    for i in range(1, len(resultaten.find_all('tr'))):
        row = resultaten.find_all('tr')[i]
        row_length = len(row.find_all('td'))
        end_of_row = row.find_all('td')[row_length -1].getText()
        if len(end_of_row.split('.')) == 2:
            index = len(row.find_all('td')) - 2
            opponent_index = len(row.find_all('td')) - 5
            
        else:
            index = len(row.find_all('td')) -1
            opponent_index = len(row.find_all('td')) - 4

        if len(row.find_all('a')) == 3:
            if row.find_all('a')[0].getText() != '':
                competition = row.find_all('a')[0].getText()
                competition = competition.replace('\n', '')

        match_played = row.find_all('td')[index].getText()
        opponent = row.find_all('td')[opponent_index].getText()
        
        try:
            home_score = match_played.split('–')[0]
            away_score = match_played.split('–')[1]
            
        except:
            home_score = match_played.split('-')[0]
            away_score = match_played.split('-')[1]
        
        print(match_played)
        away_score = away_score.split(' ')[0]
        away_score = away_score.replace('\n', '')
        df_game_stats['Competition'].append(competition)
        df_game_stats['Goals_scored'].append(home_score)
        df_game_stats['Goals_conceded'].append(away_score)
        df_game_stats['Opponent'].append(opponent)

df_game_stats_twente = pd.DataFrame(df_game_stats)

#%%
# Ajax
wiki_url = 'https://nl.wikipedia.org/wiki/Lijst_van_Europese_wedstrijden_van_Ajax'
res = requests.get(wiki_url)
soup = bs4.BeautifulSoup(res.text, 'html.parser')

soup = soup.find(id='bodyContent')
soup = soup.find("div", {"class": "mw-parser-output"})
# No unique elements in which the tables were separated. through some trial &
# error figured out what the right table was. 
resultaten = soup.find_all('table',{'class':'wikitable'})[0]

df_game_stats = {'Competition': [],
                 'Goals_scored': [],
                 'Goals_conceded': []}

for i in range(1, len(resultaten.find_all('tr'))):
    row = resultaten.find_all('tr')[i]
    if row.find_all('td')[1].getText() != '' and row.find_all('td')[1].getText() != '\n':
        competition = row.find_all('td')[1].getText()
        competition = competition.replace('\n', '')
        match_played = row.find_all('td')[5].getText()
     

    else:
        match_played = row.find_all('td')[5].getText()

    
    home_score = match_played.split('-')[0]
    away_score = match_played.split('-')[1]
    away_score = away_score.split(' ')[0]
    away_score = away_score.replace('\n', '')
    df_game_stats['Competition'].append(competition)
    df_game_stats['Goals_scored'].append(home_score)
    df_game_stats['Goals_conceded'].append(away_score)

df_game_stats_ajax = pd.DataFrame(df_game_stats)

#%%
# PSV
wiki_url = 'https://nl.wikipedia.org/wiki/Lijst_van_Europese_wedstrijden_van_PSV'
res = requests.get(wiki_url)
soup = bs4.BeautifulSoup(res.text, 'html.parser')

soup = soup.find(id='bodyContent')
soup = soup.find("div", {"class": "mw-parser-output"})
# No unique elements in which the tables were separated. through some trial &
# error figured out what the right table was. 
resultaten = soup.find_all('table',{'class':'wikitable'})[1]

df_game_stats = {'Competition': [],
                 'Opponent': [],
                 'Goals_scored_home': [],
                 'Goals_conceded_home': [],
                 'Goals_scored_away': [],
                 'Goals_conceded_away': []}

unique_comp = []

for i in range(1, len(resultaten.find_all('tr'))):
    row = resultaten.find_all('tr')[i]
    
    if len(row.find_all('a')) == 4 or len(row.find_all('a')) == 5:
        competition = row.find_all('td')[1].getText()
        competition = competition.replace('\n', '')
        unique_comp.append(competition)
    
    for j in range(len(row.find_all('td'))):
        comp_search = row.find_all('td')[j].getText()
        comp_search = comp_search.replace('\n', '')
        if comp_search in unique_comp:
            print('kees')
            competition = row.find_all('td')[j].getText()
    
    
    match_played_home = row.find_all('td')[5].getText()
    match_played_away = row.find_all('td')[6].getText()
    opponent = row.find_all('td')[4].getText()

    try: 
        home_goals_scored = match_played_home.split('-')[0]
        home_goals_conceded = match_played_home.split('-')[1]
        home_goals_conceded = home_goals_conceded.replace('\n', '')[1:]
        home_goals_conceded = home_goals_conceded.split(' ')[0]
    
    except:
        home_goals_scored = 0
        home_goals_conceded = 0
        
    try:
        away_goals_scored = match_played_away.split('-')[1]
        away_goals_conceded = match_played_away.split('-')[0]
        away_goals_scored = away_goals_scored.replace('\n', '')[1:]
        away_goals_scored = away_goals_scored.split(' ')[0]
        
    except:
        away_goals_scored = 0
        away_goals_conceded= 0

    
    df_game_stats['Competition'].append(competition)
    df_game_stats['Opponent'].append(opponent)
    df_game_stats['Goals_scored_home'].append(home_goals_scored)
    df_game_stats['Goals_conceded_home'].append(home_goals_conceded)
    df_game_stats['Goals_scored_away'].append(away_goals_scored)
    df_game_stats['Goals_conceded_away'].append(away_goals_conceded)

df_game_stats_psv = pd.DataFrame(df_game_stats)

#%%
for i in df_game_stats_psv:
    try:
        df_game_stats_psv[i] = df_game_stats_psv[i].astype(int)
        
    except:
        continue
    
df_game_stats_psv['Goals_scored'] = df_game_stats_psv['Goals_scored_away'] + df_game_stats_psv['Goals_scored_home']
df_game_stats_psv['Goals_conceded'] = df_game_stats_psv['Goals_conceded_home'] + df_game_stats_psv['Goals_conceded_away']

df_game_stats_psv = df_game_stats_psv[['Competition', 'Goals_scored', 'Goals_conceded']]

