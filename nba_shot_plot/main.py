import requests
import pandas as pd
import seaborn as sns
import plotly.graph_objs as go
import streamlit as st
from static.players import players
from static.teams import teams_dict
from PIL import Image



def side_bar():
	player_dict = (players["names"])
	player_list = []
	for p in player_dict:
		player_list.append(p['name'])

	year = st.sidebar.selectbox("Pick Year", options=["","2020-21","2019-20","2018-19","2017-18","2016-17","2015-16","2014-15","2013-14","2012-13","2011-12","2010-11","2009-10","2008-09","2007-08","2006-07", "2005-06", "2004-05", "2003-04", "2002-03", "2001-02", "2000-01", "1999-00"])
	# year_selected = st.sidebar.write('You selected:', year)
	options = st.sidebar.selectbox("Pick Player", options=player_list)
	# player = st.sidebar.write('You selected:', options)
	player_dict = (players["names"])
	player_id = 2544
	for p in player_dict:
		# st.sidebar.write('Player:', p['name'], player)
		if p['name'] == options:
			player_id = p['id']

	opponent = st.sidebar.selectbox("Pick Opponent", options=teams_dict)
	agree = st.sidebar.checkbox("Compare Seasons")
	if agree:
		st.checkbox("Great", value=True)
	if player_id and opponent:
		player_image = get_player_image(player_id)
		col1, col2 = st.beta_columns([3,1])
		col1.subheader(f'{options} - Shot Analysis vs {opponent}')
		col2.image(player_image, width=100)

		jsn = get_shot_data(player_id, year)
		df, data = clean_data(jsn, opponent=opponent)
		clean_df = df.copy()
		clean_df.drop(['GRID_TYPE', 'GAME_ID','GAME_EVENT_ID', 'PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'TEAM_NAME', 'PERIOD',
		              'MINUTES_REMAINING', 'SECONDS_REMAINING', 'LOC_X', 'LOC_Y', 'SHOT_MADE_FLAG',
		              'GAME_DATE', 'HTM', 'VTM'], axis=1, inplace=True)
		fig = build_court(data, options, year)
		# fig.show()
		st.plotly_chart(fig)
		player_year_stats(clean_df)
		st.sidebar.write('Player ID:', player_id)
	elif player_id and not opponent:
		player_image = get_player_image(player_id)
		col1, col2 = st.beta_columns([3, 1])
		col1.title(f'{options} - Shot Analysis')
		col2.image(player_image, width=100)
		get_player_image(player_id)
		jsn = get_shot_data(player_id, year)
		df, data = clean_data(jsn)
		clean_df = df.copy()
		clean_df.drop(
			['GRID_TYPE', 'GAME_ID', 'GAME_EVENT_ID', 'PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'TEAM_NAME', 'PERIOD',
			 'MINUTES_REMAINING', 'SECONDS_REMAINING', 'LOC_X', 'LOC_Y', 'SHOT_MADE_FLAG',
			 'GAME_DATE', 'HTM', 'VTM'], axis=1, inplace=True)
		fig = build_court(data, options, year)
		# fig.show()
		st.plotly_chart(fig)
		player_year_stats(clean_df)
		st.sidebar.write('Player ID:', player_id)
	else:
		st.sidebar.write("Didn't work")
		build_court_empty()

	run_button = st.sidebar.button(label='Get Stats')


def build_court(data, player, year):
	layout = go.Layout(
		title=f"{player} Shot chart {year}",
		showlegend=True,
		xaxis={'showgrid': False, 'range': [-300, 300]},
		yaxis={'showgrid': False, 'range': [-100, 500]},
		height=600,
		width=650,
	)
	color="white"
	width=1
	fig = go.Figure(data=data, layout=layout)
	fig.update_layout(
		shapes=[
			# Quadratic Bezier Curves
			dict(
				type="path",
				path="M -210 110 Q 0 380 210 110",
				line=dict(color=color, width=width),
			),
			# Restricted Area
			# dict(
			# 	type="path",
			# 	path="M -20 0 Q 0 30 20 0",
			# 	line=dict(color=color, width=width),
			# ),
		]
	)

	# Rim
	fig.add_shape(type="circle",
				xref="x", yref="y",
				x0=-6, y0=-6, x1=6, y1=6,
				line=dict(color=color, width=width),
				)
	# Backboard
	fig.add_shape(type="rect",
				x0=-15, y0=-7, x1=15, y1=-7,
				line=dict(color=color, width=width),
				)
	# outer box
	fig.add_shape(type="rect",
				x0=-80, y0=160, x1=80, y1=-47.5,
				line=dict(color=color, width=width),
				)
	# inner box
	fig.add_shape(type="rect",
				x0=-60, y0=160, x1=60, y1=-47.5,
				line=dict(color=color, width=width),
				)
	# left arc
	fig.add_shape(type="rect",
				x0=-210, y0=110, x1=-210, y1=-47.5,
				line=dict(color=color, width=width),
				)
	# right arc
	fig.add_shape(type="rect",
				x0=210, y0=110, x1=210, y1=-47.5,
				line=dict(color=color, width=width),
				)

	# midrange circle
	fig.add_shape(type="circle",
				xref="x", yref="y",
				x0=-60, y0=95, x1=60, y1=220,
				line=dict(color=color, width=width),
				)
	# center court circle outer
	fig.add_shape(type="circle",
	              xref="x", yref="y",
	              x0=-60, y0=400, x1=60, y1=530,
	              line=dict(color=color, width=width),
	              )
	# center court circle inner
	fig.add_shape(type="circle",
	              xref="x", yref="y",
	              x0=-30, y0=430, x1=30, y1=500,
	              line=dict(color=color, width=width),
	              )
	# court surroundings upper
	fig.add_shape(type="rect",
	              x0=-250, y0=-47.5, x1=250, y1=465,
	              line=dict(color=color, width=width),
	              )
	# court surroundings lower
	fig.add_shape(type="rect",
	              x0=-250, y0=465, x1=250, y1=987.5,
	              line=dict(color=color, width=width),
	              )
	# # halfcourt line
	# fig.add_shape(type="rect",
	#               x0=-250, y0=500, x1=250, y1=500,
	#               line=dict(color=color, width=width),
	#               )

	return fig

def build_court_empty():
	layout = go.Layout(
		title="No data for this player in this year",
		showlegend=True,
		xaxis={'showgrid': False, 'range': [-300, 300]},
		yaxis={'showgrid': False, 'range': [-100, 500]},
		height=600,
		width=650,
	)
	color="white"
	width=1
	fig = go.Figure(layout=layout)
	# Rim
	fig.add_shape(type="circle",
				xref="x", yref="y",
				x0=-6, y0=-6, x1=6, y1=6,
				line=dict(color=color, width=width),
				)
	# Backboard
	fig.add_shape(type="rect",
				x0=-15, y0=-7, x1=15, y1=-7,
				line=dict(color=color, width=width),
				)
	# outer box
	fig.add_shape(type="rect",
				x0=-80, y0=160, x1=80, y1=-47.5,
				line=dict(color=color, width=width),
				)
	# inner box
	fig.add_shape(type="rect",
				x0=-60, y0=160, x1=60, y1=-47.5,
				line=dict(color=color, width=width),
				)
	# left arc
	fig.add_shape(type="rect",
				x0=-210, y0=130, x1=-210, y1=-47.5,
				line=dict(color=color, width=width),
				)
	# right arc
	fig.add_shape(type="rect",
				x0=210, y0=130, x1=210, y1=-47.5,
				line=dict(color=color, width=width),
				)

	# midrange circle
	fig.add_shape(type="circle",
				xref="x", yref="y",
				x0=-60, y0=95, x1=60, y1=220,
				line=dict(color=color, width=width),
				)


	return fig

def player_year_stats(df):
	if df.empty:
		st.write("No data to display for this player in this season")
	else:
		st.write(df)
		col1, col2 = st.beta_columns(2)
		col3, col4 = st.beta_columns(2)
		# col3.write(df['SHOT_DISTANCE'].describe())
		col1.write(df['SHOT_ZONE_AREA'].value_counts(normalize=True)*100)
		col2.write(df['SHOT_ZONE_RANGE'].value_counts(normalize=True)*100)
		col3.write(df['SHOT_TYPE'].value_counts(normalize=True)*100)
		col4.write(df['SHOT_ZONE_BASIC'].value_counts(normalize=True)*100)
		# median shot distance
		st.write("Median Shot Distance:", df['SHOT_DISTANCE'].median())
		# Year shooting %
		st.write("Shooting Percentage: {:.2%}".format(
			df['EVENT_TYPE'].value_counts()[1] / (df['EVENT_TYPE'].value_counts()[0] + df['EVENT_TYPE'].value_counts()[1])))
		# 2pt shooting %
		twos = df[df['SHOT_TYPE'] == '2PT Field Goal']
		st.write("2pt Shot Percentage: {:.2%}".format(twos['EVENT_TYPE'].value_counts()[1] / (
					twos['EVENT_TYPE'].value_counts()[0] + twos['EVENT_TYPE'].value_counts()[1])))
		# 3pt shooting %
		threes = df[df['SHOT_TYPE'] == '3PT Field Goal']
		if len(threes['EVENT_TYPE'].value_counts()) > 1:
			st.write("3pt Shot Percentage: {:.2%}".format(threes['EVENT_TYPE'].value_counts()[1] / (
					threes['EVENT_TYPE'].value_counts()[0] + threes['EVENT_TYPE'].value_counts()[1])))
		# Total shots taken
		total_shots = df['SHOT_ATTEMPTED_FLAG'].count()
		st.write("Total shots Taken:", total_shots)
		# Total 2pt shots take
		total_twos = twos['SHOT_ATTEMPTED_FLAG'].count()
		st.write("Total 2pt Taken:", total_twos)
		# Total 3pt shots take
		total_threes = threes['SHOT_ATTEMPTED_FLAG'].count()
		st.write("Total 3pt Taken:", total_threes)
		# Shot zone area breakdown

def clean_data(jsn, opponent=None):
	data = jsn['resultSets'][0]['rowSet']
	columns = jsn['resultSets'][0]['headers']

	df = pd.DataFrame.from_records(data, columns=columns)
	temp_df = df.copy()
	if opponent:
		temp_df = df[df['VTM'] == teams_dict[opponent]]
		temp_df = temp_df.append(df[df['HTM'] == teams_dict[opponent]])

	missed_shot_trace = go.Scatter(
		x=-1*(temp_df[temp_df['EVENT_TYPE'] == 'Missed Shot']['LOC_X']),
		y=temp_df[temp_df['EVENT_TYPE'] == 'Missed Shot']['LOC_Y'],
		mode='markers',
		name='Miss',
		marker={'color': 'red', 'size': 5},
	)

	made_shot_trace = go.Scatter(
		x=-1*(temp_df[temp_df['EVENT_TYPE'] == 'Made Shot']['LOC_X']),
		y=temp_df[temp_df['EVENT_TYPE'] == 'Made Shot']['LOC_Y'],
		mode='markers',
		name='Make',
		marker={'color': 'blue', 'size': 5}
	)

	data = [missed_shot_trace, made_shot_trace]
	return temp_df, data

def get_shot_data(player_id, year):
	headers = {'Host': 'stats.nba.com',
				'Connection': 'keep-alive',
				'Pragma': 'no-cache',
				'Cache-Control': 'no-cache',
				'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
				'Accept': 'application/json, text/plain, */*',
				'x-nba-stats-token': 'true',
				'sec-ch-ua-mobile': '?0',
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
				'x-nba-stats-origin': 'stats',
				'Origin': 'https://www.nba.com',
				'Sec-Fetch-Site': 'same-site',
				'Sec-Fetch-Mode': 'cors',
				'Sec-Fetch-Dest': 'empty',
				'Referer': 'https://www.nba.com/',
				'Accept-Encoding': 'gzip, deflate, br',
				'Accept-Language': 'en-US,en;q=0.9,he;q=0.8'}
	shot_data_url_start = f'http://stats.nba.com/stats/shotchartdetail?AheadBehind=&CFID=33&CFPARAMS={year}&ClutchTime=&Conference=&ContextFilter=&ContextMeasure=FGA&DateFrom=&DateTo=&Division=&EndPeriod=10&EndRange=28800&GROUP_ID=&GameEventID=&GameID=&GameSegment=&GroupID=&GroupMode=&GroupQuantity=5&LastNGames=0&LeagueID=00&Location=&Month=0&OnOff=&OpponentTeamID=0&Outcome=&PORound=0&Period=0&PlayerID='
	shot_data_url_end = f'&PlayerID1=&PlayerID2=&PlayerID3=&PlayerID4=&PlayerID5=&PlayerPosition=&PointDiff=&Position=&RangeType=0&RookieYear=&Season={year}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StartPeriod=1&StartRange=0&StarterBench=&TeamID=0&VsConference=&VsDivision=&VsPlayerID1=&VsPlayerID2=&VsPlayerID3=&VsPlayerID4=&VsPlayerID5=&VsTeamID='
	full_url = shot_data_url_start + str(player_id) + shot_data_url_end
	jsn = requests.get(full_url, headers=headers).json()
	return jsn

def get_player_image(player_id):
	url = f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png"
	return url


def get_players_list():
	url = "https://7enmqppfr7.execute-api.us-east-1.amazonaws.com/dev/players"
	resp = requests.get(url)
	player_list = resp.json()
	return player_list


# Filter Options
def filter_opponent(df, opponent, year, player):
	# Done
	pass

def filter_range(df):
	pass

def filter_area(df):
	pass

def main():
	side_bar()


if __name__ == '__main__':
	# st.set_page_config(layout="wide")
	main()
