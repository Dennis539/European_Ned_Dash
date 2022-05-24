# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 22:14:15 2022

@author: denni
"""

import requests
import pandas as pd
import bs4
import copy

#%%
year = 1960
method = 1

df_coef = {'Club': [],
           'Rank': [],
           'Year':[]}
lock_2 = 0
while lock_2 == 0:
    print(method)
    lock_1 = 0
    while lock_1 == 0:
        url = f'https://kassiesa.net/uefa/data/method{method}/trank{year}.html'
        res = requests.get(url)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        try:
            soup.find('h1', {'style': 'margin:0; font-size:150px; line-height:150px; font-weight:bold;'}).getText() == '404'
            lock_1 = 1
            print('lock_1 activated')
        
        except:

            count = 0
            for i in soup.find_all('tr', {'class': 'clubline'}):

                if i.find_all('td')[3].getText() != 'Ned' and method > 4:
                    count = count + 1
                    continue
                
                elif i.find_all('td')[2].getText() != 'Ned' and method < 5 :
                    count = count + 1
                    continue

                
                else:
                    print(year)
                    print('--------------')
                    
                    if method < 5:
                        club = i.find_all('td')[1].getText()
                        
                    else:
                        club = i.find_all('td')[2].getText()
                        
                    rank = i.find_all('td')[0].getText()
                    
                    if rank == '':
                        count_2 = copy.deepcopy(count)
            
                    while rank == '':
                        #Changing the index. 

                        count_2 = count_2 - 1
                        soup_extra = soup.find_all('tr', {'class': 'clubline'})[count_2]
                        rank = soup_extra.find_all('td')[0].getText()
                    
                    print(rank)
                    df_coef['Club'].append(club)
                    df_coef['Rank'].append(rank)
                    df_coef['Year'].append(year)
                    count = count + 1
                    
        
            year = year + 1
                
    method = method + 1
    url = f'https://kassiesa.net/uefa/data/method{method}/trank{year}.html'
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    try:
        soup.find('h1', {'style': 'margin:0; font-size:150px; line-height:150px; font-weight:bold;'}).getText() == '404'
        lock_2 = 1
        
    except:
        continue

df_coef = pd.DataFrame(df_coef)

#%%
df_coef['Rank'] = df_coef['Rank'].astype(int)
df_coef.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coefficients\\Club_coefficients.xlsx')

# Kind of wanted to have the empty values as well as I did not want to have a line
# drawn when a club did not have a coefficient score. This was easily done by
# First creating a wide format as it would automatically populate all of the
# empty cells with nan. 
df_coef_wide = df_coef.pivot(index = 'Club', columns = 'Year', values = 'Rank').reset_index()
df_coef_long = pd.melt(df_coef_wide, id_vars = 'Club', value_name = 'Rank')
df_coef_long.to_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coefficients\\Club_coefficients_long.xlsx')



