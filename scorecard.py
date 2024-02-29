import sqlite3
import pandas as pd
import data_manipulation
def fetch_batting_scorecard(ID, innings, batters_list):
    conn = sqlite3.connect('./ipl_database.db')

    # Fetch batting data
    batting_query = f'''
    SELECT batter, SUM(batsman_run) AS Runs_Scored, COUNT(*) AS Balls_Faced, 
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

def scorecard(ID):
    batters_list = data_manipulation.get_batting_positions_id_innings(ID, 1)


def match_list():
    conn = sqlite3.connect('ipl_database.db')
    cursor = conn.cursor()
    # print("In input filter_stats")
    # Define the SQL query to count the occurrences of the player's name in the Player_of_Match column
    query = '''
    SELECT *
    FROM ipl_match_list
    '''
    df_match_list = pd.read_sql_query(query, conn)
    # Execute the query with the player's name as a parameter

    conn.close()

    return df_match_list
    