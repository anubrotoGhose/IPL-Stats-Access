from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from io import StringIO
from io import BytesIO
import sqlite3
import pandas as pd
import search_results
import data_manipulation
import venue_stats
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

@app.route('/matchlists', methods=['GET', 'POST'])
def match_list_table():
    df_match_list = scorecard.match_list()
    df_match_list['ID'] = df_match_list['ID'].apply(lambda x: f'<a href="/scorecard/{x}">{x}</a>')
    table_html_ipl_match_list = df_match_list.to_html(classes='table', escape=False)
    
    return render_template('show_ipl_match_list.html', table_html_ipl_match_list=table_html_ipl_match_list)

@app.route('/scorecard/<int:id>', methods=['GET'])
def show_scorecard(id):
    # Your code to fetch the scorecard data based on the ID
    batting_1, batting_2,rp_1, bowling_1, bowling_2, rp_2 = scorecard.scorecard(id)
    batting_1 = batting_1.to_html(classes='table')
    batting_2 = batting_2.to_html(classes='table')
    bowling_1 = bowling_1.to_html(classes='table')
    bowling_2 = bowling_2.to_html(classes='table')
  
    rp_1="Batters remaining:"+str(rp_1)
    rp_2="Batters remaining:"+str(rp_2)
    match_det = scorecard.match_details(id)
    x = scorecard.match_function(match_det)
    # print(x)
    return render_template('show_scorecard.html',match_det=match_det, batting_1=batting_1, bowling_1 = bowling_1,rp_1=rp_1, batting_2=batting_2, bowling_2=bowling_2, rp_2=rp_2)

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
    df_fielder = pd.DataFrame()
    if column_name == 'Players':
        first_match_date, last_match_date = data_manipulation.get_first_and_last_match_dates(cell_value)
        df_batter = pd.DataFrame(data_manipulation.batter_stats(cell_value, first_match_date, last_match_date)) # Add Start and End Date
        df_bowler = pd.DataFrame(data_manipulation.bowler_stats(cell_value, first_match_date, last_match_date))
        df_fielder = data_manipulation.fielder_stats(cell_value, first_match_date, last_match_date)
        table_html_batter = df_batter.to_html(classes='table')
        table_html_bowler = df_bowler.to_html(classes='table')
        table_html_fielder = df_fielder.to_html(classes='table')
        return render_template('profile_page.html', 
                           column_name=column_name, 
                           cell_value=cell_value, 
                           table_html_batter=table_html_batter, 
                           table_html_bowler = table_html_bowler, 
                           table_html_fielder = table_html_fielder)

    elif column_name == 'Venues':
        first_match_date, last_match_date = venue_stats.get_first_and_last_match_dates(cell_value)
    else:
        df_batter = pd.DataFrame(data_manipulation.x_batter_stats(cell_value)) # Add Start and End Date
        df_bowler = pd.DataFrame(data_manipulation.x_bowler_stats(cell_value)) # Add Start and End Date
    table_html_batter = df_batter.to_html(classes='table')
    table_html_bowler = df_bowler.to_html(classes='table')
    table_html_fielder = df_fielder.to_html(classes='table')
    return render_template('profile_page_other.html', 
                           column_name=column_name, 
                           cell_value=cell_value, 
                           table_html_batter=table_html_batter, 
                           table_html_bowler = table_html_bowler)

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


@app.route('/top_partnerships')
def top_partnerships():
    return render_template('top_10_partnerships.html')

@app.route('/season_partnerships')
def season_partnerships():
    return render_template('season_partnerships.html')

@app.route('/top_batsmen')
def top_batsmen():
    return render_template('top_10_batsmen.html')

@app.route('/top_batsman_score')
def top_batsman_score():
    return render_template('top_batsman_score.html')

@app.route('/select_batsmen_across_seasons')
def select_batsmen_across_seasons():
    return render_template('select_batsmen_across_seasons.html')

@app.route('/player_of_the_match')
def player_of_match():
    return render_template('player_of_the_match.html')

@app.route('/hatricks')
def hatricks():
    return render_template('hatricks.html')

@app.route('/highest_four_hitters')
def highest_four_hitters():
    return render_template('highest_four_hitters.html')

@app.route('/highest_sixers')
def highest_sixers():
    return render_template('highest_sixers.html')

@app.route('/runs_scored')
def runs_scored():
    # Connect to the database
    conn = sqlite3.connect('./ipl_database.db')

    df = pd.read_sql_query("SELECT * FROM ipl_batter_list ORDER BY Runs DESC LIMIT 50", conn)

    conn.close()

    # Display the DataFrame
    df.index = range(1, len(df) + 1)
    table = df.to_html(classes='table')
    return render_template('top_players.html',
                           heading = "Top Batters By Runs Scored",
                           table=table)

@app.route('/top_batting_averages')
def top_batting_averages():
    # Connect to the database
    conn = sqlite3.connect('./ipl_database.db')

    df = pd.read_sql_query("SELECT * FROM ipl_batter_list WHERE Balls >= 60 ORDER BY Average DESC", conn)

    # Close the connection
    conn.close()
    df.index = range(1, len(df) + 1)
    table = df.to_html(classes='table')
    return render_template('top_players.html',
                           heading = "Top Batters By Batting Average",
                           table=table)

@app.route('/top_batting_strike_rates')
def top_batting_strike_rates():
    # Connect to the database
    conn = sqlite3.connect('./ipl_database.db')

    df = pd.read_sql_query("SELECT * FROM ipl_batter_list WHERE Balls >= 60 ORDER BY Strike_Rate DESC", conn)

    # Close the connection
    conn.close()
    df.index = range(1, len(df) + 1)
    # Display the DataFrame
    table = df.to_html(classes='table')
    return render_template('top_players.html',
                           heading = "Top Batters By Batting Strike Rates",
                           table=table)

@app.route('/wickets_taken')
def wickets_taken():
    # Connect to the database
    conn = sqlite3.connect('./ipl_database.db')

    df = pd.read_sql_query("SELECT * FROM ipl_bowler_list ORDER BY Wickets DESC LIMIT 50", conn)

    # Close the connection
    conn.close()

    # Display the DataFrame
    df.index = range(1, len(df) + 1)
    table = df.to_html(classes='table')
    return render_template('top_players.html',
                           heading = "Top Bowlers By Wickets Taken",
                           table=table)

@app.route('/top_bowling_averages')
def top_bowling_averages():
    # Connect to the database
    conn = sqlite3.connect('./ipl_database.db')

    df = pd.read_sql_query("SELECT * FROM ipl_bowler_list WHERE Wickets >= 60 ORDER BY Average ASC", conn)

    # Close the connection
    conn.close()

    # Display the DataFrame
    df.index = range(1, len(df) + 1)
    table = df.to_html(classes='table')
    return render_template('top_players.html',
                           heading = "Top Bowlers By Bowling Average",
                           table=table)

@app.route('/top_bowling_economy')
def top_bowling_economy():
    # Connect to the database
    conn = sqlite3.connect('./ipl_database.db')

    df = pd.read_sql_query("SELECT * FROM ipl_bowler_list WHERE Wickets >= 40 ORDER BY Economy ASC", conn)

    # Close the connection
    conn.close()

    # Display the DataFrame
    df.index = range(1, len(df) + 1)
    table = df.to_html(classes='table')
    return render_template('top_players.html',
                           heading = "Top Bowlers by Economy",
                           table=table)


@app.route('/process_stats_filter/<cell_value>/<column_name>', methods=['POST'])
def process_stats_filter(cell_value, column_name):
    
    
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    view_format = request.form.get('view_format')
    view_type = request.form.get('view_type')
    id_list, date_list, team1_list, team2_list, v = detailed_stats.get_match_ids_and_teams_for_player(cell_value, start_date, end_date)
    # print(id_list,"\n" , date_list,"\n", team1_list,"\n", team2_list,"\n", v)
    

    df_bat = None
    df_bowl = None
    df_field = None
    
    if view_format == None:
        view_format = "all"
    else:
        if view_format == "batting_formats":
            view_format = "batter"
        elif view_format == "bowling_formats":
            view_format = "bowler"
        elif view_format == "fielding_formats":
            view_format = "fielder"
        elif view_format == "all_round":
            view_format = "all"
            
    
    if view_type == "career_summary":
        if view_format == "all" or view_format == 'batter':
            df_bat = pd.DataFrame(data_manipulation.batter_stats(cell_value, start_date, end_date))
            df_bat = df_bat.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'bowler':
            df_bowl = pd.DataFrame(data_manipulation.bowler_stats(cell_value, start_date, end_date))
            df_bowl = df_bowl.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'fielder':
            df_field = data_manipulation.fielder_stats(cell_value, start_date, end_date)
            df_field = df_field.to_html(classes='table', escape=False)
    elif view_type == "innings_by_innings_list":
        if view_format == "all" or view_format == 'batter':
            df_bat = detailed_stats.innings_by_innings_list_batting(cell_value, id_list)
            df_bat = df_bat.dropna(subset=['batter'])
            df_bat.index = range(1, len(df_bat) + 1)
            df_bat["ID"] = df_bat['ID'].apply(lambda x: f'<a href="/scorecard/{x}">{x}</a>')
            df_bat = df_bat.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'bowler':
            df_bowl = detailed_stats.innings_by_innings_list_bowling(cell_value, id_list)
            df_bowl = df_bowl.dropna(subset=['Bowler'])
            df_bowl.index = range(1, len(df_bowl) + 1)
            df_bowl["ID"] = df_bowl['ID'].apply(lambda x: f'<a href="/scorecard/{x}">{x}</a>')
            df_bowl = df_bowl.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'fielder':
            df_field = detailed_stats.innings_by_innings_list_fieldings(cell_value, id_list)
            df_field = df_field.dropna(subset=['Fielder'])
            df_field.index = range(1, len(df_field) + 1)
            df_field["ID"] = df_field['ID'].apply(lambda x: f'<a href="/scorecard/{x}">{x}</a>')
            df_field = df_field.to_html(classes='table', escape=False)
    elif view_type == "cumulative_averages":
        if view_format == "all" or view_format == 'batter':
            df_bat = detailed_stats.innings_by_innings_list_batting(cell_value, id_list)
            df_bat = df_bat.dropna(subset=['batter'])
            df_bat.index = range(1, len(df_bat) + 1)
            df_bat["ID"] = df_bat['ID'].apply(lambda x: f'<a href="/scorecard/{x}">{x}</a>')
            df_bat = df_bat.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'bowler':
            df_bowl = detailed_stats.innings_by_innings_list_bowling(cell_value, id_list)
            df_bowl = df_bowl.dropna(subset=['Bowler'])
            df_bowl.index = range(1, len(df_bowl) + 1)
            df_bowl["ID"] = df_bowl['ID'].apply(lambda x: f'<a href="/scorecard/{x}">{x}</a>')
            df_bowl = df_bowl.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'fielder':
            df_field = detailed_stats.innings_by_innings_list_fieldings(cell_value, id_list)
            df_field = df_field.dropna(subset=['Fielder'])
            df_field.index = range(1, len(df_field) + 1)
            df_field["ID"] = df_field['ID'].apply(lambda x: f'<a href="/scorecard/{x}">{x}</a>')
            df_field = df_field.to_html(classes='table', escape=False)
    elif view_type == "reverse_cumulative":
        if view_format == "all" or view_format == 'batter':
            df_bat = detailed_stats.innings_by_innings_list_batting(cell_value, id_list)
            df_bat = df_bat.dropna(subset=['batter'])
            df_bat.index = range(1, len(df_bat) + 1)
            df_bat["ID"] = df_bat['ID'].apply(lambda x: f'<a href="/scorecard/{x}">{x}</a>')
            df_bat = df_bat.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'bowler':
            df_bowl = detailed_stats.innings_by_innings_list_bowling(cell_value, id_list)
            df_bowl = df_bowl.dropna(subset=['Bowler'])
            df_bowl.index = range(1, len(df_bowl) + 1)
            df_bowl["ID"] = df_bowl['ID'].apply(lambda x: f'<a href="/scorecard/{x}">{x}</a>')
            df_bowl = df_bowl.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'fielder':
            df_field = detailed_stats.innings_by_innings_list_fieldings(cell_value, id_list)
            df_field = df_field.dropna(subset=['Fielder'])
            df_field.index = range(1, len(df_field) + 1)
            df_field["ID"] = df_field['ID'].apply(lambda x: f'<a href="/scorecard/{x}">{x}</a>')
            df_field = df_field.to_html(classes='table', escape=False)
    elif view_type == "seasons":
        if view_format == "all" or view_format == 'batter':
            df_bat = detailed_stats.player_batting_stats_season_wise(cell_value, start_date, end_date)
            df_bat = df_bat.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'bowler':
            df_bowl = detailed_stats.player_bowling_stats_season_wise(cell_value, start_date, end_date)
            df_bowl = df_bowl.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'fielder':
            df_field = detailed_stats.player_stats_season_based_fielder(cell_value, start_date, end_date)
            df_field = df_field.to_html(classes='table', escape=False)
    elif view_type == "ground_averages":
        if view_format == "all" or view_format == 'batter':
            df_bat = detailed_stats.player_stats_venue_based_batting(cell_value, start_date, end_date)
            df_bat.index = range(1, len(df_bat) + 1)
            df_bat = df_bat.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'bowler':
            df_bowl = detailed_stats.player_stats_venue_based_bowler(cell_value, start_date, end_date)
            df_bowl.index = range(1, len(df_bowl) + 1)
            df_bowl = df_bowl.to_html(classes='table', escape=False)
        if view_format == "all" or view_format == 'fielder':
            df_field = detailed_stats.player_stats_venue_based_fielder(cell_value, start_date, end_date)
            df_field.index = range(1, len(df_field) + 1)
            df_field = df_field.to_html(classes='table', escape=False)


    return render_template('detailed_filtered_stats_page.html',
                           cell_value = cell_value,
                           column_name = column_name,
                           playing_team = team1_list,
                           opposition = team2_list,
                           start_date=start_date, 
                           end_date=end_date, 
                           view_format=view_format, 
                           view_type=view_type,
                           df_bat = df_bat,
                           df_bowl = df_bowl,
                           df_field = df_field)


@app.route('/download_csv', methods=['POST'])
def download_csv():
    html_data = request.form.get('csv_data')
    if html_data is not None:
        df = pd.read_html(BytesIO(html_data.encode()))[0]
        df.drop(columns=['Unnamed: 0'], inplace=True)
        buffer = BytesIO()
        df.to_csv(buffer, index=False, encoding='utf-8')
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, mimetype='text/csv', download_name='ipl_stats.csv')
    else:
        render_template('detailed_filtered_stats_page.html')


if __name__ == '__main__':
    app.run(debug=True)