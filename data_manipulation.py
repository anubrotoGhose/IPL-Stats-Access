import pandas as pd
import sqlite3
import numpy as np
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
        batting_avg = "inf"
    else:
        batting_avg = player_runs/count
    
    batter_dict = {}
    batter_dict['Total Runs'] = [player_runs]
    batter_dict['Batting Average'] = [round(batting_avg, 2)]
    # Close the connection
    conn.close()

    return batter_dict
