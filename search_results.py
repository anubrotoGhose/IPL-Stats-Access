import pandas as pd
import sqlite3
# conn = sqlite3.connect('./ipl_database.db')
# # Query the database
# df_ball = pd.read_sql_query('SELECT * FROM ipl_ball_by_ball;', conn)

# # Display the first few rows of the table
# print(df_ball)

# # Close the connection
# conn.close()

# # Reconnect to the database
# conn = sqlite3.connect('./ipl_database.db')
# # Query the database
# df_match = pd.read_sql_query('SELECT * FROM ipl_match_list;', conn)

# # Display the first few rows of the table
# print(df_match)


# # Close the connection
# conn.close()



def extract_elements():

    # Path to your SQLite database
    db_path = './ipl_database.db'

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # SQL query to fetch unique cities
    unique_cities_query = "SELECT DISTINCT City FROM ipl_match_list;"

    #SQL query to fetch unique venues
    unique_venues_query = "SELECT DISTINCT Venue FROM ipl_match_list;"

    # SQL query to fetch unique Umpire1
    unique_umpire_query = """
    SELECT DISTINCT Umpire1 FROM ipl_match_list
    UNION
    SELECT DISTINCT Umpire2 FROM ipl_match_list;
    """

    #SQL query to fetch unique player names
    # unique_player_query = "SELECT DISTINCT Team1Players FROM ipl_match_list;"

    unique_player_query = """
    SELECT DISTINCT Team1Players FROM ipl_match_list
    UNION
    SELECT DISTINCT Team1Players FROM ipl_match_list;
    """

    #SQL query to fetch unique team names

    unique_team_name_query = """
    SELECT DISTINCT Team1 FROM ipl_match_list
    UNION
    SELECT DISTINCT Team2 FROM ipl_match_list;
    """

    # Execute the queries and fetch the results
    try:
        cursor.execute(unique_cities_query)
        unique_cities = cursor.fetchall()
        unique_cities = [item[0] for item in unique_cities if item[0] is not None]

        cursor.execute(unique_venues_query)
        unique_venues = cursor.fetchall()
        unique_venues = [item[0] for item in unique_venues if item[0] is not None]
        
        cursor.execute(unique_umpire_query)
        unique_umpire = cursor.fetchall()
        unique_umpire = [item[0] for item in unique_umpire if item[0] is not None]

        cursor.execute(unique_team_name_query)
        unique_team_name = cursor.fetchall()
        unique_team_name = [item[0] for item in unique_team_name if item[0] is not None]

        cursor.execute(unique_player_query)
        unique_player = cursor.fetchall()
        unique_player = [item[0] for item in unique_player if item[0] is not None]
        unique_player_name = []
        for i in unique_player:

            # Remove brackets and split the string
            elements = i.strip("[]").split(", ")

            # Trim each element and remove quotes
            elements = [element.strip("'") for element in elements]

            for j in elements:
                unique_player_name.append(j)
        
        unique_player_name = list(set(unique_player_name))
        # print("Unique Cities:", unique_cities,"\n")
        # print("Unique Venues:", unique_venues,"\n")
        # print("Unique Umpire:", unique_umpire,"\n")
        # print("Unique Team Names", unique_team_name,"\n")
        # print("Unique Player Names", unique_player_name,"\n")

        search_dict = {}
        search_dict['Players'] = unique_player_name
        search_dict['Venues'] = unique_venues
        search_dict['Cities'] = unique_cities
        search_dict['Teams'] = unique_team_name
        search_dict['Umpires'] = unique_umpire


        

        # Convert the dictionary into a pandas DataFrame
        # df = pd.DataFrame(search_dict)


        # print(search_dict)
            
        return search_dict
        

    except sqlite3.Error as error:
        print("Error while executing SQL", error)

    finally:
        # Close the database connection
        conn.close()

# # Find the maximum length of the lists in the dictionary
#         max_length = max(len(lst) for lst in search_dict.values())

#         # Pad shorter lists with None
#         for key in search_dict:
#             search_dict[key] += [None] * (max_length - len(search_dict[key]))
def filter_dict_by_search(substring):
    
    search_dict = extract_elements()
    # Create a new dictionary to store the filtered lists
    filtered_dict = {}

    # Iterate over each key and list in the original dictionary
    for key, value_list in search_dict.items():
        # Use list comprehension to filter the list
        filtered_list = [item for item in value_list if substring.lower() in item.lower()]
        # Assign the filtered list to the corresponding key in the new dictionary
        filtered_dict[key] = filtered_list

    return filtered_dict


