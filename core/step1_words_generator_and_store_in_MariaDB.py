# ###################################### ###################################### #
# ###################################### ###################################### #
# Step 1: Generating and Storing Words with NLTK and LangDetect
#
# In the first step, we focus on creating a dataset of words by leveraging libraries NLTK and LangDetect.
#
# Workflow Overview:
# I. Merge NLTK and LangDetect libraries to process the input data.
# II. Filter out offensive words and irrelevant terms to ensure the dataset is clean and reliable.
# III. Organize words into distinct categories based on the number of letters.
# IV. Store the cleaned and categorized data in the 'email_generation' database within the 'words' table
#    (columns: id, word, NoOfLetters) for future use in email generation.
#
# This step ensures that we begin the email generation process with a clean, linguistically accurate
# dataset that is free from inappropriate content, forming the foundation for later stages.
# ###################################### ###################################### #
# ###################################### ###################################### #

import time
import mysql.connector
from langdetect import detect, LangDetectException
from nltk.corpus import words as nltk_words


def connect_to_database():
    """Connect to the MariaDB database."""
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="email_generation",
        charset='utf8mb4',  # Set the charset
        collation='utf8mb4_general_ci'  # Set a compatible collation
    )
    return conn


def create_table(cur, table_name, clean=False):
    """Drop and create a table with a dynamic name."""
    # Drop the table if it exists
    if clean:
        cur.execute(f'DROP TABLE IF EXISTS `{table_name}`')

    # Create table for storing valid words with dynamic length (you can adjust the length as needed)
    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        word VARCHAR(10) NOT NULL UNIQUE,
        NoOfLetters INT NOT NULL
    );
    ''')


def is_english(text):
    """Check if the text is detected as English using langdetect."""
    try:
        if detect(text) == 'en':
            return True
    except LangDetectException:
        return False
    return False


def filter_and_store_english_words(cur, valid_words, table_name, word_len):
    """Filter words of length 3 from nltk, check if langdetect recognizes them as English, and store them."""
    count = 0
    offensive_words = load_offensive_words()
    for word in valid_words:
        if len(word) == word_len and is_english(word) and word.lower() not in offensive_words:
            count += 1
            print(f"Valid Word found! {word} at count {count}")

            # Insert the valid word and count into the database
            cur.execute(f"INSERT IGNORE INTO {table_name} (word, NoOfLetters) VALUES (%s, %s)", (word, word_len))


def load_offensive_words():
    """Load a list of offensive or inappropriate words."""
    return {
        'ass', 'bum', 'gay', 'pig', 'suck'
        'cunt', 'dick', 'fuck', 'slut', 'whore',
        'bitch', 'cocky', 'dicks', 'nigger', 'shit'
    }


def generate_X_letters_words(number_of_letters):
    # Load valid English words from nltk
    valid_words = set(nltk_words.words())

    # Connect to the database
    conn = connect_to_database()
    cur = conn.cursor()
    # Create Table if not exists, Possibility to dynamically create new tables on parameters
    # create_table(cur, f'{number_of_letters}letters_words')
    if number_of_letters == 3:
        create_table(cur, 'words')
    conn.commit()

    # Filter words of length 3 and check if they're English
    filter_and_store_english_words(cur, valid_words, 'words', number_of_letters)

    # Commit all the changes and close the connection
    conn.commit()
    cur.close()
    conn.close()


def regenerate_data(min_letters, max_letters):
    """Main function to execute the script."""
    start_time = time.time()

    # Define Loop for generating words of X numbers of letters
    for no_of_letters in range(min_letters, (max_letters+1)):
        print(f"DEBUG: Generating words with no of letters: {no_of_letters}")
        generate_X_letters_words(no_of_letters)

    end_time = time.time() - start_time
    print(f"Compute Time: {end_time} seconds")


