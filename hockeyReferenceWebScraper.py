import requests
from bs4 import BeautifulSoup
import pandas as pd
import unidecode

pd.options.display.max_columns = 20
pd.options.display.max_rows = 1000
pd.options.display.width = 2000

team_career = False
player_career = True
team_season = False

team = 'tbl'
player_name = 'curtis mcelhinney'
year = '2021'
month = '05'
day = '7'


# get team data
def team_data(team_p, year_p):
    global a, team_gp, team_w, team_l, td, main_soup
    url = 'https://www.hockey-reference.com/teams/' + team_p.upper() + '/' + year_p + '.html'
    response = requests.get(url)
    main_soup = BeautifulSoup(response.text, 'html.parser')
    info = main_soup.find(id='info').findAll('a')
    for a in info:
        if a.text == "Schedule and Results":
            url = 'https://www.hockey-reference.com/' + a['href']
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find(id='all_games')
    rows = table.findAll('td')
    team_gp = 0
    team_w = 0
    team_l = 0
    for td in rows:
        if td.text == 'W':
            team_w += 1
        if td.text == 'L':
            team_l += 1
        if td.text == 'W' or td.text == 'L':
            team_gp += 1


def player_urls(name):
    global a, url_list, year_list, team_list
    url = 'https://www.hockey-reference.com/players/'
    response = requests.get(url)
    player_soup = BeautifulSoup(response.text, 'html.parser')
    index = player_soup.find(id='all_index').findAll('a')
    for a in index:
        if a.text == name.split()[1][0].upper():
            url = 'https://www.hockey-reference.com' + a['href']
    response = requests.get(url)
    player_soup = BeautifulSoup(response.text, 'html.parser')
    index = player_soup.find(id='all_players').findAll('a')
    for a in index:
        if unidecode.unidecode(a.text.lower()) == name:
            url = 'https://www.hockey-reference.com' + a['href']
            # url = 'https://www.hockey-reference.com' + '/players/a/ahose01.html'
            player_url = url
    response = requests.get(url)
    player_soup = BeautifulSoup(response.text, 'html.parser')
    team_list = []
    url_list = []
    year_list = []
    index = player_soup.find(id='all_stats_basic_plus_nhl').find('tbody').findAll('th')
    for th in index:
        if th.get('data-stat') == 'season' and th.get('scope') == 'row':
            current_year = th.text[0:2] + th.text.split('-')[1]
            if current_year == '1900':
                current_year = '2000'
            year_list.append(current_year)
            url = player_url.replace('.html', '') + '/gamelog/' + current_year
            url_list.append(url)
    index = player_soup.find(id='all_stats_basic_plus_nhl').find('tbody').findAll('td')
    for td in index:
        if td.get('data-stat') == 'team_id':
            for a in td:
                team_list.append(a.text)

    to_remove = []
    j = 0
    while j < len(team_list):
        if team_list[j] == 'TOT':
            to_remove.append(j)
        j += 1
    for x in reversed(to_remove):
        del team_list[x]
        del url_list[x]
        del year_list[x]

    to_remove = []
    for x in year_list:
        if int(x) > int(year):
            to_remove.append(year_list.index(x))
    for x in reversed(to_remove):
        del team_list[x]
        del url_list[x]
        del year_list[x]


def full_roster_urls():
    global url_list, name_list, td
    roster_data = main_soup.find(id='skaters').findAll('td')
    url_list = []
    name_list = []
    for td in roster_data:
        if td.get('data-stat') == "player":
            player_id = td.get('data-append-csv')
            name = td.get('csk')
            first_name = name.split(',')[1]
            last_name = name.split(',')[0]
            name2 = first_name + ' ' + last_name
            if player_id is not None:
                url = 'https://www.hockey-reference.com/players/' + name[0] \
                      + '/' + player_id + '/gamelog/' + year
                url_list.append(url)
                name_list.append(name2.lower())


# def results_urls():
#     global url_list, team1, team2
#     url = 'https://www.hockey-reference.com/boxscores/?year='+year+'&month='+month+'&day='+day
#     response = requests.get(url)
#     results_soup = BeautifulSoup(response.text, 'html.parser')
#     url_list = []
#     index = results_soup.find(class_='game_summaries').findAll('a')
#     for a in index:
#         if a.text == 'Final':
#             url = 'https://www.hockey-reference.com' + a['href']
#             url_list.append(url)
#
#
# def results_roster_urls():
#     for url in url_list:
#         response = requests.get(url)
#         results_soup = BeautifulSoup(response.text, 'html.parser')
#         roster1 = []
#         roster2 = []
#         index = results_soup.find(id='all_CGY_skaters').findAll('a')


# get player data
def player_data():
    global player_gp_list, player_w_list, player_l_list, player_gp_out_list, player_w_out_list, \
        player_l_out_list, score_list, ss_list, weighted_score_list, td, a
    player_gp_list = []
    player_w_list = []
    player_l_list = []
    player_gp_out_list = []
    player_w_out_list = []
    player_l_out_list = []
    score_list = []
    ss_list = []
    weighted_score_list = []
    i = 0
    while i < len(url_list):
        if career_data:
            team_p = team_list[i]
            year_p = year_list[i]
            team_data(team_p, year_p)
        response = requests.get(url_list[i])
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find(id='all_gamelog')
        all_tds = table.findAll('td')
        filtered_trs = []
        for td in all_tds:
            if td.get('data-stat') == "team_id":
                for a in td:
                    if career_data:
                        if a.text == team_p.upper():
                            filtered_trs.append(a.find_parent('tr'))
                    else:
                        if a.text == team.upper():
                            filtered_trs.append(a.find_parent('tr'))

        player_gp = 0
        player_w = 0
        player_l = 0
        for tr in filtered_trs:
            for td in tr:
                if td.get('data-stat') == "game_result":
                    if td.text == "W" or td.text == "L" or td.text == "L-OT" or td.text == "L-SO":
                        player_gp += 1
                    if td.text == "W":
                        player_w += 1
                    if td.text == "L" or td.text == "L-OT" or td.text == "L-SO":
                        player_l += 1

        player_w_out = team_w - player_w
        player_l_out = team_l - player_l
        player_gp_out = player_w_out + player_l_out
        if player_gp_out == 0 or player_gp == 0:
            player_score = 0
        else:
            player_score = round((player_w / player_gp - player_w_out / player_gp_out) * 82)
        player_ss = min(player_gp, player_gp_out)
        player_combined = round(player_ss * player_score / 41, 1)

        player_gp_list.append(player_gp)
        player_w_list.append(player_w)
        player_l_list.append(player_l)
        player_gp_out_list.append(player_gp_out)
        player_w_out_list.append(player_w_out)
        player_l_out_list.append(player_l_out)
        score_list.append(player_score)
        ss_list.append(player_ss)
        weighted_score_list.append(player_combined)
        i += 1


# set up dataframe
def dataframe_team_full():
    dl = sorted(list(zip(name_list, player_gp_list, player_w_list, player_l_list,
                         player_gp_out_list, player_w_out_list, player_l_out_list,
                         ss_list, score_list, weighted_score_list)),
                key=lambda x: x[9], reverse=True)
    df = pd.DataFrame(dl, columns=['Name', 'GPi', 'Wi', 'Li', 'GPo', 'Wo', 'Lo', 'Sample Size', 'Score',
                                   'Weighted'])
    df.loc['Total'] = df.sum(numeric_only=True)
    print(df)


def dataframe_team_short():
    dl = sorted(list(zip(name_list, weighted_score_list)),
                       key=lambda x: x[1], reverse=True)
    df = pd.DataFrame(dl, columns=['Name', 'Weighted'])
    print(df)


def dataframe_player_full():
    data_list = sorted(list(zip(year_list, team_list, player_gp_list, player_w_list, player_l_list,
                                player_gp_out_list, player_w_out_list, player_l_out_list,
                                ss_list, score_list, weighted_score_list)),
                       key=lambda x: x[0], reverse=True)
    df = pd.DataFrame(data_list,
                      columns=['Year', 'Team', 'GPi', 'Wi', 'Li', 'GPo', 'Wo', 'Lo', 'Sample Size', 'Score',
                               'Weighted'])
    total_gpi = df['GPi'].sum()
    total_gpo = df['GPo'].sum()
    career_score = round(df['Weighted'].sum(), 1)
    score_per_season = round(career_score / (total_gpi + total_gpo) * 82, 1)
    df.loc['Total'] = df.sum(numeric_only=True)
    print(player_name.upper())
    print(df)
    print('Score per season: ' + str(score_per_season))
    print('Career score: ' + str(career_score))


def dataframe_player_short(name):
    data_list = sorted(list(zip(year_list, team_list, player_gp_list, player_w_list, player_l_list,
                                player_gp_out_list, player_w_out_list, player_l_out_list,
                                ss_list, score_list, weighted_score_list)),
                       key=lambda x: x[0], reverse=True)
    df = pd.DataFrame(data_list,
                      columns=['Year', 'Team', 'GPi', 'Wi', 'Li', 'GPo', 'Wo', 'Lo', 'Sample Size', 'Score',
                               'Weighted'])
    total_gpi = df['GPi'].sum()
    total_gpo = df['GPo'].sum()
    career_score = round(df['Weighted'].sum(), 1)
    score_per_season = round(career_score / (total_gpi + total_gpo) * 82, 1)
    print(name + ' ' + str(score_per_season) + ' ' + str(career_score))


def team_career_analytics():
    global career_data
    career_data = True
    team_data(team, year)
    full_roster_urls()
    print(name_list)
    for i in name_list:
        player_urls(i)
        player_data()
        dataframe_player_short(i)


def player_career_analytics():
    global career_data
    career_data = True
    player_urls(player_name)
    player_data()
    dataframe_player_full()


def team_season_analytics():
    global career_data
    career_data = False
    team_data(team, year)
    full_roster_urls()
    player_data()
    dataframe_team_short()


if team_career:
    team_career_analytics()
elif player_career:
    player_career_analytics()
elif team_season:
    team_season_analytics()

# results_urls()
