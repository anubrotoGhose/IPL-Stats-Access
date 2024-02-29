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


def fetch_batting_scorecard(ID, innings):
    conn = sqlite3.connect('./ipl_database.db')

    # Fetch batting data
    batting_query = '''
    SELECT ball.batter, SUM(ball.batsman_run) AS Runs_Scored, COUNT(*) AS Balls_Faced, 
           SUM(CASE WHEN ball.batsman_run = 4 THEN 1 ELSE 0 END) AS Four_Count,
           SUM(CASE WHEN ball.batsman_run = 6 THEN 1 ELSE 0 END) AS Six_Count,
           SUM(CASE WHEN ball.player_out != 'not out' THEN 1 ELSE 0 END) AS Out, 
           CASE WHEN MAX(ball.isWicketDelivery) = 1 THEN MAX(ball.kind) ELSE 'not out' END AS Dismissal_Type, 
           MAX(ball.fielders_involved) AS fielders_involved, 
           MAX(CASE WHEN ball.player_out != 'not out' THEN ball.bowler ELSE NULL END) AS Bowler
    FROM ipl_ball_by_ball AS ball
    JOIN (
        SELECT DISTINCT batter
        FROM ipl_ball_by_ball
        WHERE ID = ? AND innings = ?
        ORDER BY overs, ballnumber
    ) AS batting_order ON ball.batter = batting_order.batter
    WHERE ball.ID = ? AND ball.innings = ?
    GROUP BY ball.batter
    ORDER BY MIN(ball.overs), MIN(ball.ballnumber);  -- Order by batting position
    '''

    batting_data = pd.read_sql_query(batting_query, conn, params=(ID, innings, ID, innings))

    conn.close()

    return batting_data