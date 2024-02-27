import data_manipulation
from time import time 
def fetch_player_stats(player_name):
    
    start_date, end_date = data_manipulation.get_first_and_last_match_dates(player_name)
    innings_played = data_manipulation.find_batting_positions(player_name)
    total_balls_bowled = data_manipulation.total_bowls(player_name, start_date, end_date)
    total_matches = data_manipulation.num_matches(player_name, start_date, end_date)
    print(sum(innings_played))
    print({'Innings': innings_played, 'Balls': total_balls_bowled, 'Matches': total_matches})
    return {'Innings': innings_played, 'Balls': total_balls_bowled, 'Matches': total_matches}

def classify_player(player_stats):
    balls_bowled_per_match = player_stats['Balls'] / player_stats["Matches"]
    
    # Calculate the percentage of innings played at each batting position
    total_innings = sum(player_stats['Innings'])
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
s1 = time()


# Fetch player stats for "DA Warner"
player_name = "SR Tendulkar"
player_stats = fetch_player_stats(player_name)

# Classify the player
classification = classify_player(player_stats)
print("Player Classification for", player_name + ":", classification)

s2 = time()
s3 = s2 -s1
print("Time Taken = ", s3)