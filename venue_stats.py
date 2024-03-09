import sqlite3
import numpy as np
def get_first_and_last_match_dates(venue):
    conn = sqlite3.connect('./ipl_database.db')
    cursor = conn.cursor()

    # Fetch the first match date for the player
    cursor.execute("SELECT MIN(Date) FROM ipl_match_list WHERE Venue = ?", (venue))
    first_match_date = cursor.fetchone()[0]

    # Fetch the last match date for the player
    cursor.execute("SELECT MAX(Date) FROM ipl_match_list WHERE Venue = ?", (venue))
    last_match_date = cursor.fetchone()[0]

    conn.close()

    return first_match_date, last_match_date
