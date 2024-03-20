import sqlite3
import pandas as pd
def get_match_ids_and_teams_for_player(player_name, start_date, end_date):
    conn = sqlite3.connect('ipl_database.db')
    cursor = conn.cursor()
    id_list = []
    date_list = []
    team1_list = []
    team2_list = []
    v = []
    cursor.execute("""
        SELECT ID,Date, Team1, Team2, Team1Players, Team2Players, Venue
        FROM ipl_match_list
        WHERE (Team1Players LIKE ? OR Team2Players LIKE ?) AND Date BETWEEN ? AND ?
    """, ('%' + player_name + '%', '%' + player_name + '%', start_date, end_date))

    result = cursor.fetchall()

    # print(len(result))
    for match_id, date, team1, team2, pl1, pl2, venue in result:
        id_list.append(match_id)
        date_list.append(date)
        v.append(venue)
        if player_name in pl1:
            # print(f"Match ID: {match_id}, {player_name} is in {team1}, playing against {team2} on {date}")
            team1_list.append(team1)
            team2_list.append(team2)
        else:
            team1_list.append(team2)
            team2_list.append(team1)
            # print(f"Match ID: {match_id}, {player_name} is in {team2}, playing against {team1} on {date}")

    conn.close()
    return id_list, date_list, sorted(list(set(team1_list))), sorted(list(set(team2_list))), sorted(list(set(v)))

def innings_by_innings_list_match_list_details(id_list):
    Date = []
    Venue = []
    Season = []
    MatchNumber = []
    City = []
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    for ID in id_list:
        query = '''
        SELECT 
            Date, Venue, Season, MatchNumber, City   
        FROM 
            ipl_match_list
        WHERE 
            ID = ?
        GROUP BY 
            ID;
        '''
        cursor.execute(query, (ID,))
        x = cursor.fetchall()[0]
        Date.append(x[0])
        Venue.append(x[1])
        Season.append(x[2])
        MatchNumber.append(x[3])
        City.append(x[4])

    conn.close()

    return Date, Venue, Season, MatchNumber, City


def innings_by_innings_list_batting(player_name, start_date, end_date):
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('./ipl_database.db')

    # Define the SQL query with the corrected column name and date range condition
    query = f'''
    SELECT
        ml.Date,
        ml.MatchNumber,
        ml.Season,
        SUM(CASE WHEN batter = ? THEN batsman_run ELSE 0 END) AS runs_scored,
        COUNT(CASE WHEN (extra_type IS NULL OR extra_type = 'byes' OR extra_type = 'legbyes' OR extra_type = 'noballs') AND (batter = ?) THEN 1 ELSE NULL END) AS balls_faced,
        MAX(CASE WHEN isWicketDelivery = 1 THEN kind ELSE 'Not Out' END) AS dismissal_kind,
        COUNT(CASE WHEN (batsman_run = 6) AND (batter = ?) THEN 1 ELSE NULL END) AS Six_Count,
        COUNT(CASE WHEN (batsman_run = 4) AND (batter = ?) THEN 1 ELSE NULL END) AS Four_Count,
        ml.Venue,
        ml.City,
        bb.ID
    FROM
        ipl_ball_by_ball bb
    JOIN
        ipl_match_list ml ON bb.ID = ml.ID
    WHERE
        (batter = ? OR "non-striker" = ?) AND
        ml.Date BETWEEN ? AND ?
    GROUP BY
        bb.ID
    ORDER BY
        bb.ID;
    '''

    # Execute the query with the player name and date range as parameters
    df = pd.read_sql_query(query, conn, params=(player_name, player_name, player_name, player_name, player_name, player_name, start_date, end_date))

    # Close the connection
    conn.close()

    return df
def innings_by_innings_list_bowling(player_name, start_date, last_date):
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('ipl_database.db')

    # Define the SQL query with the corrected syntax
    query = f'''
    SELECT
        ml.Date,
        ml.MatchNumber,
        ml.Season,
        SUM(CASE WHEN extra_type IS NULL OR extra_type = 'noballs' OR extra_type = 'wides' THEN total_run ELSE 0 END) AS runs_conceded,
        SUM(CASE WHEN isWicketDelivery = 1 AND kind != 'run out' THEN 1 ELSE 0 END) AS wickets_taken,
        COUNT(CASE WHEN extra_type IS NULL OR extra_type LIKE "%byes%" THEN 1 END) AS balls_bowled,
        CAST((COUNT(CASE WHEN extra_type IS NULL OR extra_type LIKE '%byes%' THEN 1 ELSE 0 END) - 
        SUM(CASE WHEN extra_type = 'wides' THEN 1 ELSE 0 END) - 
        SUM(CASE WHEN extra_type = 'noballs' THEN 1 ELSE 0 END)) / 6 AS TEXT) || '.' ||
        ((COUNT(CASE WHEN extra_type IS NULL OR extra_type LIKE '%byes%' THEN 1 ELSE 0 END) - 
        SUM(CASE WHEN extra_type = 'wides' THEN 1 ELSE 0 END) - 
        SUM(CASE WHEN extra_type = 'noballs' THEN 1 ELSE 0 END)) % 6) AS Overs,
        SUM(batsman_run) AS Runs_Conceding,
        ROUND((CAST(SUM(batsman_run) AS FLOAT) / 
        (COUNT(CASE WHEN extra_type IS NULL OR extra_type LIKE '%byes%' THEN 1 ELSE 0 END) - 
        SUM(CASE WHEN extra_type = 'wides' THEN 1 ELSE 0 END) - 
        SUM(CASE WHEN extra_type = 'noballs' THEN 1 ELSE 0 END))) * 6, 2) AS Economy,
        SUM(CASE WHEN isWicketDelivery = 1 THEN 1 ELSE 0 END) AS Wickets,
        COUNT(CASE WHEN total_run = 0  THEN 1 END) AS Dots,
        COUNT(CASE WHEN extra_type = 'wides' THEN 1 END) AS Wides,
        COUNT(CASE WHEN extra_type = 'noballs' THEN 1 END) AS NoBalls,
        ml.Venue,
        ml.City,
        bb.ID
    FROM
        ipl_ball_by_ball as bb
    JOIN
        ipl_match_list ml ON bb.ID = ml.ID
    WHERE
        (bowler = ?) AND
        ml.Date BETWEEN ? AND ?
    GROUP BY
        bb.ID
    ORDER BY
        bb.ID;
    '''
    # Execute the query with the player name as a parameter
    df = pd.read_sql_query(query, conn, params=(player_name,  start_date, last_date))

    # Close the connection
    conn.close()
    return df

def innings_by_innings_list_fieldings(name, start_date, end_date):
    conn = sqlite3.connect('./ipl_database.db')
    query = f"SELECT * FROM ipl_field_by_innings WHERE (Date BETWEEN '{start_date}' AND '{end_date}') AND Fielder = '{name}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def player_stats_venue_based_batting(player_name, start_date, end_date):

    # Connect to the SQLite database
    conn = sqlite3.connect('ipl_database.db')

    # Read ipl_match_list and ipl_ball_by_ball tables into pandas dataframes
    ipl_match_list = pd.read_sql_query("SELECT * FROM ipl_match_list", conn)
    ipl_ball_by_ball = pd.read_sql_query("SELECT * FROM ipl_ball_by_ball", conn)

    # Close the database connection
    conn.close()
    ipl_match_list = ipl_match_list[(ipl_match_list['Date'] >= start_date) & (ipl_match_list['Date'] <= end_date)]
    # Merge the dataframes
    merged_data = pd.merge(ipl_match_list, ipl_ball_by_ball, on='ID')

    player_data = merged_data[merged_data['batter'] == player_name]

    # Group by venue and aggregate batting statistics
    venue_stats = player_data.groupby('Venue').agg(
        runs=('batsman_run', 'sum'),
        dismissals=('isWicketDelivery', 'sum'),
        balls=('ballnumber', 'count'),
        fours=('batsman_run', lambda x: (x == 4).sum()),
        sixes=('batsman_run', lambda x: (x == 6).sum()),
        strike_rate=('batsman_run', lambda x: (x.sum() / len(x)) * 100)
    )

    # Calculate average runs per dismissal
    venue_stats['Average'] = venue_stats['runs'] / venue_stats['dismissals'].replace(0, pd.NA)

    # Reset index to make Venue a column instead of index
    venue_stats.reset_index(inplace=True)

    # Display the venue-wise batting statistics
    return venue_stats

import pandas as pd
import sqlite3

def player_stats_venue_based_bowler(player_name, start_date, end_date):
    # Connect to the SQLite database
    conn = sqlite3.connect('ipl_database.db')

    # Read ipl_match_list and ipl_ball_by_ball tables into pandas dataframes
    ipl_match_list = pd.read_sql_query("SELECT * FROM ipl_match_list", conn)
    ipl_ball_by_ball = pd.read_sql_query("SELECT * FROM ipl_ball_by_ball", conn)
    
    # Filter matches based on start_date and end_date
    ipl_match_list['Date'] = pd.to_datetime(ipl_match_list['Date'])
    ipl_match_list = ipl_match_list[(ipl_match_list['Date'] >= start_date) & (ipl_match_list['Date'] <= end_date)]

    # Close the database connection
    conn.close()

    # Merge the dataframes
    merged_data = pd.merge(ipl_match_list, ipl_ball_by_ball, on='ID')

    # Filter data for matches where the specified player bowled
    player_data = merged_data[merged_data['bowler'] == player_name]

    # Group by venue and aggregate bowling statistics
    venue_stats = player_data.groupby('Venue').agg(
        runs_conceded=('total_run', 'sum'),
        wickets_taken=('isWicketDelivery', 'sum'),
        balls_bowled=('ballnumber', 'count'),
        fours=('total_run', lambda x: ((x == 4) | (x == 5)).sum()),  # Assuming 5 denotes no-ball in total_run
        sixes=('total_run', lambda x: ((x == 6) | (x == 7)).sum()),  # Assuming 7 denotes wide in total_run
    )

    # Calculate bowling strike rate
    venue_stats['Strike_Rate'] = venue_stats['balls_bowled'] / venue_stats['wickets_taken']

    # Calculate average runs per wicket
    venue_stats['Average'] = venue_stats['runs_conceded'] / venue_stats['wickets_taken'].replace(0, pd.NA)

    # Reset index to make Venue a column instead of index
    venue_stats.reset_index(inplace=True)

    # Display the venue-wise bowling statistics
    return venue_stats


def player_stats_venue_based_fielder(player_name, start_date, end_date):
    conn = sqlite3.connect('./ipl_database.db')

    sql_query = """
    SELECT 
        i.Venue,
        SUM(CASE WHEN b.kind IN ('caught', 'caught and bowled') THEN 1 ELSE 0 END) AS catches,
        SUM(CASE WHEN b.kind = 'run out' THEN 1 ELSE 0 END) AS runouts,
        SUM(CASE WHEN b.kind = 'stumped' THEN 1 ELSE 0 END) AS stumpings
    FROM 
        ipl_match_list i
    JOIN 
        ipl_ball_by_ball b ON i.ID = b.ID
    WHERE 
        (b.fielders_involved LIKE ? AND b.kind IN ('caught', 'caught and bowled', 'run out', 'stumped'))
        AND i.Date BETWEEN ? AND ?
    GROUP BY 
        i.Venue;
    """

    fielding_stats = pd.read_sql_query(sql_query, conn, params=('%' + player_name + '%', start_date, end_date))

    conn.close()

    return fielding_stats


def player_stats_season_based_fielder(player_name, start_date, end_date):
    conn = sqlite3.connect('./ipl_database.db')

    sql_query = """
    SELECT 
        i.Season,
        SUM(CASE WHEN b.kind IN ('caught', 'caught and bowled') THEN 1 ELSE 0 END) AS catches,
        SUM(CASE WHEN b.kind = 'run out' THEN 1 ELSE 0 END) AS runouts,
        SUM(CASE WHEN b.kind = 'stumped' THEN 1 ELSE 0 END) AS stumpings
    FROM 
        ipl_match_list i
    JOIN 
        ipl_ball_by_ball b ON i.ID = b.ID
    WHERE 
        (b.fielders_involved LIKE ? AND b.kind IN ('caught', 'caught and bowled', 'run out', 'stumped'))
        AND i.Date BETWEEN ? AND ?
    GROUP BY 
        i.Season;
    """

    fielding_stats = pd.read_sql_query(sql_query, conn, params=('%' + player_name + '%', start_date, end_date))

    conn.close()

    return fielding_stats


def player_batting_stats_season_wise(player_name, start_date, end_date):
    # Connect to the SQLite database
    conn = sqlite3.connect('ipl_database.db')

    # Define the SQL query to retrieve batting stats season-wise for the specified player within the date range
    query = """
        SELECT
            ipl_match_list.Season,
            COUNT(DISTINCT ipl_match_list.ID) AS Matches,
            COUNT(DISTINCT ipl_ball_by_ball.Innings) AS Innings,
            SUM(ipl_ball_by_ball.batsman_run) AS Runs,
            COUNT(ipl_ball_by_ball.ID) AS Balls,
            ROUND(AVG(ipl_ball_by_ball.batsman_run * 1.0 / NULLIF(ipl_ball_by_ball.isWicketDelivery, 0)), 2) AS Average,
            ROUND(SUM(ipl_ball_by_ball.batsman_run) * 100.0 / NULLIF(SUM(ipl_ball_by_ball.isWicketDelivery), 0), 2) AS StrikeRate,
            SUM(CASE WHEN ipl_ball_by_ball.isWicketDelivery = 0 THEN 1 ELSE 0 END) AS NotOuts
        FROM
            ipl_ball_by_ball
        JOIN
            ipl_match_list ON ipl_ball_by_ball.ID = ipl_match_list.ID
        WHERE
            ipl_ball_by_ball.batter = ? AND ipl_match_list.Date BETWEEN ? AND ?
        GROUP BY
            ipl_match_list.Season
        ORDER BY
            ipl_match_list.Season
    """

    # Execute the query and fetch the results
    batting_stats_season_wise = pd.read_sql_query(query, conn, params=(player_name, start_date, end_date))

    # Close the database connection
    conn.close()

    return batting_stats_season_wise

def player_bowling_stats_season_wise(player_name, start_date, end_date):
    # Connect to the SQLite database
    conn = sqlite3.connect('ipl_database.db')

    # Read ipl_match_list and ipl_ball_by_ball tables into pandas dataframes
    ipl_match_list = pd.read_sql_query("SELECT * FROM ipl_match_list", conn)
    ipl_ball_by_ball = pd.read_sql_query("SELECT * FROM ipl_ball_by_ball", conn)
    
    # Filter matches based on start_date and end_date
    ipl_match_list['Date'] = pd.to_datetime(ipl_match_list['Date'])
    ipl_match_list = ipl_match_list[(ipl_match_list['Date'] >= start_date) & (ipl_match_list['Date'] <= end_date)]

    # Close the database connection
    conn.close()

    # Merge the dataframes
    merged_data = pd.merge(ipl_match_list, ipl_ball_by_ball, on='ID')

    # Filter data for matches where the specified player bowled
    player_data = merged_data[merged_data['bowler'] == player_name]

    # Group by venue and aggregate bowling statistics
    season_stats = player_data.groupby('Season').agg(
        runs_conceded=('total_run', 'sum'),
        wickets_taken=('isWicketDelivery', 'sum'),
        balls_bowled=('ballnumber', 'count'),
        fours=('total_run', lambda x: ((x == 4) | (x == 5)).sum()),  # Assuming 5 denotes no-ball in total_run
        sixes=('total_run', lambda x: ((x == 6) | (x == 7)).sum()),  # Assuming 7 denotes wide in total_run
    )

    # Calculate bowling strike rate
    season_stats['Strike_Rate'] = season_stats['balls_bowled'] / season_stats['wickets_taken']

    # Calculate average runs per wicket
    season_stats['Average'] = season_stats['runs_conceded'] / season_stats['wickets_taken'].replace(0, pd.NA)

    # Reset index to make Venue a column instead of index
    season_stats.reset_index(inplace=True)

    # Display the venue-wise bowling statistics
    return season_stats