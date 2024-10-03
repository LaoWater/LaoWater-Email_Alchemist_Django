# ###################################### ###################################### #
# ###################################### ###################################### #
# Step 2: Cleaning and Filtering Data into Categories
#
# After processing raw data, the second step focuses on categorizing the data into meaningful groups.
# This categorization will later help in generating structured email patterns.
#
# Workflow Overview:
# I. Split the data into two primary categories:
#    1. Names & Nicknames: Identified by analyzing if the first character is uppercase.
#    2. Others: Words that do not follow the capitalization pattern or belong to common objects.
# II. Store these categorized entries in separate database tables:
#    - 'words' table for general words.
#    - 'names' table for names and nicknames.
# III. Generate number-related data with high-occurrence in e-mail usernames - leveraging years and common formats.
# IV. Prepare this categorized data for use in Step 3, where email patterns will be generated.
#
# By splitting the data into logical categories, this step allows us to have a focused and organized
# dataset, enhancing the relevance and structure of the email generation process.
# ###################################### ###################################### #
# ###################################### ###################################### #
import time
from decimal import Decimal

import mysql.connector


def connect_to_database():
    """Connect to the MariaDB database."""
    db_conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="email_generation",
        charset='utf8mb4',  # Set the charset
        collation='utf8mb4_general_ci'  # Set a compatible collation
    )
    return db_conn


def insert_into_table(table_name, word):
    """Inserts the word into the specified table."""
    # Connect to the database
    conn = connect_to_database()
    cur = conn.cursor()

    # Insert the word and its length into the table
    cur.execute(f'''
        INSERT IGNORE INTO `{table_name}` (word, NoOfLetters) 
        VALUES (%s, %s)
    ''', (word, len(word)))

    # Commit changes and close the connection
    conn.commit()
    cur.close()
    conn.close()

    print(f"Inserted '{word}' into {table_name}.")


def delete_table(table_name):
    """Delete all data from a table with a dynamic name."""
    # Connect to the database
    conn = connect_to_database()
    cur = conn.cursor()
    # Drop the table if it exists
    cur.execute(f'DELETE FROM `{table_name}`')

    # Commit the changes
    conn.commit()
    # Close the cursor and connection
    cur.close()
    conn.close()


def drop_table(table_name):
    """Drop and create a table with a dynamic name."""
    # Connect to the database
    conn = connect_to_database()
    cur = conn.cursor()
    # Drop the table if it exists
    cur.execute(f'DROP TABLE IF EXISTS `{table_name}`')

    # Commit the changes
    conn.commit()
    # Close the cursor and connection
    cur.close()
    conn.close()


def interrogate_scoring_table(table='high_rated_unames', history_table='high_rated_unames_history', limit_records=25):
    # Connect to the database
    conn = connect_to_database()
    cur = conn.cursor()

    # Create History Table as we will later disregard records from the main one as we parse it
    # Ensure the history table exists
    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS `{history_table}` LIKE `{table}`;
    ''')

    # Insert new records into the history table excluding duplicates
    cur.execute(f'''
    INSERT IGNORE INTO `{history_table}` (SELECT * FROM `{table}`
    WHERE username NOT IN (SELECT username FROM `{history_table}`));
    ''')

    # Commit the changes
    conn.commit()

    # Fetch the table data using the dynamic table name and limit the number of records
    cur.execute(f'''
    SELECT * FROM `{table}` ORDER BY score DESC LIMIT {limit_records};
    ''')

    # Fetch and print the column headers
    column_names = [i[0] for i in cur.description]

    # Fetch and print the rows
    rows = cur.fetchall()

    for row in rows:
        row_dict = dict(zip(column_names, row))

        # Convert Decimal to float for 'score' key
        if isinstance(row_dict.get('score'), Decimal):
            row_dict['score'] = float(row_dict['score'])

        print(row_dict)
        time.sleep(0.25)

    time.sleep(0.33)

    # Close the cursor and connection
    cur.close()
    conn.close()


def interrogate_table(table):
    # Connect to the database
    conn = connect_to_database()
    cur = conn.cursor()

    # Fetch the table data using the dynamic table name
    cur.execute(f'''
    SELECT * FROM `{table}`;
    ''')

    # Fetch and print the column headers
    column_names = [i[0] for i in cur.description]

    # Fetch and print the rows
    rows = cur.fetchall()

    print(f"\nTable Data from `{table}`:")
    for row in rows:
        print(dict(zip(column_names, row)))  # Use zip to pair column names with their respective values

    # Close the cursor and connection
    cur.close()
    conn.close()


def interrogate_final_table(fetch_top_production_records):
    # Connect to the database
    conn = connect_to_database()
    cur = conn.cursor()

    print("Current Main Production Final Table: ")
    # Fetch the table data using the dynamic table name
    cur.execute(f'''
        SELECT u1.username, u2.score, u1.search_result_title, u1.url 
        FROM high_probability_real_usernames u1
        INNER JOIN high_rated_unames_history u2 
        ON u1.username = u2.username
        ORDER BY u2.score desc
        LIMIT {fetch_top_production_records};
    ''')

    # Fetch and print the column headers (removing ID)
    column_names = ['username', 'score', 'search_result_title', 'url']

    # Fetch and print the rows
    rows = cur.fetchall()

    for row in rows:
        # Convert the row into a dictionary
        row_dict = dict(zip(column_names, row))

        # Convert score to a float if it's a Decimal or string representation of a number
        try:
            row_dict['score'] = float(row_dict['score'])
        except (ValueError, TypeError):
            row_dict['score'] = 0.0  # Fallback in case of an error

        # Print in the required order
        print(f"username: {row_dict['username']}, score: {row_dict['score']:.2f}, "
              f"search_result_title: {row_dict['search_result_title']}, URL: {row_dict['url']}")
        time.sleep(0.25)

    # Close the cursor and connection
    cur.close()
    conn.close()


def separate_names():
    # Connect to the database
    conn = connect_to_database()
    cur = conn.cursor()

    # Create the `names` table if it doesn't exist
    cur.execute('''
    CREATE TABLE IF NOT EXISTS names (
        id INT AUTO_INCREMENT PRIMARY KEY,
        word VARCHAR(10) NOT NULL UNIQUE,
        NoOfLetters INT NOT NULL
    );
    ''')

    # Insert records where the first letter of the word is uppercase
    cur.execute('''
    INSERT IGNORE INTO names (word, NoOfLetters)
    SELECT word, NoOfLetters
    FROM words
    WHERE BINARY LEFT(word, 1) = UPPER(LEFT(word, 1))
    ORDER BY NoOfLetters, word;
    ''')

    # Commit the transaction
    conn.commit()

    print("Records inserted into 'names' table where the first letter of the word is uppercase.")

    # Clean Original Table 'words' of extracted names
    cur.execute('''
    DELETE w 
    FROM words w 
    INNER JOIN names n 
    ON w.word = n.word;
    ''')

    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()


def create_and_populate_numeric_tables():
    # Connect to the database
    conn = connect_to_database()
    cur = conn.cursor()

    # 1. Create the `common_years` table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS common_years (
        id INT AUTO_INCREMENT PRIMARY KEY,
        word VARCHAR(10) NOT NULL UNIQUE
    );
    ''')
    print("Table `common_years` created.")

    # Insert the years from 1972 to 2030 as strings
    for year in range(1972, 2031):
        cur.execute('''
        INSERT IGNORE INTO common_years (word) VALUES (%s)
        ''', (str(year),))
    print("Table `common_years` populated.")

    # 2. Create the `common_numbers` table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS common_numbers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        word VARCHAR(10) NOT NULL UNIQUE
    );
    ''')
    print("Table `common_numbers` created.")

    # Insert numbers from 1 to 30 as strings
    for number in range(1, 31):
        cur.execute('''
        INSERT IGNORE INTO common_numbers (word) VALUES (%s)
        ''', (str(number),))

    # Insert numbers of the format: XXX, XXXX, X00, X000 as strings
    special_numbers = [
        33, 44, 55, 77, 88, 99, 89,  # Lucky Numbers
        100, 200, 300, 400, 500, 600, 700, 800, 900,  # X00 format
        1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000,  # X000 format
        111, 222, 333, 444, 555, 666, 777, 888, 999,  # XXX format
        1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999  # XXXX format
    ]

    for num in special_numbers:
        cur.execute('''
        INSERT IGNORE INTO common_numbers (word) VALUES (%s)
        ''', (str(num),))

    print("Table `common_numbers` populated.")

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()


def get_all_table_definitions():
    """Retrieves and prints the CREATE TABLE definition for each table in the database."""
    conn = connect_to_database()
    cursor = conn.cursor()

    # Get the list of tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        # Get the CREATE TABLE statement for each table
        cursor.execute(f"SHOW CREATE TABLE {table_name}")
        result = cursor.fetchone()
        print(f"Table: {table_name}\n")
        print(result[1])  # The CREATE TABLE statement
        print("\n" + "-" * 60 + "\n")

    cursor.close()
    conn.close()


def delete_all_tables():
    drop_table('common_numbers')
    drop_table('common_years')
    drop_table('high_probability_real_usernames')
    drop_table('high_rated_unames')
    drop_table('high_rated_unames_history')
    drop_table('names')
    drop_table('words')


# separate_names()