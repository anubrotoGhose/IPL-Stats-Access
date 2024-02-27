import sqlite3
import numpy as np
import pandas as pd

# conn = sqlite3.connect('./ipl_database.db')
# df_ball = pd.read_sql_query('SELECT * FROM ipl_ball_by_ball;', conn)
# print(df_ball.columns)
# print(df_ball)

# conn.close()


# conn = sqlite3.connect('./ipl_database.db')
# df_match= pd.read_sql_query('SELECT * FROM ipl_match_list;', conn)
# print(df_match.columns)
# print(df_match)

# conn.close()

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('./ipl_database.db')
cursor = conn.cursor()

# Replace 'player_name' with the actual name of the player you're querying
player_name = 'G Gambhir'

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
    print(f"Match ID: {match_id}, Batter Appearances: {batter_appearances}, Non-Striker Appearances: {non_striker_appearances}")
    c+=1

print(c)

# Close the connection
conn.close()


import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('./ipl_database.db')
cursor = conn.cursor()

# Replace 'player_name' with the actual name of the player you're querying
player_name = 'SK Warne'

# SQL query to count the number of times the player is in the bowler column for every ID
query = '''
SELECT ipl_ball_by_ball.ID, COUNT(DISTINCT CASE WHEN bowler = ? THEN innings ELSE NULL END) AS BowlerAppearances
FROM ipl_ball_by_ball
WHERE bowler = ?
GROUP BY ipl_ball_by_ball.ID
'''

# Execute the query
cursor.execute(query, (player_name, player_name))

# Fetch the result
results = cursor.fetchall()
counter = 0
for match_id, bowler_appearances in results:
    print(f"Match ID: {match_id}, Bowler Appearances: {bowler_appearances}")
    counter+=1
print(counter)
# Close the connection
conn.close()