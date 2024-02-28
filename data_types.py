import sqlite3

# Establish a connection to the SQLite database
conn = sqlite3.connect('./ipl_database.db')

# Create a cursor object
cursor = conn.cursor()

# Fetch all the tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Iterate over the table names
for table in tables:
    table_name = table[0]
    print(f"Table: {table_name}")
     
    # Fetch the column names and datatypes for each table
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    
    # Print the column names and datatypes
    for column in columns:
        column_name = column[1]
        data_type = column[2]
        print(f"Column: {column_name}, Datatype: {data_type}")
    
    print()  # Add a newline between tables

# Close the connection
conn.close()
