import sqlite3
import numpy as np
import pandas as pd


def get_season(match_ID_list):
    conn = sqlite3.connect('ipl_database.db')
    cursor = conn.cursor()

    # Convert the list of IDs to a tuple for the SQL query
    match_ID_tuple = tuple(match_ID_list)

    # Query to select venues for the given match IDs
    query = f'''
    SELECT Season
    FROM ipl_match_list
    WHERE ID IN {match_ID_tuple}
    '''

    # Execute the query
    cursor.execute(query)
    seasons = [row[0] for row in cursor.fetchall()]

    conn.close()

    return sorted(list(set(seasons)))

def get_venues_for_matches(match_ID_list):
    conn = sqlite3.connect('ipl_database.db')
    cursor = conn.cursor()

    # Convert the list of IDs to a tuple for the SQL query
    match_ID_tuple = tuple(match_ID_list)

    # Query to select venues for the given match IDs
    query = f'''
    SELECT Venue
    FROM ipl_match_list
    WHERE ID IN {match_ID_tuple}
    '''

    # Execute the query
    cursor.execute(query)
    venues = [row[0] for row in cursor.fetchall()]

    conn.close()

    return sorted(list(set(venues)))


def player_input_filter_stats(player_name):
    conn = sqlite3.connect('ipl_database.db')
    cursor = conn.cursor()
    # print("In input filter_stats")
    # Define the SQL query to count the occurrences of the player's name in the Player_of_Match column
    query = '''
    SELECT debut_date, last_match_date,  match_ID_list, played_for_teams, played_against_teams
    FROM ipl_player_list
    WHERE name LIKE ?
    '''

    # Execute the query with the player's name as a parameter
    cursor.execute(query, ('%' + player_name + '%',))
    lst = [item for item in cursor.fetchone()]

    conn.close()

    return lst

def count_player_of_match(player_name):
    conn = sqlite3.connect('ipl_database.db')
    cursor = conn.cursor()

    # Define the SQL query to count the occurrences of the player's name in the Player_of_Match column
    query = '''
    SELECT COUNT(*)
    FROM ipl_match_list
    WHERE Player_of_Match LIKE ?
    '''

    # Execute the query with the player's name as a parameter
    cursor.execute(query, ('%' + player_name + '%',))
    count = cursor.fetchone()[0]

    conn.close()

    return count

def get_match_ids(player_name, date):
    conn = sqlite3.connect('ipl_database.db')
    cursor = conn.cursor()

    # Define the SQL query to retrieve the match IDs based on the provided player name and date
    query = f'''
    SELECT ID
    FROM ipl_match_list
    WHERE date = ? AND (Team1Players LIKE '%{player_name}%' OR Team2Players LIKE '%{player_name}%')
    '''

    # Execute the query
    cursor.execute(query, (date,))
    match_ids = [row[0] for row in cursor.fetchall()]

    conn.close()

    return match_ids

def get_match_ids_and_teams_for_player(player_name):
    conn = sqlite3.connect('ipl_database.db')
    cursor = conn.cursor()
    id_list = []
    date_list = []
    team1_list = []
    team2_list = []
    cursor.execute("""
        SELECT ID,Date, Team1, Team2, Team1Players, Team2Players
        FROM ipl_match_list
        WHERE Team1Players LIKE ? OR Team2Players LIKE ?
    """, ('%' + player_name + '%', '%' + player_name + '%'))

    result = cursor.fetchall()

    # print(len(result))
    for match_id, date, team1, team2, pl1, pl2 in result:
        id_list.append(match_id)
        date_list.append(date)
        
        if player_name in pl1:
            # print(f"Match ID: {match_id}, {player_name} is in {team1}, playing against {team2} on {date}")
            team1_list.append(team1)
            team2_list.append(team2)
        else:
            team1_list.append(team2)
            team2_list.append(team1)
            # print(f"Match ID: {match_id}, {player_name} is in {team2}, playing against {team1} on {date}")

    conn.close()
    return id_list, date_list, team1_list, team2_list

def get_batting_positions_id_innings(match_id, innings):
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    # SQL query to fetch all unique batters in the specified match ID and innings
    query = '''
    SELECT DISTINCT batter
    FROM ipl_ball_by_ball
    WHERE ID = ? AND innings = ?
    ORDER BY overs, ballnumber
    '''

    cursor.execute(query, (match_id, innings))
    batting_positions = [row[0] for row in cursor.fetchall()]

    conn.close()
    return batting_positions


def find_batting_positions(player_name):
    id_list, date_list, team1_list, team2_list = get_match_ids_and_teams_for_player(player_name)

    batting_position = [0] * 11

    for i in id_list:
        b1 = get_batting_positions_id_innings(i, 1)
        b2 = get_batting_positions_id_innings(i, 2)
    
        if player_name in b1:
            for j in range(len(b1)):
                if b1[j] == player_name:
                    batting_position[j]+=1
        
        if player_name in b2:
            for j in range(len(b2)):
                if b2[j] == player_name:
                    batting_position[j]+=1
    
    return batting_position


def fetch_player_stats(player_name):
    
    start_date, end_date = get_first_and_last_match_dates(player_name)
    innings_played = find_batting_positions(player_name)
    total_balls_bowled = total_bowls(player_name, start_date, end_date)
    total_matches = num_matches(player_name, start_date, end_date)
    # print(sum(innings_played))
    # print({'Innings': innings_played, 'Balls': total_balls_bowled, 'Matches': total_matches})
    return {'Innings': innings_played, 'Balls': total_balls_bowled, 'Matches': total_matches}

def classify_player(player_stats):
    balls_bowled_per_match = player_stats['Balls'] / player_stats["Matches"]
    
    # Calculate the percentage of innings played at each batting position
    total_innings = sum(player_stats['Innings'])
    percentages = []
    if total_innings == 0:
        percentages = [0] * 11
    else:
        percentages = [innings / total_innings * 100 for innings in player_stats['Innings']]
        
    
    if percentages[0] + percentages[1] >= 80 and balls_bowled_per_match < 5:
        return "Opening Batsman"
    elif percentages[0] + percentages[1] + percentages[2] >= 70 and balls_bowled_per_match < 5:
        return "Top Order"
    elif percentages[2] + percentages[3] + percentages[4] >= 80 and balls_bowled_per_match < 5:
        return "Middle-order Batsman"
    elif percentages[4] + percentages[5] + percentages[6] >= 60 and balls_bowled_per_match < 5:
        return "Finisher"
    elif percentages[0] + percentages[1] + percentages[2] + percentages[3] + percentages[4] + percentages[5] >= 70 and balls_bowled_per_match > 15:
        return "All-Rounder"
    elif percentages[0] + percentages[1] + percentages[2] + percentages[3] + percentages[4] + percentages[5] >= 80 and 6 <= balls_bowled_per_match <= 15:
        return "Batting All-Rounder"
    elif (percentages[0] + percentages[1] + percentages[2] + percentages[3] + percentages[4] + percentages[5] + percentages[6] >= 65 or
          percentages[0] + percentages[1] + percentages[2] + percentages[3] + percentages[4] + percentages[5] + percentages[6] + percentages[7] >= 70) and balls_bowled_per_match > 15:
        return "Bowling All-Rounder"
    elif balls_bowled_per_match > 15:
        return "Bowler"
    elif percentages[0] + percentages[1] + percentages[2] + percentages[3] + percentages[4] + percentages[5] + percentages[6] >= 70:
        return "Batter"
    else:
        return "Player"


def get_first_and_last_match_dates(player_name):
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    # Fetch the first match date for the player
    cursor.execute("SELECT MIN(Date) FROM ipl_match_list WHERE Team1Players LIKE ? OR Team2Players LIKE ?", ('%' + player_name + '%', '%' + player_name + '%'))
    first_match_date = cursor.fetchone()[0]

    # Fetch the last match date for the player
    cursor.execute("SELECT MAX(Date) FROM ipl_match_list WHERE Team1Players LIKE ? OR Team2Players LIKE ?", ('%' + player_name + '%', '%' + player_name + '%'))
    last_match_date = cursor.fetchone()[0]

    conn.close()

    return first_match_date, last_match_date

def batter_innings(player_name, start_date, end_date):
    # Connect to the SQLite database
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    
    # SQL query to count the unique number of times the player is batter or non-striker for every ID
    query = '''
    SELECT ipl_ball_by_ball.ID, 
           COUNT(DISTINCT CASE WHEN batter = ? THEN innings ELSE NULL END) AS BatterAppearances,
           COUNT(DISTINCT CASE WHEN "non-striker" = ? THEN innings ELSE NULL END) AS NonStrikerAppearances
    FROM ipl_ball_by_ball
    JOIN ipl_match_list ON ipl_ball_by_ball.ID = ipl_match_list.ID
    WHERE (batter = ? OR "non-striker" = ?)
          AND ipl_match_list.Date BETWEEN ? AND ?
    GROUP BY ipl_ball_by_ball.ID
    '''

    # Execute the query
    cursor.execute(query, (player_name, player_name, player_name, player_name, start_date, end_date))

    # Fetch the result
    results = cursor.fetchall()
    total_matches = len(results)
    
    conn.close()
    return total_matches

def bowler_innings(player_name, start_date, end_date):
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
          AND ipl_match_list.Date BETWEEN ? AND ?
    GROUP BY ipl_ball_by_ball.ID
    '''

    # Execute the query
    cursor.execute(query, (player_name, player_name, start_date, end_date))

    # Fetch the result
    results = cursor.fetchall()
    total_matches = len(results)
    
    conn.close()
    return total_matches

def num_matches(player_name, start_date, end_date):
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
    WHERE (ipl_match_list.Team1Players LIKE '%' || ? || '%' OR ipl_match_list.Team2Players LIKE '%' || ? || '%')
          AND ipl_match_list.Date BETWEEN ? AND ?
    '''

    # Execute the query
    cursor.execute(query, (player_name, player_name, player_name, player_name, start_date, end_date))

    # Fetch the result
    results = cursor.fetchall()
    total_matches = len(results)
    
    conn.close()
    return total_matches    

def bowls_played(player_name, start_date, end_date):
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    query = '''
    SELECT COUNT(*) AS TotalBatterAppearances
    FROM ipl_ball_by_ball AS b
    JOIN ipl_match_list AS m ON b.ID = m.ID
    WHERE b.batter = ? AND m.Date BETWEEN ? AND ? AND (b.extra_type IS NULL OR b.extra_type = 'byes' OR b.extra_type = 'legbyes' OR b.extra_type = 'noballs' )
    '''

    cursor.execute(query, (player_name, start_date, end_date))
    result = cursor.fetchone()
    balls_faced = result[0]

    conn.close()

    return balls_faced

def total_bowls(player_name, start_date, end_date):
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    query = '''
    SELECT COUNT(*) AS TotalBowlsPlayed
    FROM ipl_ball_by_ball AS b
    JOIN ipl_match_list AS m ON b.ID = m.ID
    WHERE b.bowler = ? AND m.Date BETWEEN ? AND ? AND (b.extra_type IS NULL OR b.extra_type LIKE "%byes%")
    '''

    cursor.execute(query, (player_name, start_date, end_date))
    result = cursor.fetchone()
    total_bowls_played = result[0]

    conn.close()
    return total_bowls_played

def batter_runs(player_name, start_date, end_date):
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    query = '''
    SELECT SUM(b.batsman_run) 
    FROM ipl_ball_by_ball AS b
    JOIN ipl_match_list AS m ON b.ID = m.ID
    WHERE b.batter = ? AND m.Date BETWEEN ? AND ?
    '''
    cursor.execute(query, (player_name, start_date, end_date))
    player_runs = cursor.fetchone()[0]

    conn.close()

    return player_runs


def batter_wickets(player_name, start_date, end_date):
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    
    query = '''
    SELECT COUNT(*) 
    FROM ipl_ball_by_ball AS b
    JOIN ipl_match_list AS m ON b.ID = m.ID
    WHERE b.player_out = ? AND m.Date BETWEEN ? AND ?
    '''
    cursor.execute(query, (player_name, start_date, end_date))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def batter_stats(player_name, start_date, end_date):
    player_runs = batter_runs(player_name, start_date, end_date)
    
    count = batter_wickets(player_name, start_date, end_date)
    
    batting_avg = np.nan if count == 0 else round(player_runs / count, 2)
    batting_strike_rate = np.nan if bowls_played(player_name, start_date, end_date) == 0 else round((player_runs*100) / bowls_played(player_name, start_date, end_date), 2)
    batter_dict = {}
    batter_dict['Matches'] = [num_matches(player_name, start_date, end_date)]
    batter_dict['Innings'] = [batter_innings(player_name, start_date, end_date)]
    batter_dict['Runs'] = [player_runs]
    batter_dict['Balls'] = [bowls_played(player_name, start_date, end_date)]
    batter_dict['Average'] = [batting_avg]
    batter_dict['Strike Rate'] = [batting_strike_rate]
    batter_dict['Not Outs'] = [batter_innings(player_name, start_date, end_date) - count]
    

    return batter_dict

def bowler_runs(player_name, start_date, end_date):

    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    query = '''
    SELECT SUM(total_run) AS TotalRunsGiven
    FROM ipl_ball_by_ball AS b
    JOIN ipl_match_list AS m ON b.ID = m.ID
    WHERE b.bowler = ? AND m.Date BETWEEN ? AND ? AND (b.extra_type IS NULL OR b.extra_type = 'noballs' OR b.extra_type = 'wides')
    '''

    cursor.execute(query, (player_name, start_date, end_date))
    result = cursor.fetchone()
    total_runs_given = result[0] if result[0] is not None else 0

    conn.close()
    return total_runs_given

def bowler_wickets(player_name, start_date, end_date):
    import sqlite3

    # Connect to the SQLite database
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    query = '''
    SELECT COUNT(*) AS WicketsTaken
    FROM ipl_ball_by_ball AS b
    JOIN ipl_match_list AS m ON b.ID = m.ID
    WHERE b.bowler = ? AND b.isWicketDelivery = 1 AND b.kind != 'run out' 
    AND m.Date BETWEEN ? AND ?
    '''

    cursor.execute(query, (player_name, start_date, end_date))
    result = cursor.fetchone()
    wickets_taken = result[0]

    conn.close()
    return wickets_taken


def bowler_stats(player_name, start_date, end_date):

    player_runs = bowler_runs(player_name, start_date, end_date)
    count = bowler_wickets(player_name, start_date, end_date)
    
    bowling_avg = np.nan if count == 0 else round(player_runs / count, 2)
    bowling_strike_rate = np.nan if count == 0 else round(total_bowls(player_name, start_date, end_date) / count, 2)
    bowling_eco = np.nan if total_bowls(player_name, start_date, end_date) == 0 else round((player_runs*6) / total_bowls(player_name, start_date, end_date), 2)
    bowler_dict = {}
    bowler_dict['Matches'] = [num_matches(player_name, start_date, end_date)]
    bowler_dict['Innings'] = [bowler_innings(player_name, start_date, end_date)]
    bowler_dict['Runs'] = [player_runs]
    bowler_dict['Wickets'] = [count]
    bowler_dict['Economy'] = [bowling_eco]
    bowler_dict['Balls'] = [total_bowls(player_name, start_date, end_date)]
    bowler_dict['Strike Rate'] = [bowling_strike_rate]
    bowler_dict['Average'] = [bowling_avg]
    
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