# ###################################### ###################################### #
# ###################################### ###################################### #
# Step 5: Validating and Storing High-Probability Usernames Through Web Scraping
#
# In this step, we focused on validating the top AI-scored usernames using Google search
# to determine their plausibility based on actual search results. The goal was to identify
# which usernames are more likely to belong to real users based on their presence in
# online content.
#
# Workflow Overview:
# I. Extract a set number of AI-scored usernames from the database.
# II. Perform a Google search for each username using the Google Custom Search API.
# III. Capture relevant details, including the search result title, snippet, and URL.
# IV. Store the validated usernames and their first search result in a separate database
#    table for future analysis.
# V. Optionally remove processed usernames from the source table to avoid rechecking.
#
# This approach ensures that we filter the generated usernames based on actual web presence,
# leading to a more targeted list of potential real-world usernames. By storing these validated
# entries in the database, we enable future data analysis and decision-making based on the
# credibility and presence of these usernames in publicly available content.
# ###################################### ###################################### #
# ###################################### ###################################### #

import time
import requests
from .step3_generate_emails_patterns import email_generator
from .step2_MariaDB_database_engine import connect_to_database, interrogate_table, \
    interrogate_final_table
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
API_KEY = os.getenv('API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')


def interrogate_scoring_table(limit=10, table='high_rated_unames', remove_checked=False):
    # Connect to the database
    conn = connect_to_database()
    cur = conn.cursor()
    print(f"\nLoading Data from All time AI High scoring usernames (Production Table) "
          f"\n(First Top {limit} Records as selected by User, to be processed in Search Engine)..")
    time.sleep(0.44)
    # Fetch the table data using the dynamic table name and limit
    cur.execute(f'''
    SELECT ID, username, score FROM `{table}` order by score desc LIMIT {limit};
    ''')

    # Fetch the rows
    rows = cur.fetchall()

    # Extract just the usernames into a list
    usernames = []
    for row in rows:
        row_dict = dict(zip(['ID', 'username', 'score'], row))

        # Append the username to the list
        usernames.append(row_dict['username'])

    # If the flag is set, remove these records from the table
    if remove_checked:
        # Collect IDs to delete
        ids_to_remove = tuple([row[0] for row in rows])  # IDs from the fetched rows
        cur.execute(f'''
        DELETE FROM `{table}` WHERE ID IN {ids_to_remove};
        ''')
        conn.commit()  # Commit the changes to the database

    # Close the cursor and connection
    cur.close()
    conn.close()

    # Return the list of usernames
    return usernames


def google_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        search_result = response.json()
        return search_result.get('items', [])  # Returns the list of search results
    else:
        print("Error:", response.status_code, response.text)
        return []


def scrape_google_for_validity(no_of_records, remove_record_after=False, exact_search_engine_match=False):
    # With Remove_checked=True, usernames are disregarded from database
    AI_high_scoring_usernames = interrogate_scoring_table(limit=no_of_records, remove_checked=remove_record_after)
    print(AI_high_scoring_usernames)

    if remove_record_after:
        print("Notice! Remove Option ticked, usernames will be removed from Database.high_rated_unames "
              "after being processed in current cycle."
              "The ones which qualify will be saved in Final Production table.")
    # Initialize a list to store high-probability real usernames with their search results
    high_probability_real_usernames = []

    # Step 2: Loop through the usernames and perform Google search
    for record_username in AI_high_scoring_usernames:
        # Step 3: Search for the username on Google
        search_results = google_search(record_username)
        print(f"\nSearching for *{record_username}*...")
        # Step 4: Check all search results to find an exact match in the snippet
        exact_result_found = False
        if search_results:
            for result in search_results:
                snippet = result['snippet']

                # Check for an exact match of the username within the snippet
                if record_username in snippet.split() or not exact_search_engine_match:
                    high_probability_real_usernames.append({
                        'username': record_username,
                        'title': result['title'],
                        'snippet': snippet,
                        'url': result['link']
                    })

                    # Print that the username is being saved and break after saving the first valid result
                    if exact_search_engine_match:
                        print(f"Exact match found! Saving *{record_username}* into high_probability_real_usernames...")
                        exact_result_found = True
                        break  # Stop checking after the first valid result is found
                    else:
                        print(f"Close match found! Saving *{record_username}* into high_probability_real_usernames...")
                        break

        # If no results found, ignore
        else:
            print(f"No search results found for {record_username}. Disregarding username..")

        # Step 5: Introduce a delay before the next iteration
        time.sleep(1.3)

    # Optional: Print out the saved usernames for review
    print(f"\nTotal usernames saved to Final Production Table: {len(high_probability_real_usernames)}")
    for entry in high_probability_real_usernames:
        print(f"Username: {entry['username']}, Search Result Title: {entry['title']}, URL: {entry['url']}")
        time.sleep(0.15)

    time.sleep(1)

    return high_probability_real_usernames


def save_final_high_prob_users(usernames_list):
    # Connect to the database

    conn = connect_to_database()
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS high_probability_real_usernames (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        search_result_title VARCHAR(255) NOT NULL,
        url VARCHAR(255) NOT NULL
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
    '''
    cursor.execute(create_table_query)
    conn.commit()

    # Insert the results into the database
    insert_query = '''
    INSERT IGNORE INTO high_probability_real_usernames (username, search_result_title, url) 
    VALUES (%s, %s, %s)
    '''

    # Prepare the data to insert
    data_to_insert = [(entry['username'], entry['title'], entry['url']) for entry in usernames_list]

    # Insert the data into the table
    cursor.executemany(insert_query, data_to_insert)
    conn.commit()

    # Close the database connection
    cursor.close()
    conn.close()


########################
## Main Script Starts ##
## Load High Scoring Usernames Data ##
########################

def main():
    high_prob_real_usernames = scrape_google_for_validity(10, remove_record_after=False,
                                                          exact_search_engine_match=False)

    # Final Step, Save Relevant High Probability E-mail usernames and disregard search_engine_test failed ones
    save_final_high_prob_users(high_prob_real_usernames)

    interrogate_final_table()