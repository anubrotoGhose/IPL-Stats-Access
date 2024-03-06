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
    print(1, start_date, end_date)
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

def innings_by_innings_list_batting(name, id_list):
    batter,	Runs_Scored, Balls_Faced, Four_Count, Six_Count, Dismissal_Type, fielders_involved, Bowler = [], [], [], [], [], [], [], []

    batter_dict = {}
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    for ID in id_list:
        query = '''
        SELECT 
            batter AS Name,
            SUM(batsman_run) AS Runs_Scored,
            COUNT(CASE WHEN extra_type IS NULL OR extra_type = 'byes' OR extra_type = 'legbyes' OR extra_type = 'noballs' THEN 1 ELSE NULL END) AS Balls_Faced,
            SUM(CASE WHEN batsman_run = 4 THEN 1 ELSE 0 END) AS Four_Count,
            SUM(CASE WHEN batsman_run = 6 THEN 1 ELSE 0 END) AS Six_Count,
            CASE WHEN MAX(isWicketDelivery) = 1 THEN MAX(kind) ELSE 'not out' END AS Dismissal_Type, 
            MAX(CASE WHEN isWicketDelivery = 1 THEN fielders_involved ELSE NULL END) AS fielders_involved,
            MAX(CASE WHEN isWicketDelivery = 1 AND kind <> 'run out' THEN bowler ELSE NULL END) AS Bowler
        FROM 
            ipl_ball_by_ball
        WHERE 
            batter = ? AND ID = ?
        GROUP BY 
            batter;
        '''
        cursor.execute(query, (name, ID))
        results = cursor.fetchall()
        if results:
            x = results[0]
            batter.append(x[0])
            Runs_Scored.append(x[1])
            Balls_Faced.append(x[2])
            Four_Count.append(x[3])
            Six_Count.append(x[4])
            Dismissal_Type.append(x[5])
            fielders_involved.append(x[6])
            Bowler.append(x[7])
        else:
            batter.append(None)
            Runs_Scored.append(None)
            Balls_Faced.append(None)
            Four_Count.append(None)
            Six_Count.append(None)
            Dismissal_Type.append(None)
            fielders_involved.append(None)
            Bowler.append(None)
    
    Date, Venue, Season, MatchNumber, City = innings_by_innings_list_match_list_details(id_list)
    batter_dict["Date"] = Date
    batter_dict["MatchNumber"] = MatchNumber
    batter_dict["Season"] = Season
    batter_dict["batter"] = batter
    batter_dict["Runs_Scored"] = Runs_Scored
    batter_dict["Balls_Faced"] = Balls_Faced
    batter_dict["Four_Count"] = Four_Count
    batter_dict["Six_Count"] = Six_Count
    batter_dict["Dismissal_Type"] = Dismissal_Type
    batter_dict["fielders_involved"] = fielders_involved
    batter_dict["Bowler"] = Bowler
    batter_dict["Venue"] = Venue
    batter_dict["City"] = City
    batter_dict["ID"] = id_list
    
    conn.close()
    df = pd.DataFrame(batter_dict)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date', ascending=True)
    return df


def innings_by_innings_list_bowling(name, id_list):
    Bowler = []
    Runs_Conceded = []
    Balls_Bowled = []
    Overs = []
    Eco = []
    Six_Count = []
    Four_Count = []
    Dismissal_Type = []
    Wides = []
    NoBalls = []
    bowler_dict = {}
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    for ID in id_list:
        query = '''
        SELECT 
            bowler AS Name,
            SUM(CASE WHEN extra_type IS NULL OR extra_type = 'noballs' OR extra_type = 'wides' THEN total_run ELSE 0 END) AS Runs_Conceded,
            COUNT(CASE WHEN extra_type IS NULL OR extra_type = 'byes' OR extra_type = 'legbyes' THEN 1 END) AS Balls_Bowled,
            SUM(CASE WHEN batsman_run = 6 THEN 1 ELSE 0 END) AS Six_Count,
            SUM(CASE WHEN batsman_run = 4 THEN 1 ELSE 0 END) AS Four_Count,
            MAX(CASE WHEN isWicketDelivery = 1 THEN kind ELSE NULL END) AS Dismissal_Type,
            SUM(CASE WHEN extra_type = 'wides' THEN 1 ELSE 0 END) AS Wides,
            SUM(CASE WHEN extra_type = 'noballs' THEN 1 ELSE 0 END) AS NoBalls
        FROM 
            ipl_ball_by_ball
        WHERE 
            bowler = ? AND ID = ?
        GROUP BY 
            bowler;
        '''
        cursor.execute(query, (name, ID))
        results = cursor.fetchall()
        if results:
            x = results[0]
            Bowler.append(x[0])
            Runs_Conceded.append(x[1])
            Balls_Bowled.append(x[2])
            Overs.append(str(x[2]//6)+"."+str(x[2]%6))
            Eco.append(0)
            Six_Count.append(x[3])
            Four_Count.append(x[4])
            Dismissal_Type.append(x[5])
            Wides.append(x[6])
            NoBalls.append(x[7])
        else:
            Bowler.append(None)
            Runs_Conceded.append(None)
            Balls_Bowled.append(None)
            Overs.append(None)
            Six_Count.append(None)
            Four_Count.append(None)
            Dismissal_Type.append(None)
            Wides.append(None)
            NoBalls.append(None)
    Date, Venue, Season, MatchNumber, City = innings_by_innings_list_match_list_details(id_list)
    bowler_dict["Date"] = Date
    bowler_dict["MatchNumber"] = MatchNumber
    bowler_dict["Seasons"] = Season
    bowler_dict["Bowler"] = Bowler
    bowler_dict["Runs_Conceded"] = Runs_Conceded
    bowler_dict["Balls_Bowled"] = Balls_Bowled
    bowler_dict["Overs"] = Overs
    bowler_dict["Six_Count"] = Six_Count
    bowler_dict["Four_Count"] = Four_Count
    bowler_dict["Wides"] = Wides
    bowler_dict["NoBalls"] = NoBalls
    bowler_dict["Venue"] = Venue
    bowler_dict["City"] = City
    bowler_dict["ID"] = id_list
    
    conn.close()
    df = pd.DataFrame(bowler_dict)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date', ascending=True)
    return df

def innings_by_innings_list_fieldings(player_name, id_list):
    conn = sqlite3.connect('ipl_database.db')
    cursor = conn.cursor()
    Fielder = []
    Catches = []
    Run_Outs = []
    Stumpings = []
    f_dict = {}
    for ID in id_list:
        # SQL query to retrieve fielding stats for the specified player and match ID
        query = '''
        SELECT 
            SUM(CASE WHEN fielders_involved = ? AND kind = 'caught' THEN 1 
                    WHEN kind = 'caught and bowled' AND bowler = ? THEN 1 ELSE 0 END) AS Catches,
            SUM(CASE WHEN fielders_involved = ? AND kind = 'run out' THEN 1 ELSE 0 END) AS Runouts,
            SUM(CASE WHEN fielders_involved = ? AND kind = 'stumped' THEN 1 ELSE 0 END) AS Stumpings
        FROM 
            ipl_ball_by_ball
        WHERE 
            ID = ?;
        '''
        # Execute the query with player name and match ID as parameters
        cursor.execute(query, (player_name, player_name, player_name, player_name, ID))
        fielding_stats = cursor.fetchall()

        if fielding_stats:
            x = fielding_stats[0]
            Fielder.append(player_name)
            Catches.append(x[0])
            Run_Outs.append(x[1])
            Stumpings.append(x[2])
        else:
            Fielder.append(None)
            Catches.append(None)
            Run_Outs.append(None)
            Stumpings.append(None)


    Date, Venue, Season, MatchNumber, City = innings_by_innings_list_match_list_details(id_list)
    f_dict["Date"] = Date
    f_dict["MatchNumber"] = MatchNumber
    f_dict["Seasons"] = Season
    f_dict["Fielder"] = Fielder
    f_dict["Catches"] = Catches
    f_dict["Run_Outs"] = Run_Outs
    f_dict["Stumpings"] = Stumpings
    f_dict["Venue"] = Venue
    f_dict["City"] = City
    f_dict["ID"] = id_list
    
    conn.close()
    df = pd.DataFrame(f_dict)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date', ascending=True)
    return df


def home_match_ID_list(name, id_list, team1_list, team2_list):
    team1_list = team1_list.split(",")
    team2_list = team2_list.split(",")
    for ID in id_list:
        conn = sqlite3.connect('./ipl_database.db')
        cursor = conn.cursor()
        query = """
        
        """
    pass

def career_summary_batting_venue(name, id_list):
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    query = """
    SELECT ipl_match_list.ID
    FROM
    ipl_match_list
    WHERE  
    """
    cursor.execute(query, (name, ID))
    pass

def career_summary_batting(name, id_list):
    batter,	Runs_Scored, Balls_Faced, Four_Count, Six_Count, Dismissal_Type, fielders_involved, Bowler = [], [], [], [], [], [], [], []

    batter_dict = {}
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    for ID in id_list:
        query = '''
        SELECT 
            batter AS Name,
            SUM(batsman_run) AS Runs_Scored,
            COUNT(CASE WHEN extra_type IS NULL OR extra_type = 'byes' OR extra_type = 'legbyes' OR extra_type = 'noballs' THEN 1 ELSE NULL END) AS Balls_Faced,
            SUM(CASE WHEN batsman_run = 4 THEN 1 ELSE 0 END) AS Four_Count,
            SUM(CASE WHEN batsman_run = 6 THEN 1 ELSE 0 END) AS Six_Count,
            CASE WHEN MAX(isWicketDelivery) = 1 THEN MAX(kind) ELSE 'not out' END AS Dismissal_Type, 
            MAX(CASE WHEN isWicketDelivery = 1 THEN fielders_involved ELSE NULL END) AS fielders_involved,
            MAX(CASE WHEN isWicketDelivery = 1 AND kind <> 'run out' THEN bowler ELSE NULL END) AS Bowler
        FROM 
            ipl_ball_by_ball
        WHERE 
            batter = ? AND ID = ?
        GROUP BY 
            batter;
        '''
        cursor.execute(query, (name, ID))
        results = cursor.fetchall()
        if results:
            x = results[0]
            batter.append(x[0])
            Runs_Scored.append(x[1])
            Balls_Faced.append(x[2])
            Four_Count.append(x[3])
            Six_Count.append(x[4])
            Dismissal_Type.append(x[5])
            fielders_involved.append(x[6])
            Bowler.append(x[7])
        else:
            batter.append(None)
            Runs_Scored.append(None)
            Balls_Faced.append(None)
            Four_Count.append(None)
            Six_Count.append(None)
            Dismissal_Type.append(None)
            fielders_involved.append(None)
            Bowler.append(None)
    
    Date, Venue, Season, MatchNumber, City = innings_by_innings_list_match_list_details(id_list)
    batter_dict["Date"] = Date
    batter_dict["MatchNumber"] = MatchNumber
    batter_dict["Season"] = Season
    batter_dict["batter"] = batter
    batter_dict["Runs_Scored"] = Runs_Scored
    batter_dict["Balls_Faced"] = Balls_Faced
    batter_dict["Four_Count"] = Four_Count
    batter_dict["Six_Count"] = Six_Count
    batter_dict["Dismissal_Type"] = Dismissal_Type
    batter_dict["fielders_involved"] = fielders_involved
    batter_dict["Bowler"] = Bowler
    batter_dict["Venue"] = Venue
    batter_dict["City"] = City
    batter_dict["ID"] = id_list
    
    conn.close()
    df = pd.DataFrame(batter_dict)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date', ascending=True)
    return df


def career_summary_bowling(name, id_list):
    Bowler = []
    Runs_Conceded = []
    Balls_Bowled = []
    Overs = []
    Eco = []
    Six_Count = []
    Four_Count = []
    Dismissal_Type = []
    Wides = []
    NoBalls = []
    bowler_dict = {}
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()
    for ID in id_list:
        query = '''
        SELECT 
            bowler AS Name,
            SUM(CASE WHEN extra_type IS NULL OR extra_type = 'noballs' OR extra_type = 'wides' THEN total_run ELSE 0 END) AS Runs_Conceded,
            COUNT(CASE WHEN extra_type IS NULL OR extra_type = 'byes' OR extra_type = 'legbyes' THEN 1 END) AS Balls_Bowled,
            SUM(CASE WHEN batsman_run = 6 THEN 1 ELSE 0 END) AS Six_Count,
            SUM(CASE WHEN batsman_run = 4 THEN 1 ELSE 0 END) AS Four_Count,
            MAX(CASE WHEN isWicketDelivery = 1 THEN kind ELSE NULL END) AS Dismissal_Type,
            SUM(CASE WHEN extra_type = 'wides' THEN 1 ELSE 0 END) AS Wides,
            SUM(CASE WHEN extra_type = 'noballs' THEN 1 ELSE 0 END) AS NoBalls
        FROM 
            ipl_ball_by_ball
        WHERE 
            bowler = ? AND ID = ?
        GROUP BY 
            bowler;
        '''
        cursor.execute(query, (name, ID))
        results = cursor.fetchall()
        if results:
            x = results[0]
            Bowler.append(x[0])
            Runs_Conceded.append(x[1])
            Balls_Bowled.append(x[2])
            Overs.append(str(x[2]//6)+"."+str(x[2]%6))
            Eco.append(0)
            Six_Count.append(x[3])
            Four_Count.append(x[4])
            Dismissal_Type.append(x[5])
            Wides.append(x[6])
            NoBalls.append(x[7])
        else:
            Bowler.append(None)
            Runs_Conceded.append(None)
            Balls_Bowled.append(None)
            Overs.append(None)
            Six_Count.append(None)
            Four_Count.append(None)
            Dismissal_Type.append(None)
            Wides.append(None)
            NoBalls.append(None)
    Date, Venue, Season, MatchNumber, City = innings_by_innings_list_match_list_details(id_list)
    bowler_dict["Date"] = Date
    bowler_dict["MatchNumber"] = MatchNumber
    bowler_dict["Seasons"] = Season
    bowler_dict["Bowler"] = Bowler
    bowler_dict["Runs_Conceded"] = Runs_Conceded
    bowler_dict["Balls_Bowled"] = Balls_Bowled
    bowler_dict["Overs"] = Overs
    bowler_dict["Six_Count"] = Six_Count
    bowler_dict["Four_Count"] = Four_Count
    bowler_dict["Wides"] = Wides
    bowler_dict["NoBalls"] = NoBalls
    bowler_dict["Venue"] = Venue
    bowler_dict["City"] = City
    bowler_dict["ID"] = id_list
    
    conn.close()
    df = pd.DataFrame(bowler_dict)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date', ascending=True)
    return df

def career_summary_fieldings(player_name, id_list):
    conn = sqlite3.connect('ipl_database.db')
    cursor = conn.cursor()
    Fielder = []
    Catches = []
    Run_Outs = []
    Stumpings = []
    f_dict = {}
    for ID in id_list:
        # SQL query to retrieve fielding stats for the specified player and match ID
        query = '''
        SELECT 
            SUM(CASE WHEN fielders_involved = ? AND kind = 'caught' THEN 1 
                    WHEN kind = 'caught and bowled' AND bowler = ? THEN 1 ELSE 0 END) AS Catches,
            SUM(CASE WHEN fielders_involved = ? AND kind = 'run out' THEN 1 ELSE 0 END) AS Runouts,
            SUM(CASE WHEN fielders_involved = ? AND kind = 'stumped' THEN 1 ELSE 0 END) AS Stumpings
        FROM 
            ipl_ball_by_ball
        WHERE 
            ID = ?;
        '''
        # Execute the query with player name and match ID as parameters
        cursor.execute(query, (player_name, player_name, player_name, player_name, ID))
        fielding_stats = cursor.fetchall()

        if fielding_stats:
            x = fielding_stats[0]
            Fielder.append(player_name)
            Catches.append(x[0])
            Run_Outs.append(x[1])
            Stumpings.append(x[2])
        else:
            Fielder.append(None)
            Catches.append(None)
            Run_Outs.append(None)
            Stumpings.append(None)


    Date, Venue, Season, MatchNumber, City = innings_by_innings_list_match_list_details(id_list)
    f_dict["Date"] = Date
    f_dict["MatchNumber"] = MatchNumber
    f_dict["Seasons"] = Season
    f_dict["Fielder"] = Fielder
    f_dict["Catches"] = Catches
    f_dict["Run_Outs"] = Run_Outs
    f_dict["Stumpings"] = Stumpings
    f_dict["Venue"] = Venue
    f_dict["City"] = City
    f_dict["ID"] = id_list
    
    conn.close()
    df = pd.DataFrame(f_dict)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date', ascending=True)
    return df