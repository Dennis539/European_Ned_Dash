# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 09:47:22 2022

@author: denni
"""

import dash
from dash import Dash, Input, Output, callback, dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import numpy as np
import json
import requests
import urlopen


import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from plotly.offline import plot
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign
import os
import dash_table
import copy
from haversine import haversine, Unit

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from plotly.subplots import make_subplots


#%%
df_test = px.data.election()
geojson_test = px.data.election_geojson()

#%%
os.chdir('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\Voetbal_dashboard')


df_totaal = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\Tegenstanders_totaal.xlsx')
df_clubs = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\df_clubs.xlsx')
df_totaal_merge = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coordinate calculation\\df_totaal_distances.xlsx')
df_coef = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coefficients\\Club_coefficients.xlsx')
df_coef_long = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Coefficients\\Club_coefficients_long.xlsx')
df_totaal_players_opponents = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Players\\df_totaal_players_opponents.xlsx')
df_totaal_players = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Players\\df_totaal_players.xlsx')
df_totaal_players_2 = pd.read_excel('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Players\\df_totaal_players.xlsx')

#%%
# So apparantly the position of one player is missing. Filling this.
df_totaal_players['Position'].fillna('GK', inplace = True)

# Making age numerical 
df_totaal_players['Age'] = df_totaal_players['Age'].str.replace('-', '.').astype(float)

df_totaal_players['Age_year'] = df_totaal_players['Age'].apply(lambda x: str(x).split('.')[0])
df_totaal_players['Age_day'] = (df_totaal_players['Age'].apply(lambda x: str(x).split('.')[1]).astype(int) / 365) * 1000
df_totaal_players['Age_day'] = df_totaal_players['Age_day'].round(0).astype(int)
df_totaal_players['Age_normalized'] = df_totaal_players['Age_year'] + '.' + df_totaal_players['Age_day'].astype(str)
df_totaal_players['Age_normalized'] = df_totaal_players['Age_normalized'].astype(float)

df_totaal_players_opponents['Age'] = df_totaal_players_opponents['Age'].str.replace('-', '.').astype(float)
df_totaal_players_opponents.fillna(0, inplace = True)

df_totaal_players_opponents['Age_year'] = df_totaal_players_opponents['Age'].apply(lambda x: str(x).split('.')[0])
df_totaal_players_opponents['Age_day'] = (df_totaal_players_opponents['Age'].apply(lambda x: str(x).split('.')[1]).astype(int) / 365) * 1000
df_totaal_players_opponents['Age_day'] = df_totaal_players_opponents['Age_day'].round(0).astype(int)
df_totaal_players_opponents['Age_normalized'] = df_totaal_players_opponents['Age_year'] + '.' + df_totaal_players['Age_day'].astype(str)
df_totaal_players_opponents['Age_normalized'] = df_totaal_players_opponents['Age_normalized'].astype(float)

df_coef_long['Club'].replace({'AZ Alkmaar': 'Az Alkmaar', 'FC Twente Enschede': 'Twente', 'PSV Eindhoven': 'PSV'}, inplace = True)

df_totaal_players_opponents.Club.unique()


discrete_colors = [ 'tan', 'Goldenrod', 'Darkgoldenrod','Peru','Sienna', 'Saddlebrown', 
                   'DarkMagenta', 'Darkviolet','Indigo', 'Midnightblue']



#%%
# Slightly changing the positions. 

def position_change(pos):
    if pos.split(',')[0] in ('RW', 'FW', 'LW'):
        pos = 'Attacker'
    elif pos.split(',')[0] in ('RM', 'CM', 'AM', 'DM', 'LM', 'MF'):
        pos = 'Midfielder'
    elif pos.split(',')[0] == 'GK':
        pos = 'Goalkeeper'
    else:
        pos = 'Defender'
        
    return pos

#%%
df_totaal_players['Position'] = df_totaal_players['Position'].apply(position_change)
df_goals_against = df_totaal_players_opponents.groupby('Link').sum()['Goals'].reset_index()

df_totaal_players = df_totaal_players.merge(df_goals_against, how = 'left', on = 'Link')\
    .rename(columns = {'Goals_x': 'Goals', 'Goals_y' : 'Conceded'})


#%%
dict_df = {}
Stats_tegenstanders_totaal = pd.DataFrame(columns = ['Unnamed: 0', 'Club', 'Played', 'Country', 'Ref', 'Win', 'Draw',
       'Loss'])

for i in df_totaal['Original_club'].unique():
    dict_df[i] = pd.read_excel(f'\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Stats tegenstanders\\Stats_tegenstanders_{i}.xlsx')
    Stats_tegenstanders_totaal = pd.concat([Stats_tegenstanders_totaal, dict_df[i]])



df_countries = df_totaal.drop_duplicates(subset = 'Country')[
    ['Country', 'Country_english']]

df_countries.to_excel('df_countries.xlsx')


Stats_tegenstanders_totaal = Stats_tegenstanders_totaal.merge(
    df_countries, how = 'left', on = 'Country')

# Removing spaces before the word starts
for i in range(len(Stats_tegenstanders_totaal)):
    if Stats_tegenstanders_totaal['Country_english'].loc[i][0] == ' ':
        Stats_tegenstanders_totaal.at[i, 'Country_english'] = Stats_tegenstanders_totaal.loc[i]['Country_english'][1:]

Stats_tegenstanders_totaal['Country_english'] = Stats_tegenstanders_totaal['Country_english'].str.replace('\xa0', '')

Stats_tegenstanders_totaal['Country_english'] = Stats_tegenstanders_totaal[
    'Country_english'].str.capitalize()
Stats_tegenstanders_country = Stats_tegenstanders_totaal.groupby(
    'Country_english').sum()[['Played', 'Win', 'Draw', 'Loss']].reset_index()
Stats_tegenstanders_country['Win_ratio'] = round(
    Stats_tegenstanders_country['Win'] / Stats_tegenstanders_country['Played'], 2)

# Removing the Netherlands from the dataset as including it doesn't make sense
Stats_tegenstanders_country = Stats_tegenstanders_country.rename(columns = {'Country_english': 'Country'})

Stats_tegenstanders_country_2 = Stats_tegenstanders_country[Stats_tegenstanders_country['Country'] != 'The netherlands']
Stats_tegenstanders_country_10_high = Stats_tegenstanders_country_2.sort_values('Win_ratio', ascending=False).head(10)
Stats_tegenstanders_country_10_high = Stats_tegenstanders_country_10_high.drop(['Draw', 'Loss'], axis = 1)
Stats_tegenstanders_country_10_low = Stats_tegenstanders_country_2.sort_values('Win_ratio', ascending=False).tail(10)
Stats_tegenstanders_country_10_low = Stats_tegenstanders_country_10_low.drop(['Draw', 'Loss'], axis = 1)



#%%
"""
Creating the map which will show all of the locations Dutch teams have played. 
"""

clubs_map = px.scatter_mapbox(df_totaal,
                              lon = df_totaal['Longitude'],
                              lat = df_totaal['Latitude'],
                              hover_name = df_totaal['Club'], 
                              color = df_totaal['Original_club'],
                              zoom = 2.5)

clubs_map.update_layout(mapbox_style="carto-positron", dragmode = False)

clubs_map_dash = html.Div([dcc.Graph(id = 'European wins opponents Dutch clubs',
                                  figure = clubs_map, style = {'height': '140vh'})
                        ], style = {'padding': '2em','top': '100px', 'height': '1000px', 'width': '1450px', 
                                    'background-color': 'lightgray'})



#%%
"""
Creating a map which shows the distribution of wins per country. 
"""


with open ('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\Euro_coordinates.json') as file:
    json_file = json.load(file)
    file.close()
win_map = go.Figure(go.Choroplethmapbox(geojson = json_file,
                               z = Stats_tegenstanders_country.Played, featureidkey = 'properties.NAME',
                               locations = Stats_tegenstanders_country.Country,
                               colorscale = 'Reds'))

win_map.update_traces(showscale=False)

win_map.update_layout(width = 580, height = 400, 
                      margin=dict(l=0, r=0, t=0, b=0),mapbox_zoom=1.9, 
                      mapbox_center = {'lat': 55.4833314, 'lon': 25.7999968},
                      mapbox_style="carto-positron")


win_map_dash = html.Div([html.H3(children = 'Country play frequency', 
                                 style = { 'text-align': 'center'}), 
                         dcc.Graph(id = 'European opponents Dutch clubs',figure = win_map, 
                                  style = {'height': '450px', })],
                        style = {'position': 'absolute', 'left': '900px',
                                 'padding-left': '1em', 'width': '580px', 
                                 'top': '50px'})




#%%
"""
Creating a table which shows the furthest opponents from the respective clubs. 
The first part creates a dictionary of the dataset such that it can be used 
for the DataTable. 
"""

Win_table_top = html.Div([

            html.H3(children = 'Top 10 countries with highest win rate'),
            dash_table.DataTable(
                id = 'bla',
                data = Stats_tegenstanders_country_10_high.to_dict('records'),
                columns = [{'name': i, 'id': i} for i in Stats_tegenstanders_country_10_high.columns],
                style_cell_conditional = [
                    {'if': {'column_id': 'Country'}, 'width': '50%'},
                    {'if': {'column_id': 'Played'}, 'width': '15%'},
                    {'if': {'column_id': 'Win'}, 'width': '15%'},
                    {'if': {'column_id': 'Win_ratio'}, 'width': '20%'}])], 
            style = {'height': '750px','width': '400px',
                     'position': 'absolute', 'left': '600px','padding': '1em',
                     'padding-top': '1em', 'z-index': '100'})

Win_table_bottom = html.Div([
    html.H3(children = 'Top 10 countries with lowest win rate'), 
    dash_table.DataTable(
        id = 'blab',
        data = Stats_tegenstanders_country_10_low.to_dict('records'),
    columns = [{'name': i, 'id': i} for i in Stats_tegenstanders_country_10_low.columns],
    style_cell_conditional = [
            {'if': {'column_id': 'Country'}, 'width': '50%'},
            {'if': {'column_id': 'Played'}, 'width': '15%'},
            {'if': {'column_id': 'Win'}, 'width': '15%'},
            {'if': {'column_id': 'Win_ratio'}, 'width': '20%'}])], 
                                   style = {'height': '750px', 
                                            'position': 'absolute', 'left': '1100px',
                                            'padding': '1em', 'padding-top': '1em'
                                            })


"""
Creating a chart to show the distribution of played games from the dutch teams. 
"""

df_sum_played = df_totaal.groupby('Original_club').sum()['Played'].reset_index()
df_count_played = df_totaal.groupby('Original_club').count()['Played'].reset_index()

fig = make_subplots(rows = 1, cols = 2, specs = [[{'type': 'domain'}, {'type': 'domain'}]], 
                    subplot_titles=('Total games played', 'Unique opponents played'))

fig.add_trace(go.Pie(labels = df_sum_played['Original_club'], values = df_sum_played['Played'], 
                     name = 'Played games'), 1, 1)
fig.add_trace(go.Pie(labels = df_count_played['Original_club'], values = df_count_played['Played'], 
                     name = 'Unique opponents'), 1,2)
fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 500, height = 250, paper_bgcolor = 'whitesmoke'
                  )

chart_played_dash = html.Div([html.H3('Total opponents and Unique opponents', style = {'text-align': 'center'}), 
                              dcc.Graph(figure = fig)], 
                             style = {'position': 'absolute', 'height': '850px', 'top': '50px',
                                      'left': '1000px','padding-top': '1em', 
                                      'padding-bottom': '1em'})

#%%
club_dict = {}
for i in df_totaal_merge['Original_club'].unique():
    df_top = df_totaal_merge[
        df_totaal_merge['Original_club'] == i][
            ['Club', 'Original_club', 'Distance']].sort_values(
                'Distance', ascending = False).head()
                
    club_dict[i] = df_top[['Club', 'Original_club', 'Distance']]

club_dict_tot = pd.concat([club_dict['Feyenoord'], club_dict['PSV'], club_dict['Ajax'],
                           club_dict['AZ Alkmaar'], club_dict['Fc_Twente']])



Dropdown_distance = html.Div([
    html.H3(children = 'Distance table', style = {'font-size': '32px'}),
    dcc.Dropdown(id = 'distance_dropdown',options = list(club_dict.keys()),
                 value = 'Feyenoord')
    ], style = {'position': 'absolute', 'width': '20%', 'left': '25px',
                'height':'100px', 'top': '5px'})

Distance_table = html.Div([dash_table.DataTable(
    id = 'distance_table',
    data = club_dict['Feyenoord'].to_dict('records'),
    columns = [{'name': i, 'id': i} for i in club_dict['Feyenoord'].columns])], 
    style = {'position': 'absolute', 'height': '350px','width': '300px', 'left': '25px', 
             'top': '200px', 'z-index': '1'})



#%%






#%%
x = df_totaal_players_opponents.groupby('Player').count()['Minutes'].sort_values(ascending = False).head(10)
df_x = pd.DataFrame(x.reset_index())



fig = px.bar(df_x, x = 'Minutes', y = 'Player', orientation = 'h')

Most_Matches_played_against = html.Div([
    html.H3(children = 'Opponent player with the most minutes',style = { 'text-align': 'center'}),
    dcc.Graph(id = 'graph_players_most_freq_played_against', figure = fig)],
    style = {'position': 'absolute', 'height': '550px','width': '400px'})

Dropdown_player_club = html.Div(
    [html.H1(children = 'Club', style = {'color': 'black', 'text-align': 'center', 'font-size': '30px'}),
     dcc.RadioItems(id = 'player_club_dropdown', inputStyle={"margin-left": "19px"},
                  options = list(df_totaal_players['Club'].unique()) + ['Select all'],
                  value = 'Select all', inline = True,
                  style = {'position': 'absolute', 'bottom': '0px', 
                           'width': '800px', 'color': 'black', 'font-size': '24px'})], 
    style = {'position': 'absolute', 'width': '700px', 'left': '400px', 'height': '100px','top': '25px'})

opponent_player_most_goals = df_totaal_players_opponents.\
    groupby('Player').sum()['Goals'].sort_values(ascending = False).head(10).sort_values()
df_player_opponent_most_goals = pd.DataFrame(opponent_player_most_goals.reset_index())

fig_opponent_most_goals = px.bar(df_player_opponent_most_goals, x = 'Goals', 
                                 y = 'Player', text = 'Goals', orientation = 'h', 
                                 color = discrete_colors, color_discrete_map="identity")
fig_opponent_most_goals.update_layout(margin=dict(l=0, r=0, t=20, b=0), 
                                      width = 450, height = 400,
                                      plot_bgcolor= 'white', paper_bgcolor = 'white',
                                      hoverlabel = dict(
                                          bgcolor = 'lightgray',
                                          font_size = 14))
fig_opponent_most_goals.update_coloraxes(showscale=False)
fig_opponent_most_goals.update(layout_showlegend=False)

opponent_most_goals_scored = html.Div([
    html.H3(children = 'Opponent team with the most goals', style = { 'text-align': 'center'}),
    dcc.Graph(id = 'graph_players_most_scored_opponent', figure = fig_opponent_most_goals)],
    style = {'position': 'absolute', 'height': '550px','width': '400px', 'left': '50px', 'top': '50px'})




opponent_player_oldest = df_totaal_players_opponents.\
    groupby('Player').max('Age')['Age'].sort_values(ascending = False).head(1).sort_values()


card_oldest_opponent = html.Div(id = 'Oldest_opponent', children = dbc.Card(
    [dbc.CardHeader("Oldest opponent:", style = {'text-align': 'center'}),
     dbc.CardBody(
         html.H2(f"{opponent_player_oldest.index[0]}\n{opponent_player_oldest[0]} years", className="card-title", 
                 style = {'font-size': '40px', 'text-align': 'center'})
         ),
    ], outline = True, color = 'primary',
    style={'position': 'absolute', "width": "450px", 'height': '150px', 
           'top': '50px', 'border-style': 'solid', 'border-color': 'black', 
           'box-shadow': '10px 10px', 'border-width': 'thin'},
), style = {'position': 'absolute', 'width': '450px', 'left': '1100px', 'top': '250px'})



#%%





#%%
"""
This dataframe shows the frequency of how often Dutch teams have faced
a certain opponent. 
"""
# PSV and Feyenoord met each other once in an european match, meaning this match
# Should be twice in this dataset. This can be achieved by including a combination
# of Link and Link_opponent within the remove duplicates argument. 
df_unique_opponents = df_totaal_players.drop_duplicates(subset= ['Link', 'Link_opponent'])

df_unique_opponents_club = \
    pd.DataFrame(df_unique_opponents.groupby('Link_opponent')\
                 .count()['Club'].sort_values(ascending = False).reset_index())


df_unique_opponents_club = df_unique_opponents_club.\
    merge(df_unique_opponents[['Opponent', 'Link_opponent']].drop_duplicates(subset = ['Link_opponent']), 
          how = 'left', ).\
        drop_duplicates(subset = ['Opponent']).\
            rename(columns = {'Club': 'Total_matches_played_against'}).\
            reset_index(drop = True)

"""
This dataframe shows the amount of goals scored against opponents. 
"""
df_unique_goal = \
    pd.DataFrame(df_totaal_players.groupby('Link_opponent')
                 .sum()['Goals'].sort_values(ascending = False).reset_index())
    
df_unique_goal = df_unique_goal.\
    merge(df_unique_opponents[['Link_opponent', 'Opponent']].drop_duplicates(subset = ['Link_opponent']), 
          how = 'left', ).drop_duplicates(subset = ['Opponent']).\
        rename(columns = {'Club': 'Total_matches_played_against'})\
            .reset_index(drop = True)


df_unique_stats = df_unique_goal.merge(df_unique_opponents_club, how = 'left', on = 'Link_opponent').\
    rename(columns = {'Opponent_x': 'Opponent', 'Goals': 'Goals_scored_against'}).reset_index(drop = True).\
        drop(['Opponent_y'], axis =1)


fig_club_opponent_most_goals_conceded = \
    px.scatter(
        df_unique_stats, x = 'Total_matches_played_against', 
        y = 'Goals_scored_against', labels={
            'Total_matches_played_against': 'Matches played',
            'Goals_scored_against': 'Goals conceded'},
        hover_name = 'Opponent'
        )
    
fig_club_opponent_most_goals_conceded.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 450, height = 400,
                  plot_bgcolor= 'white',
                  paper_bgcolor = 'white',        
                  hoverlabel = dict(
                              bgcolor = 'lightgray',
                              font_size = 14))

fig_club_opponent_most_goals_conceded.update_xaxes(zeroline = True, zerolinewidth = 2, zerolinecolor = 'black')
fig_club_opponent_most_goals_conceded.update_yaxes(zeroline = True, zerolinewidth = 2, zerolinecolor = 'black')


opponent_club_most_goals_conceded = html.Div([
    html.H3(children = 'Opponent matches vs. goals conceded', style = { 'text-align': 'center'}),
    dcc.Graph(id = 'graph_clubs_most_conceded_opponent', figure = fig_club_opponent_most_goals_conceded)],
    style = {'position': 'absolute', 'height': '550px','width': '400px', 'left': '600px'})



#%%
"""
This dataframe shows the amount of goals scored by opponents. 
"""
df_unique_opponents = df_totaal_players_opponents.drop_duplicates(subset= ['Link', 'Link_opponent'])

df_unique_opponents_club = \
    pd.DataFrame(df_unique_opponents.groupby('Link_opponent')\
                 .count()['Club'].sort_values(ascending = False).reset_index())


df_unique_opponents_club = df_unique_opponents_club.\
    merge(df_unique_opponents[['Opponent', 'Link_opponent']].drop_duplicates(subset = ['Link_opponent']), 
          how = 'left', ).\
        drop_duplicates(subset = ['Opponent']).\
            rename(columns = {'Club': 'Total_matches_played_against'}).\
            reset_index(drop = True).head(10).sort_values(by = 'Total_matches_played_against', ascending = True)
            
fig = px.bar(df_unique_opponents_club, x = 'Total_matches_played_against', y = 'Opponent', orientation = 'h',
             color=discrete_colors, color_discrete_map="identity")

fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 500, height = 400,
                  plot_bgcolor= 'white',
                  paper_bgcolor = 'white',        
                  hoverlabel = dict(
                              bgcolor = 'lightgray',
                              font_size = 14))

fig.update_coloraxes(showscale=False)
fig.update(layout_showlegend=False)


Opponent_most_matches_played_against = html.Div([
    html.H3(children = 'Most frequently faced opponent', style = { 'text-align': 'center'}),
    dcc.Graph(id = 'graph_clubs_faced_scored_opponent', figure = fig)],
    style = {'position': 'absolute', 'height': '550px','width': '350px', 'left': '400px',
             'top': '50px'})

"""
This dataframe shows the amount of goals conceded by opponents. 
"""
df_unique_goal_opponents = \
    pd.DataFrame(df_totaal_players_opponents.groupby('Link_opponent')
                 .sum()['Goals'].sort_values(ascending = False).reset_index())
    
df_unique_goal_opponents = df_unique_goal_opponents.\
    merge(df_unique_opponents[['Link_opponent', 'Opponent']].drop_duplicates(subset = ['Link_opponent']), 
          how = 'left', ).drop_duplicates(subset = ['Opponent']).\
        rename(columns = {'Club': 'Total_matches_played_against'})\
            .reset_index(drop = True).head(10).sort_values(by = 'Goals', ascending = True)

fig = px.bar(df_unique_goal_opponents, x = 'Goals', y = 'Opponent', orientation = 'h',
             color = discrete_colors, color_discrete_map="identity")
fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 500, height = 400,
                  plot_bgcolor= 'white',
                  paper_bgcolor = 'white',        
                  hoverlabel = dict(
                              bgcolor = 'lightgray',
                              font_size = 14))

fig.update_coloraxes(showscale=False)
fig.update(layout_showlegend=False)
opponent_club_most_goals_scored = html.Div([
    html.H3(children = 'Opponent with the most goals scored', style = { 'text-align': 'center'}),
    dcc.Graph(id = 'graph_clubs_most_scored_opponent', figure = fig)],
    style = {'position': 'absolute', 'height': '550px','width': '400px', 'left': '0px', ' top': '50px'})





#%%





#%%
Dropdown_player_club_2 = html.Div(
    [html.H3(children = 'Club', style = {'color': 'white', 'text-align': 'center'}),
     dcc.Dropdown(id = 'player_club_dropdown_2', 
                  options = list(df_totaal_players['Club'].unique()) + ['Select all'],
                  value = 'Select all',
                  style = {'position': 'absolute', 'bottom': '0px', 'width': '300px'})], 
    style = {'position': 'absolute', 'width': '300px', 'left': '60px', 'height': '100px',
             'background-color': 'dimgray','top': '25px'})


Dropdown_player_nationality = html.Div(
    [html.H3(children = 'Nationality', style = {'color': 'white', 'text-align': 'center'}),
     dcc.Dropdown(id = 'player_nationality', 
                  options = ['Select all'] + list(df_totaal_players['Nationality'].unique()),
                  value = 'Select all',
                  style = {'position': 'absolute', 'bottom': '0px', 'width': '300px', })], 
    style = {'position': 'absolute', 'width': '300px', 'left': '420px', 'height': '100px',
             'background-color': 'dimgray','top': '25px'})


Dropdown_player_competition = html.Div(
    [html.H3(children = 'Competition', style = {'color': 'white', 'text-align': 'center'}),
     dcc.Dropdown(id = 'player_competition', 
                  options = ['Select all'] + list(df_totaal_players['Comp'].unique()),
                  value = 'Select all',
                  style = {'position': 'absolute', 'bottom': '0px', 'width': '300px', })], 
    style = {'position': 'absolute', 'width': '300px', 'left': '780px', 'height': '100px',
             'background-color': 'dimgray','top': '25px'})

Dropdown_player_position = html.Div(
    [html.H3(children = 'Competition', style = {'color': 'white', 'text-align': 'center'}),
     dcc.Dropdown(id = 'player_position', 
                  options = ['Select all'] + list(df_totaal_players['Position'].unique()),
                  value = 'Select all',
                  style = {'position': 'absolute', 'bottom': '0px', 'width': '300px', })], 
    style = {'position': 'absolute', 'width': '300px', 'left': '1140px', 'height': '100px',
             'background-color': 'dimgray','top': '25px'})


Player_most_matches_played = pd.DataFrame(
    df_totaal_players.groupby(['Player'])['Nationality'].count().reset_index().\
        rename(columns = {'Nationality': 'Matches'}))
Player_most_matches_played_top_10 = Player_most_matches_played.\
    sort_values('Matches', ascending = False).head(10).sort_values('Matches', ascending = True)
    
    
Player_most_goals_scores = pd.DataFrame(
    df_totaal_players.groupby(['Player'])['Goals'].sum().reset_index())
Player_most_goals_scores_top_10 = Player_most_goals_scores.\
    sort_values(by = 'Goals', ascending = False).head(10).sort_values(by = 'Goals', ascending = False)

fig = px.bar(Player_most_matches_played_top_10, x = 'Matches', y = 'Player', orientation = 'h',
             color = discrete_colors, color_discrete_map="identity")

fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 450, height = 400,
                  plot_bgcolor= 'white',
                  paper_bgcolor = 'white',        
                  hoverlabel = dict(
                              bgcolor = 'lightgray',
                              font_size = 14))

fig.update_coloraxes(showscale=False)
fig.update(layout_showlegend=False)
Player_most_matches_played_top_10 = html.Div([
    html.H3(children = 'Eredivisie player with the most minutes',style = { 'text-align': 'center'}),
    dcc.Graph(id = 'graph_players_most_freq_played', figure = fig)],
    style = {'position': 'absolute', 'height': '550px','width': '500px'})

df_player_merge = Player_most_matches_played.merge(Player_most_goals_scores, how = 'left')

fig = px.scatter(df_player_merge, x = 'Matches', y = 'Goals', hover_name= 'Player')
fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 450, height = 400,
                  plot_bgcolor= 'white',
                  paper_bgcolor = 'white',        
                  hoverlabel = dict(
                              bgcolor = 'lightgray',
                              font_size = 14))
fig.update_xaxes(zeroline = True, zerolinewidth = 2, zerolinecolor = 'black')
fig.update_yaxes(zeroline = True, zerolinewidth = 2, zerolinecolor = 'black')
Matches_vs_goals = html.Div([
    html.H3(id = 'H3_matches_vs_goals', children = 'Goals per minutes', style = {'text-align': 'center'}),
    dcc.Graph(id = 'matches_vs_goals', figure = fig)],
    style = {'position': 'absolute', 'height': '550px', 'width': '800px', 'left': '550px'})

Player_oldest = df_totaal_players.groupby('Player')['Age'].max().sort_values(ascending = False).head(10).reset_index()

fig = px.bar(Player_oldest, x = 'Age', y = 'Player', orientation='h', color = discrete_colors, color_discrete_map="identity")
fig.update_coloraxes(showscale=False)
fig.update(layout_showlegend=False)

Oldest_players_top_10 = html.Div([
    html.H3(children = 'Oldest player',style = { 'text-align': 'center'}),
    dcc.Graph(id = 'graph_players_oldest', figure = fig)],
    style = {'position': 'absolute', 'height': '550px','width': '500px', 'left': '0px'})

card = html.Div(id = 'unique_players_in_europe', children = 
    dbc.Card(
    [dbc.CardHeader("Unique players in Europe", style = {'text-align': 'center'}),
     dbc.CardBody(
         html.H2(f"{len(df_totaal_players['Player'].unique())}", className="card-title", 
                 style = {'font-size': '40px', 'text-align': 'center'})
         ),
    ], outline = True, color = 'primary',
    style={'position': 'absolute', "width": "250px", 'left': '1200px', 'height': '150px', 
           'top': '50px', 'border-style': 'solid', 'border-color': 'black', 
           'box-shadow': '10px 10px', 'border-width': 'thin'},
), style={'position': 'absolute', "width": "250px", 'left': '1200px'})



avg_age_normalized = str(round(np.mean(df_totaal_players['Age_normalized']), 3))
decimal = (int(avg_age_normalized.split('.')[1]) / 1000) * 365
avg_days = round(decimal)
avg_year = avg_age_normalized.split('.')[0]



card_2 = html.Div(id = 'average_age', children = [dbc.Card( children = 
    [dbc.CardHeader("Average age:", style = {'text-align': 'center'}),
     dbc.CardBody(
         html.H2(f"{avg_year} years and {avg_days} days", className="card-title", 
                 style = {'font-size': '40px', 'text-align': 'center'})
         ),
    ],
    style={'position': 'absolute', "width": "250px", 'left': '0px', 
           'border-style': 'solid', 'border-color': 'black', 
           'box-shadow': '10px 10px',  'border-width': 'thin'},
)], style = {'position': 'absolute', "width": "250px", 'left': '150px', 'height': '150px', 'bottom': '50px'})

"""
Coefficient chart
"""
line_color = iter(['Green', 'Red', 'Gold', 'Blue', 'Purple'])
fig = go.Figure()
for i in df_coef_long['Club'].unique():
    df_coef_long_2 = df_coef_long[df_coef_long['Club'] == i]
    if i in df_totaal_players['Club'].unique():
        fig.add_trace(go.Scatter(x = df_coef_long_2['Year'], y = df_coef_long_2['Rank'],
                                 mode = 'lines', name = df_coef_long_2['Club'].unique()[0],
                                 line_color = next(line_color)))

    else:
        fig.add_trace(go.Scatter(x = df_coef_long_2['Year'], y = df_coef_long_2['Rank'], 
                                 visible = 'legendonly', mode = 'lines', name = df_coef_long_2['Club'].unique()[0]))

#fig = px.line(df_coef_long, x = 'Year', y = 'Rank', color = 'Club')
fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 800, height = 400,
                  plot_bgcolor= 'white',
                  paper_bgcolor = 'whitesmoke')

chart_coef_dash = html.Div([

            html.H3('Club coefficients', style = {'text-align': 'left'}), 
            dcc.Graph(figure = fig)], 
            style = {'position': 'absolute', 'left': '600px','padding-top': '1em', 
                     'padding': '1em','width': '800px','padding-bottom': '1em',
                     'top': '200px'})

Highest_coef = df_coef_long.groupby('Club').min('Rank')['Rank'].reset_index()
Highest_coef_club = Highest_coef[Highest_coef['Rank'] == min(Highest_coef['Rank'])].reset_index()


card_coefficient = html.Div(id = 'Highest_coefficient', children = [dbc.Card( children = 
    [dbc.CardHeader("Highest (calculated) coefficient:", style = {'text-align': 'center'}),
     dbc.CardBody(
         html.H2(f"{Highest_coef_club.Club.values[0]}:\n Rank min(Highest_coef['Rank'])", className="card-title", 
                 style = {'font-size': '40px', 'text-align': 'center'})
         ),
    ],
    style={'position': 'absolute', "width": "250px", 'left': '0px', 
           'border-style': 'solid', 'border-color': 'black', 
           'box-shadow': '10px 10px',  'border-width': 'thin'},
)], style = {'position': 'absolute', "width": "250px", 'left': '1150px', 'height': '150px', 'top': '50px'})


#%%
a = df_totaal_players[['Player', 'Club', ]]
b = df_totaal_players_opponents[['Player', 'Club', 'Opponent']]

z = pd.merge(a, b, how = 'inner', on = ['Player', 'Club'])

z = z.drop_duplicates(subset = ['Player', 'Club', 'Opponent'])


Old_opponents = html.Div([

            html.H3(children = 'Old opponents'),
            dash_table.DataTable(
                id = 'old_opponents',
                data = z.to_dict('records'),
                columns = [{'name': i, 'id': i} for i in z.columns],
                style_cell_conditional = [
                    {'if': {'column_id': 'Player'}, 'width': '40%'},
                    {'if': {'column_id': 'Club'}, 'width': '30%'},
                    {'if': {'column_id': 'Opponent'}, 'width': '30%'}],
                page_action = 'none',
                fixed_rows={'headers': True},
                style_table = {'height': '300px', 'overflowY': 'auto'})], 
            style = {'height': '300px','width': '400px',
                     'position': 'absolute', 'left': '600px','padding': '1em',
                     'padding-top': '1em', 'z-index': '100'})

Most_old_opponent = z.groupby('Opponent').count().reset_index()
Most_old_opponent = Most_old_opponent[Most_old_opponent['Club'] == max(Most_old_opponent['Club'])]['Opponent'].values

clubs = ''
for i in range(len(Most_old_opponent)):
    if i == 0:
        clubs = clubs + Most_old_opponent[i]
        
    else:
        clubs = clubs + ', ' + Most_old_opponent[i]

card_most_old_opponent = html.Div(id = 'most_old_opponent', children = [dbc.Card( children = 
    [dbc.CardHeader("Club with most players from the same team:", style = {'text-align': 'center'}),
     dbc.CardBody(
         html.H2(f"{clubs}", className="card-title", 
                 style = {'font-size': '36px', 'text-align': 'center'})
         ),
    ],
    style={'position': 'absolute', "width": "350px", 'left': '0px', 
           'border-style': 'solid', 'border-color': 'black', 
           'box-shadow': '10px 10px',  'border-width': 'thin'},
)], style = {'position': 'absolute', "width": "350px", 'left': '1100px', 'height': '100px', 'top': '50px'})


#%%
df_totaal_players_opponents['Nationality'] = df_totaal_players_opponents['Nationality'].astype(str)
df_totaal_players_opponents['Nationality'] = df_totaal_players_opponents['Nationality'].str.replace('0', ' ')
df_totaal_players_opponents['ISO_nat'] = df_totaal_players_opponents['Nationality'].apply(lambda x: str(x).split(' ')[0])
df_totaal_players_opponents['ISO_nat'] = df_totaal_players_opponents['ISO_nat'].str.upper()
df_play_freq_nationalities = df_totaal_players_opponents.groupby('ISO_nat')['Player'].count().reset_index()

with open ('C:\\Users\\Dennis\\OneDrive\\Documenten\\Programming in Python\\Pet projects\\European opponents\\World_2.json') as file:
    json_file_world = json.load(file)
    file.close()
Nat_opponents = go.Figure(go.Choroplethmapbox(geojson = json_file_world,
                               z = df_play_freq_nationalities['Player'], featureidkey = 'properties.iso_a2',
                               locations = df_play_freq_nationalities['ISO_nat'], colorscale = 'Greens'))

Nat_opponents.update_traces(showscale=False)

Nat_opponents.update_layout(width = 900, height = 600, 
                      margin=dict(l=0, r=0, t=0, b=0), 
                      mapbox_center = {'lat': 35.4833314, 'lon': 20.7999968},
                      mapbox_style="carto-positron")

Nat_opponents_map_dash = html.Div([
    html.H3(children = 'Country play frequency', 
            style = { 'text-align': 'center'}), 
    dcc.Graph(id = 'opponents_nationalities_map_dash',figure = Nat_opponents, 
              style = {'height': '550px', })],
    style = {'position': 'absolute', 'left': '550px',
             'padding-left': '1em', 'width': '900px', 
             'top': '50px'})

#%%
app = dash.Dash()

tab_style = {
    #'borderBottom': '1px solid #000000',
    'padding': '6px',
    'backgroundColor': 'lightgray',
    'color': 'white',
    'fontWeight': 'bold',
    'font-size': '16px'
}

tab_selected_style = {
    'borderTop': '1px solid #000000',
    #'borderBottom': '1px solid #000000',
    'backgroundColor': 'lightgray',
    'fontWeight': 'bold',
    'font-size': '16px'
}

app.layout = html.Div([
    html.Div(id = 'parent', children = [
        html.H1(id = 'H1', 
                children = 'European matches dashboard Eredivisie', 
                style = {'textAlign':'center', 'vertical-align': 'middle',
                         'color': 'white', 'background-color': 'dimgray', 'height': '100px'}),
        dcc.Tabs(id = 'tabs_european_opponents_Netherlands', value = 'locations_map_dash', children=[
            dcc.Tab(label='Locations', value = 'locations_map_dash', children = [
                html.Div(clubs_map_dash),

                ], style = tab_style, selected_style = tab_selected_style),
            
            dcc.Tab(label='Opponent clubs', value = 'win/loss', children = [
                html.Div([
                    html.Div([
                        html.Div(Dropdown_distance),
                        html.Div(Distance_table),
                        html.Div(Opponent_most_matches_played_against),
                        html.Div(win_map_dash)
                        ], style = {'position': 'absolute', 'background-color': 'white', 'top': '150px',
                                    'height': '600px', 'z-index': '100', 'width': '1500px'}),
                    html.Div([
                        html.Div(opponent_club_most_goals_scored),
                        html.Div(Win_table_top),
                        html.Div(Win_table_bottom),
                        ], style = {'position': 'absolute', 'background-color': 'white', 'top': '850px',
                                    'height': '500px', 'z-index': '100', 'width': '1500px'})
                    ], style = {'position': 'absolute', 'background-color': 'whitesmoke', 
                                                'height': '1800px', 'width': '1500px'})
                ], style = tab_style, selected_style = tab_selected_style),
            
            dcc.Tab(label='Opponent players', value='Tab_distances', children = [
                html.Div([
                    html.Div(Dropdown_player_club),
                    html.Div([
                        html.Div(Most_Matches_played_against),
                        html.Div(Old_opponents),
                        html.Div(card_oldest_opponent),
                        html.Div(card_most_old_opponent)
                        ], style = {'position': 'absolute', 'background-color': 'white', 'top': '150px',
                                    'height': '600px', 'z-index': '100', 'width': '1500px'}),
                    html.Div([
                        html.Div(opponent_most_goals_scored),
                        html.Div(Nat_opponents_map_dash),
                        ], style = {'position': 'absolute', 'background-color': 'white', 'top': '850px',
                                    'height': '800px', 'z-index': '100', 'width': '1500px'})
                    ], style = {'position': 'absolute', 'background-color': 'whitesmoke', 
                                'height': '1800px', 'width': '1500px'})
                ], style = tab_style, selected_style = tab_selected_style),
                                
            dcc.Tab(label='Players Eredivisie', value = 'PSV_map_dash', children = [
                html.Div([
                    html.Div([
                        html.Div(Dropdown_player_club_2),
                        html.Div(Dropdown_player_nationality),
                        html.Div(Dropdown_player_competition),
                        html.Div(Dropdown_player_position)]),
                    html.Div([
                        html.Div(Player_most_matches_played_top_10),
                        html.Div(Matches_vs_goals),
                        html.Div(card)
                        ], style = {'position': 'absolute', 'background-color': 'white', 'top': '150px',
                                    'height': '600px', 'z-index': '100', 'width': '1500px'}),
                    html.Div([
                        html.Div(Oldest_players_top_10),
                        html.Div(card_2),
                        html.Div(card_coefficient),
                        html.Div(chart_coef_dash)
                        ], style = {'position': 'absolute', 'background-color': 'white', 'top': '850px',
                                    'height': '750px', 'z-index': '100', 'width': '1500px'})

                    ], style = {'position': 'absolute', 'background-color': 'whitesmoke', 
                                'height': '1800px', 'width': '1500px'})
                ], style = tab_style, selected_style = tab_selected_style)]
            )], style = {'background-color': 'lightgray'})
        ])


@app.callback([Output('graph_players_most_freq_played', 'figure'),
               Output('matches_vs_goals', 'figure'),
               Output('H3_matches_vs_goals', 'children'),
               Output('graph_players_oldest', 'figure'),
               Output('unique_players_in_europe', 'children'),
               Output('average_age', 'children'),
               Output('Highest_coefficient', 'children')],
              [Input('player_club_dropdown_2', 'value'),
               Input('player_nationality', 'value'),
               Input('player_competition', 'value'),
               Input('player_position', 'value')])
def func_club_players(club, nationality, competition, position):
    
    df_coef_long_filter = copy.deepcopy(df_coef_long)
    df_totaal_players_filter = copy.deepcopy(df_totaal_players)
    if club != 'Select all':
        df_totaal_players_filter = df_totaal_players[df_totaal_players['Club'] == club]
        df_coef_long_filter = df_coef_long_filter[df_coef_long_filter['Club'] == club]

    if nationality != 'Select all':
        df_totaal_players_filter = df_totaal_players_filter[df_totaal_players_filter['Nationality'] == nationality]
    
    if competition != 'Select all':
        df_totaal_players_filter = df_totaal_players_filter[df_totaal_players_filter['Comp'] == competition]

    if position != 'Select all':
        df_totaal_players_filter = df_totaal_players_filter[df_totaal_players_filter['Position'] == position]


    Player_most_matches_played = pd.DataFrame(
        df_totaal_players_filter.groupby(['Player'])['Nationality'].count().reset_index().\
            rename(columns = {'Nationality': 'Matches'}))
    
    Player_most_minutes_played = pd.DataFrame(
        df_totaal_players_filter.groupby(['Player'])['Minutes'].sum().reset_index().\
            rename(columns = {'Nationality': 'Matches'}))
        
    Player_most_matches_played_top_10 = Player_most_matches_played.\
        sort_values('Matches', ascending = False).head(10).sort_values('Matches', ascending = True)
        
    
    Player_oldest = pd.DataFrame(df_totaal_players_filter.groupby('Player')['Age'].max().\
        sort_values(ascending = False).head(10).sort_values(ascending = True).reset_index())

    fig_3 = px.bar(Player_oldest, x = 'Age', y = 'Player', orientation='h', color = discrete_colors, color_discrete_map="identity")
    fig_3.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 500, height = 450,
                      plot_bgcolor= 'white',
                      paper_bgcolor = 'white',        
                      hoverlabel = dict(
                                  bgcolor = 'lightgray',
                                  font_size = 14))
        
    fig_3.update_coloraxes(showscale=False)
    fig_3.update(layout_showlegend=False)
    
    if position == 'Goalkeeper' or position == 'Defender':
        Keeper_goals_conceded = pd.DataFrame(
            df_totaal_players_filter.groupby('Player')['Conceded'].sum().reset_index())
        df_player_merge = Player_most_minutes_played.merge(Keeper_goals_conceded, how = 'left')
        fig_2 = px.scatter(df_player_merge, x = 'Minutes', y = 'Conceded', hover_name= 'Player')
        H3_matches_vs_goals_output = 'Goals against per minute'
    
    else:
        Player_most_goals_scores = pd.DataFrame(
            df_totaal_players_filter.groupby(['Player'])['Goals'].sum().reset_index()) 
        df_player_merge = Player_most_minutes_played.merge(Player_most_goals_scores, how = 'left')
        fig_2 = px.scatter(df_player_merge, x = 'Minutes', y = 'Goals', hover_name= 'Player')
        H3_matches_vs_goals_output = 'Goals per minutes'



    card = html.Div(id = 'unique_players_in_europe', children = 
                    dbc.Card(
                        [dbc.CardHeader("Unique players in Europe", style = {'text-align': 'center'}),
                         dbc.CardBody(
                             html.H2(f"{len(df_totaal_players_filter['Player'].unique())}", 
                                     className="card-title",
                                     style = {'font-size': '40px', 'text-align': 'center'})
                             )
                         ], 
                        outline = True, color = 'primary',
                        style={'position': 'absolute', "width": "250px", 'height': '150px', 
                               'top': '50px', 'border-style': 'solid', 'border-color': 'black', 
                               'box-shadow': '10px 10px', 'border-width': 'thin'},
                        ), 
                    style={'position': 'absolute', "width": "250px"})


    Highest_coef = df_coef_long_filter.groupby('Club').min('Rank')['Rank'].reset_index()
    Highest_coef_club = Highest_coef[Highest_coef['Rank'] == min(Highest_coef['Rank'])].reset_index()


    card_coefficient = html.Div(id = 'Highest_coefficient', children = [dbc.Card(children = 
        [dbc.CardHeader("Highest (calculated) coefficient:", style = {'text-align': 'center'}),
         dbc.CardBody(
             [html.H1(f"{Highest_coef_club.Club.values[0]}: ", className="card-title", 
                     style = {'font-size': '40px', 'text-align': 'center'}),
             html.H2(f"Rank {min(Highest_coef['Rank'])}", className="card-title", 
                     style = {'font-size': '40px', 'text-align': 'center'})]
             ),
        ],
        style={'position': 'absolute', "width": "250px", 'left': '0px', 
               'border-style': 'solid', 'border-color': 'black', 
               'box-shadow': '10px 10px',  'border-width': 'thin'},
    )], style = {'position': 'absolute', "width": "250px", 'left': '0px', 'bottom': '50px', 'top': '0px'})


    
    avg_age_normalized = str(round(np.mean(df_totaal_players_filter['Age_normalized']), 3))
    decimal = (int(avg_age_normalized.split('.')[1]) / 1000) * 365
    avg_days = round(decimal)
    avg_year = avg_age_normalized.split('.')[0]
    

    card_2 = html.Div(id = 'average_age', children = [dbc.Card( children = 
        [dbc.CardHeader("Average age:", style = {'text-align': 'center'}),
         dbc.CardBody(
             html.H2(f"{avg_year} years and {avg_days} days", className="card-title", 
                     style = {'font-size': '40px', 'text-align': 'center'})
             ),
        ],
        style={'position': 'absolute', "width": "250px", 'left': '0px', 
               'border-style': 'solid', 'border-color': 'black', 
               'box-shadow': '10px 10px',  'border-width': 'thin'},
    )], style = {'position': 'absolute', "width": "250px", 'left': '0px', 'height': '150px'})
    
    
    

    
    
    
    

    fig_2.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 600, height = 400,
                      plot_bgcolor= 'white',
                      paper_bgcolor = 'white',        
                      hoverlabel = dict(
                                  bgcolor = 'lightgray',
                                  font_size = 14))
    fig_2.update_xaxes(zeroline = True, zerolinewidth = 2, zerolinecolor = 'black')
    fig_2.update_yaxes(zeroline = True, zerolinewidth = 2, zerolinecolor = 'black')

    fig = px.bar(Player_most_matches_played_top_10, x = 'Matches', y = 'Player', orientation = 'h', color = discrete_colors, color_discrete_map="identity")

    
    fig.update_coloraxes(showscale=False)
    fig.update(layout_showlegend=False)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 500, height = 500,
                      plot_bgcolor= 'white',
                      paper_bgcolor = 'white',        
                      hoverlabel = dict(
                                  bgcolor = 'lightgray',
                                  font_size = 14))

    
    return fig, fig_2, H3_matches_vs_goals_output, fig_3, card, card_2, card_coefficient
                                
                                
                                

@app.callback([Output('graph_players_most_freq_played_against', 'figure'), 
               Output('graph_players_most_scored_opponent', 'figure'),
               Output('Oldest_opponent', 'children')],
              [Input('player_club_dropdown', 'value')])
def func_update_graph_most_played(club):
    if club == 'Select all':
        x = df_totaal_players_opponents.groupby('Player').sum()['Minutes'].\
            sort_values(ascending = False).head(10).sort_values()
        
        opponent_player_most_goals= df_totaal_players_opponents.\
            groupby('Player').sum()['Goals'].sort_values(ascending = False).head(10).sort_values()
            
        opponent_player_oldest = df_totaal_players_opponents.\
            groupby('Player').max('Age')['Age'].sort_values(ascending = False).head(1).sort_values()
    
    else:
        df_totaal_players_opponents_filter = df_totaal_players_opponents[df_totaal_players_opponents['Club'] == club]

        x = df_totaal_players_opponents_filter.groupby('Player').sum()\
            ['Minutes'].sort_values(ascending = False).head(10).sort_values()
        
        opponent_player_most_goals= df_totaal_players_opponents_filter.\
            groupby('Player').sum()['Goals'].sort_values(ascending = False).head(10).sort_values()
            
        opponent_player_oldest = df_totaal_players_opponents_filter.\
            groupby('Player').max('Age')['Age'].sort_values(ascending = False).head(1).sort_values()

    opponent_player_oldest_year = str(opponent_player_oldest[0]).split('.')[0]
    opponent_player_oldest_day = str(opponent_player_oldest[0]).split('.')[1]


    card_oldest_opponent = html.Div(id = 'Oldest_opponent', children = dbc.Card(
        [dbc.CardHeader("Oldest opponent:", style = {'text-align': 'center'}),
         dbc.CardBody(
             [html.H2(f"{opponent_player_oldest.index[0]}", className="card-title", 
                     style = {'font-size': '40px', 'text-align': 'center'}),
             html.H2(f'{opponent_player_oldest_year} years and {opponent_player_oldest_day} days', className="card-title", 
                     style = {'font-size': '40px', 'text-align': 'center'})
             ]
             ),
        ], outline = True, color = 'primary',
        style={'position': 'absolute', "width": "400px",  'height': '200px', 
               'top': '50px', 'border-style': 'solid', 'border-color': 'black', 
               'box-shadow': '10px 10px', 'border-width': 'thin', 'left': '0px'},
    ), style = {'position': 'absolute', 'width': '450px'})





    df_x = pd.DataFrame(x.reset_index())
    fig = px.bar(df_x, x = 'Minutes', y = 'Player', text = 'Minutes', orientation = 'h', 
                 color = 'Minutes')
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 450, height = 400,
                      plot_bgcolor= 'white',
                      paper_bgcolor = 'white')
    
    
    fig.update_coloraxes(showscale=False)
    
    
    df_player_opponent_most_goals = pd.DataFrame(opponent_player_most_goals.reset_index())
    fig_opponent_most_goals = px.bar(df_player_opponent_most_goals, x = 'Goals', 
                                     y = 'Player', text = 'Goals', orientation = 'h', color = discrete_colors, color_discrete_map="identity")
    fig_opponent_most_goals.update_layout(margin=dict(l=0, r=0, t=20, b=0), width = 450, height = 400,
                      plot_bgcolor= 'white',
                      paper_bgcolor = 'white')
    
    fig_opponent_most_goals.update_coloraxes(showscale=False)
    fig_opponent_most_goals.update(layout_showlegend=False)
    
    return fig, fig_opponent_most_goals, card_oldest_opponent
    


@app.callback([Output('old_opponents', 'data'), Output('old_opponents', 'columns'), 
               Output('old_opponents', 'style_cell_conditional')],
              [Input('player_club_dropdown', 'value')])
def update_old_opponent_table(club):
    z_copy = copy.deepcopy(z)
    if club == 'Select all': 
        return z_copy.to_dict('records'), [{'name': i, 'id': i} for i in z_copy.columns],[
                {'if': {'column_id': 'Player'}, 'width': '40%'},
                {'if': {'column_id': 'Club'}, 'width': '40%'},
                {'if': {'column_id': 'Opponent'}, 'width': '30%'}]
    
    else:
        z_copy = z_copy[z_copy['Club'] == club]
        return z_copy.to_dict('records'), [{'name': i, 'id': i} for i in z_copy.columns],[
            {'if': {'column_id': 'Player'}, 'width': '40%'},
            {'if': {'column_id': 'Club'}, 'width': '30%'},
            {'if': {'column_id': 'Opponent'}, 'width': '30%'}]



@app.callback([Output('distance_table', 'data'), Output('distance_table', 'columns'), 
               Output('distance_table', 'style_cell_conditional')],
              [Input('distance_dropdown', 'value')])
def update_distance_table(club):
    if club == 'Select all': 
        return club_dict_tot.to_dict('records'), [{'name': i, 'id': i} for i in club_dict[club].columns],[
                {'if': {'column_id': 'Club'}, 'width': '40%'},
                {'if': {'column_id': 'Original_club'}, 'width': '40%'},
                {'if': {'column_id': 'Distance'}, 'width': '30%'}]
    
    else:
        return club_dict[club].to_dict('records'), [{'name': i, 'id': i} for i in club_dict[club].columns],[
            {'if': {'column_id': 'Club'}, 'width': '40%'},
            {'if': {'column_id': 'Original_club'}, 'width': '40%'},
            {'if': {'column_id': 'Distance'}, 'width': '30%'}]
    

if __name__ == '__main__':
    app.run_server()

    



