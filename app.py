from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import search_results
import data_manipulation
import detailed_stats
import scorecard
import ast
app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_input = request.form['user_input']
        search_dict = search_results.filter_dict_by_search(user_input)

        # Store search_dict in session
        session['search_dict'] = search_dict

        return redirect(url_for('searchresults', user_input=user_input))
    return render_template('home.html')

@app.route('/scorecard', methods=['GET', 'POST'])
def scorecard_table():
    df_match_list = scorecard.match_list()
    table_html_ipl_match_list = df_match_list.to_html(classes='table')
    return render_template('scorecard_table.html', table_html_ipl_match_list=table_html_ipl_match_list)

@app.route('/searchresults/<user_input>')
def searchresults(user_input):
    # Retrieve the search_dict from the session
    search_dict = session.get('search_dict', {})

    # Get the keys (column names)
    dict_keys = search_dict.keys()

    return render_template('searchresults.html', user_input=user_input, dict_keys=dict_keys, search_dict=search_dict)

@app.route('/profile_page/<column_name>')
def profile_page(column_name):
    cell_value = request.args.get('value')
    df_batter = pd.DataFrame()
    df_bowler = pd.DataFrame()
    if column_name == 'Players':
        first_match_date, last_match_date = data_manipulation.get_first_and_last_match_dates(cell_value)
        df_batter = pd.DataFrame(data_manipulation.batter_stats(cell_value, first_match_date, last_match_date)) # Add Start and End Date
        df_bowler = pd.DataFrame(data_manipulation.bowler_stats(cell_value, first_match_date, last_match_date)) # Add Start and End Date
    else:
        df_batter = pd.DataFrame(data_manipulation.x_batter_stats(cell_value)) # Add Start and End Date
        df_bowler = pd.DataFrame(data_manipulation.x_bowler_stats(cell_value)) # Add Start and End Date

    # Convert the DataFrame to HTML
    table_html_batter = df_batter.to_html(classes='table')
    table_html_bowler = df_bowler.to_html(classes='table')
    return render_template('profile_page.html', column_name=column_name, cell_value=cell_value, table_html_batter=table_html_batter, table_html_bowler = table_html_bowler)

@app.route('/stats_filter/<cell_value>/<column_name>')
def stats_filter(cell_value, column_name):
    if column_name == 'Players':
        # Assuming data_manipulation.player_input_filter_stats returns a tuple containing the required data
        x = data_manipulation.player_input_filter_stats(cell_value)

        debut_date, last_match_date, match_ID_list, played_for_teams, played_against_teams = x[0], x[1], ast.literal_eval(x[2]), ast.literal_eval(x[3]), ast.literal_eval(x[4])
        
        venue_lst = data_manipulation.get_venues_for_matches(match_ID_list)
        seasons = data_manipulation.get_season(match_ID_list)
        
        # Pass the additional variables to the template
        return render_template('stats_filter.html', cell_value=cell_value, column_name=column_name, playing_teams=played_for_teams, opposition_teams=played_against_teams, venue_lst=venue_lst, debut_date=debut_date,last_match_date =last_match_date, seasons=seasons)
    
    return render_template('stats_filter.html', cell_value=cell_value, column_name=column_name)

@app.route('/process_stats_filter/<cell_value>/<column_name>', methods=['POST'])
def process_stats_filter(cell_value, column_name):
    
    playing_team = request.form.get('playing_team')
    opposition = request.form.get('opposition')
    ground = request.form.get('ground')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    season = request.form.get('season')
    match_result = request.form.getlist('match_result')
    view_format = request.form.get('view_format')
    view_type = request.form.get('view_type')
    id_list, date_list, team1_list, team2_list, v = detailed_stats.get_match_ids_and_teams_for_player(cell_value, start_date, end_date)
    print(id_list, date_list, team1_list, team2_list, v)
    playing_team_tuple = tuple(team1_list)
    opposition_tuple = tuple(playing_team)
    ground_tuple = tuple(ground)
    season_tuple = tuple(season)
    if playing_team == "all":
        playing_team_tuple = tuple(team1_list)
    else:
        playing_team_tuple = tuple(playing_team)

    if opposition == "all":
        opposition_tuple = tuple(team2_list)
    else:
        opposition_tuple = tuple(playing_team)


    if ground == "all":
        ground_tuple = tuple(v)
    else:
        ground_tuple = tuple(ground)
    
    if season == "all":
        pass
    else:
        season_tuple = tuple(season)

    if len(match_result)==0 or len(match_result)==3:
        pass
    else:
        match_result_tuple = tuple(match_result)
    
    if view_format == None:
        print("hi")
    else:
        if view_format == "batting_formats":
            view_format = "batter"
        elif view_format == "bowling_formats":
            view_format =="bowler"
        elif view_format == "fielding_formats":
            view_format =="bowler"

    
    if view_type == "career_summary":
        pass
    elif view_type == "innings_by_innings_list":
        pass
    elif view_type == "innings_by_innings_list":
        pass
    elif view_type == "innings_by_innings_list":
        pass
    elif view_type == "innings_by_innings_list":
        pass
    elif view_type == "innings_by_innings_list":
        pass

    # print("Playing Team:", playing_team, type(playing_team), len(playing_team))
    # print("Opposition:", opposition, type(opposition), len(opposition))
    # print("Ground:", ground, type(ground), len(ground))
    print("Start Date:", start_date, type(start_date), len(start_date))
    print("End Date:", end_date, type(end_date), len(end_date))
    # print("Season:", season, type(season), len(season))
    # print("Match Result:", match_result, type(match_result), len(match_result))
    # print("View Format:", view_format, type(view_format))
    # print("View Type:", view_type, type(view_type), len(view_type))



    return render_template('detailed_filtered_stats_page.html',
                           cell_value = cell_value,
                           column_name = column_name,
                           playing_team=playing_team, 
                           opposition=opposition, 
                           ground=ground, 
                           start_date=start_date, 
                           end_date=end_date, 
                           season=season, 
                           match_result=match_result, 
                           view_format=view_format, 
                           view_type=view_type)


if __name__ == '__main__':
    app.run(debug=True)