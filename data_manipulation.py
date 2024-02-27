import pandas as pd
import sqlite3
import numpy as np

def batter_innings(player_name):

    # Connect to the SQLite database
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    # SQL query to count the unique number of times the player is batter or non-striker for every ID
    query = '''
    SELECT ipl_ball_by_ball.ID, COUNT(DISTINCT CASE WHEN batter = ? THEN innings ELSE NULL END) AS BatterAppearances,
        COUNT(DISTINCT CASE WHEN "non-striker" = ? THEN innings ELSE NULL END) AS NonStrikerAppearances
    FROM ipl_ball_by_ball
    JOIN ipl_match_list ON ipl_ball_by_ball.ID = ipl_match_list.ID
    WHERE batter = ? OR "non-striker" = ?
    GROUP BY ipl_ball_by_ball.ID
    '''

    # Execute the query
    cursor.execute(query, (player_name, player_name, player_name, player_name))

    # Fetch the result
    results = cursor.fetchall()
    c = 0
    for match_id, batter_appearances, non_striker_appearances in results:
        # print(f"Match ID: {match_id}, Batter Appearances: {batter_appearances}, Non-Striker Appearances: {non_striker_appearances}")
        c+=1

    # print(c)
    conn.close()
    return c
    # Close the connection
    
def bowler_innings(player_name):
    # Connect to the SQLite database
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    # SQL query to count the unique number of times the player is a bowler for every ID
    query = '''
    SELECT ipl_ball_by_ball.ID, 
           COUNT(DISTINCT CASE WHEN bowler = ? THEN innings ELSE NULL END) AS BowlerInnings
    FROM ipl_ball_by_ball
    JOIN ipl_match_list ON ipl_ball_by_ball.ID = ipl_match_list.ID
    WHERE bowler = ?
    GROUP BY ipl_ball_by_ball.ID
    '''

    # Execute the query
    cursor.execute(query, (player_name, player_name))

    # Fetch the result
    results = cursor.fetchall()
    total_innings = len(results)
    
    conn.close()
    return total_innings

def num_matches(player_name):

    # Connect to the SQLite database
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    # SQL query to count the number of times the player is in Team1Players or Team2Players for each ID
    query = '''
    SELECT ipl_match_list.ID, 
        (CASE 
            WHEN ipl_match_list.Team1Players LIKE '%' || ? || '%' THEN 1
            ELSE 0
        END) AS InTeam1Players,
        (CASE 
            WHEN ipl_match_list.Team2Players LIKE '%' || ? || '%' THEN 1
            ELSE 0
        END) AS InTeam2Players
    FROM ipl_match_list
    WHERE ipl_match_list.Team1Players LIKE '%' || ? || '%' 
    OR ipl_match_list.Team2Players LIKE '%' || ? || '%'
    '''

    # Execute the query
    cursor.execute(query, (player_name, player_name, player_name, player_name))

    # Fetch the result
    results = cursor.fetchall()
    f = 0
    for match_id, in_team1players, in_team2players in results:
        # print(f"Match ID: {match_id}, In Team1Players: {in_team1players}, In Team2Players: {in_team2players}")
        f+=1
    # print("match",f)
    # Close the connection
    conn.close()
    return f    

def bowls_played(player_name):

    # Connect to the SQLite database
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    # Replace 'player_name' with the actual name of the player you're querying

    # SQL query to count the total number of times the player is in the batter column
    query = '''
    SELECT COUNT(*) AS TotalBatterAppearances
    FROM ipl_ball_by_ball
    WHERE batter = ?
    '''

    # Execute the query
    cursor.execute(query, (player_name,))

    # Fetch the result
    result = cursor.fetchone()
    total_batter_appearances = result[0]
    
    # Close the connection
    conn.close()

    return total_batter_appearances

def total_bowls(player_name):
    # Connect to the SQLite database
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    # SQL query to count the total number of times the player is in the bowler column
    query = '''
    SELECT COUNT(*) AS TotalBowlsPlayed
    FROM ipl_ball_by_ball
    WHERE bowler = ?
    '''

    # Execute the query
    cursor.execute(query, (player_name,))

    # Fetch the result
    result = cursor.fetchone()
    total_bowls_played = result[0]
    
    # Close the connection
    conn.close()
    return total_bowls_played


def batter_stats(player):
    conn = sqlite3.connect('./ipl_database.db')
    # Query the database
    df_ball = pd.read_sql_query('SELECT * FROM ipl_ball_by_ball;', conn)

    player_runs = df_ball[df_ball['batter'] == player]['batsman_run'].sum()
    number_times_out_query = 'SELECT COUNT(*) FROM ipl_ball_by_ball WHERE player_out = ?;'
    cursor = conn.cursor()
    cursor.execute(number_times_out_query, (player,))
    count = cursor.fetchone()[0]
    batting_avg = 0
    if count == 0:
        batting_avg = np.nan
    else:
        batting_avg = player_runs/count
        batting_avg = round(batting_avg, 2)
    
    batter_dict = {}
    batter_dict['Matches'] = [num_matches(player)]
    batter_dict['Innings'] = [batter_innings(player)]
    batter_dict['Runs'] = [player_runs]
    batter_dict['Balls'] = [bowls_played(player)]
    batter_dict['Average'] = [batting_avg]
    batter_dict['Not Outs'] = [batter_innings(player) - count]
    
    # Close the connection
    conn.close()

    return batter_dict

def bowler_runs(player_name):
    import sqlite3

    # Connect to the SQLite database
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    # Replace 'player_name' with the actual name of the bowler you're querying

    # SQL query to count the total number of runs given by the player as a bowler excluding legbyes and byes
    query = '''
    SELECT SUM(total_run) AS TotalRunsGiven
    FROM ipl_ball_by_ball
    WHERE bowler = ?
    '''

    # Execute the query
    cursor.execute(query, (player_name,))

    # Fetch the result
    result = cursor.fetchone()
    total_runs_given = result[0] if result[0] is not None else 0
    

    # Close the connection
    conn.close()
    return total_runs_given

def bowler_wickets(player_name):
    import sqlite3

    # Connect to the SQLite database
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    # Replace 'player_name' with the actual name of the bowler you're querying

    # SQL query to count the number of wickets taken by the bowler excluding run outs
    query = '''
    SELECT COUNT(*) AS WicketsTaken
    FROM ipl_ball_by_ball
    WHERE bowler = ? AND isWicketDelivery = 1 AND kind != 'run out'
    '''

    # Execute the query
    cursor.execute(query, (player_name,))

    # Fetch the result
    result = cursor.fetchone()
    wickets_taken = result[0]

    # print(f"Bowler: {player_name}")
    # print(f"Total Wickets Taken (excluding run outs): {wickets_taken}")
    
    # Close the connection
    conn.close()
    return wickets_taken


def bowler_stats(player):
    conn = sqlite3.connect('./ipl_database.db')
    # Query the database

    player_runs = bowler_runs(player)
    
    count = bowler_wickets(player)
    bowling_avg = 0
    if count == 0:
        bowling_avg = np.nan
    else:
        bowling_avg = player_runs/count
        bowling_avg = round(bowling_avg, 2)
    
    bowler_dict = {}
    bowler_dict['Matches'] = [num_matches(player)]
    bowler_dict['Innings'] = [bowler_innings(player)]
    bowler_dict['Runs'] = [player_runs]
    bowler_dict['Wickets'] = [count]
    bowler_dict['Balls'] = [total_bowls(player)]
    bowler_dict['Average'] = [bowling_avg]
    
    # Close the connection
    conn.close()

    return bowler_dict


def x_batter_stats(x):
    batter_dict = {}
    batter_dict = {}
    batter_dict['Matches'] = [0]
    batter_dict['Innings'] = [0]
    batter_dict['Runs'] = [0]
    batter_dict['Bowls'] = [0]
    batter_dict['Average'] = [0]
    return batter_dict

def x_bowler_stats(x):


    bowler_dict = {}
    bowler_dict['Matches'] = [0]
    bowler_dict['Innings'] = [0]
    bowler_dict['Runs'] = [0]
    bowler_dict['Wickets'] = [0]
    bowler_dict['Bowls'] = [0]
    bowler_dict['Average'] = [0]
    return bowler_dict