import sqlite3
import pandas as pd
import data_manipulation
import ast

def remaining_players(ID, innings, batting_list):
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT Team1Players, Team2Players FROM ipl_match_list WHERE ID = ?;", (ID,))
    toss_info = cursor.fetchone()
    
    x1, x2 = ast.literal_eval(toss_info[0]), ast.literal_eval(toss_info[1])

    y = batting_list[0]
    remaining_players_list = []
    if y in x1:
        remaining_players_list = [player for player in x1 if player not in batting_list]
    else:
        remaining_players_list = [player for player in x2 if player not in batting_list]
    return remaining_players_list

def fetch_batting_scorecard(ID, innings, batters_list):
    conn = sqlite3.connect('./ipl_database.db')

    # Fetch batting data
    batting_query = f'''
    SELECT batter, SUM(batsman_run) AS Runs_Scored, 
    COUNT(CASE WHEN extra_type IS NULL OR extra_type = 'byes' OR extra_type = 'legbyes' OR extra_type = 'noballs' THEN 1 ELSE NULL END) AS Balls_Faced, 
           SUM(CASE WHEN batsman_run = 4 THEN 1 ELSE 0 END) AS Four_Count,
           SUM(CASE WHEN batsman_run = 6 THEN 1 ELSE 0 END) AS Six_Count,
           SUM(CASE WHEN player_out != 'not out' THEN 1 ELSE 0 END) AS Out, 
           CASE WHEN MAX(isWicketDelivery) = 1 THEN MAX(kind) ELSE 'not out' END AS Dismissal_Type, 
           MAX(fielders_involved) AS fielders_involved, 
           MAX(CASE WHEN player_out != 'not out' THEN bowler ELSE NULL END) AS Bowler
    FROM ipl_ball_by_ball
    WHERE ID = ? AND innings = ?
    GROUP BY batter
    ORDER BY MIN(overs), MIN(ballnumber);  -- Order by batting position
    '''
    batting_data = pd.read_sql_query(batting_query, conn, params=(ID, innings))

    conn.close()

    # Reorder the rows based on the provided list of batters
    batting_data = batting_data.set_index('batter').loc[batters_list].reset_index()
    return batting_data

def fetch_bowling_scorecard(ID, innings):
    conn = sqlite3.connect('./ipl_database.db')

    # Fetch bowling data
    bowling_query = f'''
    SELECT bowler, overs, SUM(batsman_run) AS Runs_Conceding, 
           COUNT(CASE WHEN isWicketDelivery = 1 THEN 1 ELSE NULL END) AS Wickets,
           SUM(CASE WHEN non_boundary = 0 THEN 1 ELSE 0 END) AS Dots,
           SUM(CASE WHEN batsman_run = 4 THEN 1 ELSE 0 END) AS Four_Count,
           SUM(CASE WHEN batsman_run = 6 THEN 1 ELSE 0 END) AS Six_Count,
           SUM(CASE WHEN extra_type = 'wide' THEN 1 ELSE 0 END) AS Wide,
           SUM(CASE WHEN extra_type = 'noballs' THEN 1 ELSE 0 END) AS noballs_bowled
    FROM ipl_ball_by_ball
    WHERE ID = ? AND innings = ?
    GROUP BY bowler, overs;
    '''
    bowling_data = pd.read_sql_query(bowling_query, conn, params=(ID, innings))

    conn.close()

    return bowling_data

def scorecard(ID):
    batters_list_1 = data_manipulation.get_batting_positions_id_innings(ID, 1)
    batters_list_2 = data_manipulation.get_batting_positions_id_innings(ID, 2)
    remaining_players_1 = remaining_players(ID, 1, batters_list_1)
    remaining_players_2 = remaining_players(ID, 2, batters_list_2)
    return fetch_batting_scorecard(ID, 1, batters_list_1), fetch_batting_scorecard(ID, 2, batters_list_2), remaining_players_1, fetch_bowling_scorecard(ID, 1), fetch_bowling_scorecard(ID, 2), remaining_players_2


def match_details(ID):
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    det = "City, Season, MatchNumber, Team1, Team2, Venue, TossWinner, TossDecision, WinningTeam, WonBy, Margin, method, Player_of_Match, Umpire1, Umpire2,Date"
    cursor.execute("SELECT City, Season, MatchNumber, Team1, Team2, Venue, TossWinner, TossDecision, SuperOver, WinningTeam, WonBy, Margin, method, Player_of_Match, Umpire1, Umpire2,Date FROM ipl_match_list WHERE ID = ?;", (ID,))
    info = cursor.fetchone()
    lst = list(info)
    conn.close()
    
    return lst

def match_list():
    conn = sqlite3.connect('ipl_database.db')
    cursor = conn.cursor()
    query = '''
    SELECT *
    FROM ipl_match_list
    '''
    df_match_list = pd.read_sql_query(query, conn)
    # Execute the query with the player's name as a parameter

    conn.close()

    return df_match_list
    