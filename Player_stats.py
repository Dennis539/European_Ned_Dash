# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 21:12:21 2022

@author: denni
"""

import requests
#import requests_html
import bs4
import pandas as pd
import datetime
import time
import copy

#%%
def find_ref(soup_2):
    #Used for finding the referees
    div_ref = soup_2.find(string = 'Officials')
    refs = div_ref.find_parent('div').getText()
    refs = refs.split('\xa0·')
    for word in range(len(refs)):
        if word == 0:
            refs[word] = refs[word].replace('Officials:', '')
            
        refs[word].replace('\\xa0', '')
        refs[word] = refs[word][1:]
    return refs
    #refs = refs.str.replace('\xa0', ' ')
    
def table_club(soup_2, fbref_code, opponent, season, comp, link, opponent_link):
    df_2 = {'Player': [], 'Nationality': [], 'Position': [], 'Age': [], 
            'Minutes': [], 'Goals': [], 'Assists': [], 'Link': [],
            'Opponent': [], 'Season': [], 'Comp': [], 'Link_opponent': []}
    # So apparantly fbref keeps certain codes for every football club they have.
    stats_summary = f'stats_{fbref_code}_summary'
    soup_2_stats = soup_2.find('table', {'id': stats_summary}).select('tbody')[0]

    for j in range(len(soup_2_stats.find_all('tr'))):
        row = soup_2_stats.find_all('tr')[j]
        df_2['Player'].append(row.find('th').getText().replace('\xa0', ''))
        df_2['Nationality'].append(row.find_all('td')[1].getText())
        df_2['Position'].append(row.find_all('td')[2].getText())
        df_2['Age'].append(row.find_all('td')[3].getText())
        df_2['Minutes'].append(row.find_all('td')[4].getText())
        df_2['Goals'].append(row.find_all('td')[5].getText())
        df_2['Assists'].append(row.find_all('td')[6].getText())
        df_2['Opponent'].append(opponent)
        df_2['Season'].append(season)
        df_2['Comp'].append(comp)
        df_2['Link'].append(link)
        df_2['Link_opponent'].append(opponent_link)
        
    df_2 = pd.DataFrame(df_2)
    return df_2

def table_opponent(soup_2, opponent, link, opponent_link):
    # Also wanted to have information about the European opponents. 
    stat_opponent = soup_2.find(string = f'{opponent} Player Stats Table')
    table_opponents = stat_opponent.find_parent('table')
    table_opponents = table_opponents.select('tbody')[0]
    
    df_opponent_2 = {'Player': [], 'Nationality': [], 'Age': [], 'Minutes': [], 
                     'Goals': [], 'Assists': [],'Opponent': [], 'Link': [], 'Link_opponent': []}
    
    for j in range(len(table_opponents.find_all('tr'))):
        row = table_opponents.find_all('tr')[j]
        df_opponent_2['Player'].append(row.find('th').getText().replace('\xa0', ''))
        df_opponent_2['Nationality'].append(row.find_all('td')[1].getText())
        df_opponent_2['Age'].append(row.find_all('td')[3].getText())
        df_opponent_2['Goals'].append(row.find_all('td')[5].getText())
        df_opponent_2['Assists'].append(row.find_all('td')[6].getText())
        df_opponent_2['Minutes'].append(row.find_all('td')[4].getText())
        df_opponent_2['Opponent'].append(opponent)
        df_opponent_2['Link'].append(link)
        df_opponent_2['Link_opponent'].append(opponent_link)
    
    df_opponent_2 = pd.DataFrame(df_opponent_2)
    return df_opponent_2

def get_info_per_season(res, fbref_code, df_club, referees, df_opponent):
    global opponent_link

    kees = []
    
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    
    soup = soup.find('div', {'id': 'all_matchlogs'})
    soup = soup.select('tbody')[0]
    
    # The part below will remove a lot of the seasons where a team did not
    # play european football. This is because this will determine whether a 
    # team has played all of their matches in the same competition. This is 
    # because all teams not inside the Netherlands will not have this particular
    # part. 
    soup_3 = soup.find_all('span', {'class': 'f-i'})
    if len(soup_3) == 0:
        return
    
    for i in range(len(soup.find_all('tr'))):
        row = soup.find_all('tr')[i]
        #This part checks whether the match has been played in the first place. 
        #If the match has not been played yet, break out of the loop as all of
        #the results after this will also not have been played. 
        if 'Head-to-Head' in row.getText():
            break
        
        comp = row.find_all('td')[1].getText()
        
        # This check makes sure that only European competition are being searched through
        if comp in ('Eredivisie', 'Dutch Eredivisie', 'Eerste Divisie', 'Rel/Pro Play-offs'):
            continue
        
        link = row.find('th').select('a')[0]
        link = link.get_attribute_list('href')[0]
        
        # This part checks whether the match itself has already been saved 
        if link in df_club['Link'].values:
            kees.append(1)
            continue
            print('Match already saved')
        
        url = 'https://fbref.com' + link
        res_2 = requests.get(url)
        soup_2 = bs4.BeautifulSoup(res_2.text, 'html.parser')
        
        #Finding the opponent. Realizing later on that this could have been done
        #so much easier by finding it at the previous page. 
        soup_2_strong = soup_2.select('strong')
        for k in soup_2_strong:
            links = k.select('a')
            if links:
                links = links[0]
                club_links = links.get_attribute_list('href')
                club_links = club_links[0]
                if fbref_code not in club_links:
                    opponent = links.getText()
                    opponent_link = links['href']
                    #Getting the unique code for each club in the database. 
                    opponent_link = opponent_link.split('/')[3]
                    break



        referees.extend(find_ref(soup_2))
        try:
            
            df_club = pd.concat([df_club, 
                                 table_club(soup_2 = soup_2, fbref_code = fbref_code,
                                            opponent = opponent, season = season, 
                                            comp = comp, link = link, opponent_link = opponent_link)])
            df_opponent = pd.concat([df_opponent,
                                     table_opponent(soup_2 = soup_2, opponent = opponent, 
                                                    link = link, opponent_link = opponent_link)])
        
        except:
            opponent = row.find('td', {'data-stat': 'opponent'})
            opponent = opponent.find('a').getText()
            df_club = pd.concat([df_club, 
                                 table_club(soup_2 = soup_2, fbref_code = fbref_code, 
                                            opponent = opponent, season = season, 
                                            comp = comp, link = link,
                                            opponent_link = opponent_link)])
            df_opponent = pd.concat([df_opponent,
                                     table_opponent(soup_2 = soup_2, opponent = opponent,
                                                    link = link, opponent_link = opponent_link)])
    
        time.sleep(1)
    print('Season done')
    return df_club, referees, df_opponent

def reset_dataframes():
    df_club = pd.DataFrame({'Player': [], 'Nationality': [], 'Position': [], 'Age': [],
           'Minutes': [], 'Goals': [], 'Assists': [], 'Opponent': [], 
           'Season': [], 'Comp': [], 'Link': []})

    df_opponent = pd.DataFrame({'Player': [], 'Nationality': [], 'Age': [], 
                            'Minutes': [], 'Opponent': [], 'Link': []})

    return df_club, df_opponent


"""
Problem now is that all clubnames are still inconsistent. 
Idea: Every opponent will have a link. Try to use this link to find out what the
name of the club is in the current season. Always append this name within the dataframe. 
Only test this on one dataframe. If works, it will also work for the other dataframes. 

Also, there seems to be a mistake in the script in which some clubs have been done double. 

"""
#%%
"""
This script could roughly be divided in three parts. Part one is finding all of
the different seasons in which there is data from the club. This will get the
links from the different seasons from the club.
The second part looks at the differetn seasons of each club. Here, the European
matches will be found together with the links from these matches.
The third part looks at all the different matches and gets the information from
these matches. 
"""

referees = []

#%%
df_club, df_opponent = reset_dataframes()
#%%
count = 0
# AZ-Alkmaar
fbref_code = '3986b791'

res_origin = requests.get('https://fbref.com/en/squads/3986b791/history/AZ-Alkmaar-Stats-and-History#all_comps_intl_club_cup')
soup_origin = bs4.BeautifulSoup(res_origin.text, 'html.parser')

soup_origin = soup_origin.find('table', {'id': 'comps_fa_club_league'})
soup_origin = soup_origin.select('tbody')[0]

for i in range(len(soup_origin.find_all('th'))):
    season = soup_origin.find_all('th')[i].getText()
    
    print(season)

        
    # Finding all but the current season. 
    try:
        res = requests.get(f'https://fbref.com/en/squads/3986b791/{season}/AZ-Alkmaar-Stats')
        
    # Finding the current season. 
    except:
        res = requests.get('https://fbref.com/en/squads/3986b791/AZ-Alkmaar-Stats')
    try:
        df_club, referees, df_opponent = get_info_per_season(res, fbref_code, df_club, referees, df_opponent)
    
    except:
        print('not now')

    
    count = count + 1
    
    if count % 9 == 0:
        time.sleep(55)

    time.sleep(5)
    
df_players_az = copy.deepcopy(df_club)
df_players_az['Club'] = 'Az Alkmaar'
df_opponents_players_az = copy.deepcopy(df_opponent)
df_opponents_players_az['Club'] = 'Az Alkmaar'


#%%
df_club, df_opponent = reset_dataframes()

# Ajax
fbref_code = '19c3f8c4'

res_origin = requests.get('https://fbref.com/en/squads/19c3f8c4/history/Ajax-Stats-and-History#all_comps_intl_club_cup')
soup_origin = bs4.BeautifulSoup(res_origin.text, 'html.parser')

soup_origin = soup_origin.find('table', {'id': 'comps_fa_club_league'})
soup_origin = soup_origin.select('tbody')[0]

for i in range(len(soup_origin.find_all('th'))):
    season = soup_origin.find_all('th')[i].getText()
    
    if season in df_club['Season'].unique():
        print(season)
        continue
    # Finding all but the current season. 
    try:
        res = requests.get(f'https://fbref.com/en/squads/19c3f8c4/{season}/Ajax-Stats')
        
    # Finding the current season. 
    except:
        res = requests.get('https://fbref.com/en/squads/19c3f8c4/Ajax-Stats')
    
    df_club, referees, df_opponent = get_info_per_season(res, fbref_code, df_club, referees, df_opponent)
    count = count + 1
    if count % 9 == 0:
        time.sleep(50)

    time.sleep(10)

df_players_ajax = copy.deepcopy(df_club)
df_players_ajax['Club'] = 'Ajax'
df_opponents_players_ajax = copy.deepcopy(df_opponent)
df_opponents_players_ajax['Club'] = 'Ajax'

#%%
time.sleep(60)

df_club, df_opponent = reset_dataframes()

# PSV-eindhoven
fbref_code = 'e334d850'

res_origin = requests.get('https://fbref.com/en/squads/e334d850/history/PSV-Eindhoven-Stats-and-History')
soup_origin = bs4.BeautifulSoup(res_origin.text, 'html.parser')

soup_origin = soup_origin.find('table', {'id': 'comps_fa_club_league'})
soup_origin = soup_origin.select('tbody')[0]

for i in range(len(soup_origin.find_all('th'))):
    season = soup_origin.find_all('th')[i].getText()

    if season in df_club['Season'].unique():
        print(season)
        continue

    # Finding all but the current season. 
    try:
        res = requests.get(f'https://fbref.com/en/squads/e334d850/{season}/PSV-Eindhoven-Stats')
        
    # Finding the current season. 
    except:
        res = requests.get('https://fbref.com/en/squads/e334d850/PSV-Eindhoven-Stats')
    
    df_club, referees, df_opponent = get_info_per_season(res, fbref_code, df_club, referees, df_opponent)
    time.sleep(10)
    
    count = count + 1
    if count % 9 == 0:
        time.sleep(50)

    time.sleep(10)

df_players_psv = copy.deepcopy(df_club)
df_players_psv['Club'] = 'PSV'

df_opponents_players_psv = copy.deepcopy(df_opponent)
df_opponents_players_psv['Club'] = 'PSV'

time.sleep(60)

#%%
df_club, df_opponent = reset_dataframes()

# Feyenoord
fbref_code = 'fb4ca611'

res_origin = requests.get('https://fbref.com/en/squads/fb4ca611/history/Feyenoord-Stats-and-History')
soup_origin = bs4.BeautifulSoup(res_origin.text, 'html.parser')

soup_origin = soup_origin.find('table', {'id': 'comps_fa_club_league'})
soup_origin = soup_origin.select('tbody')[0]

for i in range(len(soup_origin.find_all('th'))):
    season = soup_origin.find_all('th')[i].getText()

    if season in df_club['Season'].unique():
        print(season)
        continue
    
    # Finding all but the current season. 
    try:
        res = requests.get(f'https://fbref.com/en/squads/fb4ca611/{season}/Feyenoord-Stats')
        
    # Finding the current season. 
    except:
        res = requests.get('https://fbref.com/en/squads/fb4ca611/Feyenoord-Stats')
    
    try:
        df_club, referees, df_opponent = get_info_per_season(res, fbref_code, df_club, referees, df_opponent)
    
    except:
        print('Skipped season')
    time.sleep(10)
    
    count = count + 1
    if count % 9 == 0:
        time.sleep(50)

    time.sleep(10)

df_players_feyenoord = copy.deepcopy(df_club)
df_players_feyenoord['Club'] = 'Feyenoord'
df_opponents_players_feyenoord = copy.deepcopy(df_opponent)
df_opponents_players_feyenoord['Club'] = 'Feyenoord'

time.sleep(60)

#%%
# Fc_Twente
df_club, df_opponent = reset_dataframes()

fbref_code = 'a1f721d3'

res_origin = requests.get('https://fbref.com/en/squads/a1f721d3/history/Twente-Stats-and-History')
soup_origin = bs4.BeautifulSoup(res_origin.text, 'html.parser')

soup_origin = soup_origin.find('table', {'id': 'comps_fa_club_league'})
soup_origin = soup_origin.select('tbody')[0]

for i in range(len(soup_origin.find_all('th'))):
    season = soup_origin.find_all('th')[i].getText()

    print(season)
    # Finding all but the current season. 
    try:
        res = requests.get(f'https://fbref.com/en/squads/a1f721d3/{season}/Twente-Stats')
        
    # Finding the current season. 
    except:
        res = requests.get('https://fbref.com/en/squads/a1f721d3/Twente-Stats')
    
    
    try:
        df_club, referees, df_opponent = get_info_per_season(res, fbref_code, df_club, referees, df_opponent)
    
    except:
        print('Skipped season')
    
    count = count + 1
    if count % 9 == 0:
        time.sleep(50)

    time.sleep(10)

df_players_twente = copy.deepcopy(df_club)
df_players_twente['Club'] = 'Twente'
df_opponents_players_twente = copy.deepcopy(df_opponent)
df_opponents_players_twente['Club'] = 'Twente'


#%%
df_totaal = pd.concat([df_players_ajax, df_players_az])
df_totaal = pd.concat([df_totaal, df_players_feyenoord])
df_totaal = pd.concat([df_totaal, df_players_psv])
df_totaal = pd.concat([df_totaal, df_players_twente])

df_totaal.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Players\\df_totaal_players.xlsx')

#%%
df_totaal_tegenstander = pd.concat([df_opponents_players_ajax, df_opponents_players_az])
df_totaal_tegenstander = pd.concat([df_totaal_tegenstander, df_opponents_players_feyenoord])
df_totaal_tegenstander = pd.concat([df_totaal_tegenstander, df_opponents_players_psv])
df_totaal_tegenstander = pd.concat([df_totaal_tegenstander, df_opponents_players_twente])

df_totaal_tegenstander.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Players\\df_totaal_players_opponents.xlsx')



