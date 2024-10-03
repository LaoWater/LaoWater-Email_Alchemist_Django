# ###################################### ###################################### #
# ###################################### ###################################### #
# Step 6: User Data Processing and Finalizing High-Scoring Usernames
#
# In this step, we integrate both user-provided data and previously generated datasets
# to enhance the username generation process. We offer users the ability to upload their
# own datasets and adjust the existing models. This step also involves generating final
# high-probability usernames through AI scoring and validation workflows.
#
# Workflow Overview:
# I. Optionally upload user-provided datasets and insert the data into the 'names' and 'words' tables.
# II. Optionally regenerate the original datasets by adjusting the minimum and maximum letter constraints.
# III. Generate usernames based on predefined neural network patterns and datasets, using AI scoring agents.
# IV. Interrogate the database for the top AI-scored usernames and validate them through Google search.
# V. Store the validated usernames in the final production table for further use.
#
# This step allows a user-driven approach for enhancing the dataset, while also finalizing
# the process of generating high-probability usernames that have a strong web presence.
# It combines the flexibility of user input with automated scoring and validation to create
# a reliable pool of real-world usernames.
# ###################################### ###################################### #
# ###################################### ###################################### #


import time
from .step2_MariaDB_database_engine import (connect_to_database, interrogate_table, \
                                           interrogate_final_table, insert_into_table, delete_table, separate_names,
                                           create_and_populate_numeric_tables,
                                           interrogate_scoring_table)
from .step4_scoring_potential_records_wLLM import generate_usernames_with_AI_Scoring_agents
from .step1_words_generator_and_store_in_MariaDB import regenerate_data
from .step5_custom_search_engine_API import scrape_google_for_validity, save_final_high_prob_users
import os


def process_user_file_and_insert_data(subdirectory=r'User Upload', file_name='Names_and_words.txt', overwrite=False):
    """Reads the file from the specified subdirectory and inserts data into 'names' and 'words' tables."""

    # Construct full file path
    file_path = os.path.join(subdirectory, file_name)

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found.")
        return

    # Read the file content
    with open(file_path, 'r') as file:
        lines = file.readlines()

    if overwrite:
        delete_table('words')
        delete_table('names')

    # Process each line and insert into the correct table
    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace

        if line:  # Ensure the line is not empty
            table_name = 'names' if line[0].isupper() else 'words'
            insert_into_table(table_name, line)


def regenerate_original_data(min_letters=3, max_letters=5):
    # Provide Min&Max Number of Letters.
    create_and_populate_numeric_tables()
    regenerate_data(min_letters, max_letters)
    separate_names()
    # regenerate_data()


###################################
## Global Variables to handle UI ##
###################################

################
#  User Flags  #
# To Be Implemented in GUI #
################

# Number of raw generate usernames to be then processed towards multiple-layers Filtering
no_of_raw_generated_usernames = 50
# User uploads file of Names and Words to be integrated in script's logic
upload_your_own_data = False
# In case of User uploaded data, if User wants to strictly use his provided data and exclude original Names&Words.
overwrite_existing_data = False
# In case words definitions & Rules are changed or Data becomes corrupted - Regenerate Data.
regenerate_original_datasets = False
# Limit number of Records shown in final step - Final Production Table
fetch_top_production_records = 10
# Remove Records after being parsed and filtered towards Main Production Table
remove_record_after = False


# Regenerate Original Dataset using Pre-Defined Model: Provide Min and Max Letters blueprints
if regenerate_original_datasets:
    regenerate_original_data(3, 5)

if upload_your_own_data:
    process_user_file_and_insert_data(overwrite=overwrite_existing_data)


# Words & Names Data Base Model has been generated at this point, whether
# 1. We're using our own Database of words&names
# 2. Using strictly user provided base model
# or 3. An integration of both

########################
########################
## Main Script Starts ##
########################
########################

def main_script():
    # Generate usernames based on chosen Dataset and Email Patterns Neural Network
    generate_usernames_with_AI_Scoring_agents(no_of_raw=no_of_raw_generated_usernames,
                                              no_of_sorted=int(no_of_raw_generated_usernames / 7))
    time.sleep(1.5)

    limit_ai_high_scoring_records = 5
    # Review Current High Scoring usernames
    print(f"\nCurrent top {limit_ai_high_scoring_records} High Scoring usernames from current cycle: ")
    interrogate_scoring_table(limit_records=limit_ai_high_scoring_records)

    ##################################
    ## Final processing step (Optional) ###
    ## Searching for top X most high-scoring usernames on Google ###
    ## remove_record_after = True - Remove Record from High-Scoring storage to avoid duplicates searching,
    ## As it will be automatically saved to Main Production Final Table ##
    ## exact_search_engine_match = True - Only absolute exact matches are considered relevant, rest disregarded ##
    ##################################

    high_prob_real_usernames = scrape_google_for_validity(10, remove_record_after=True,
                                                          exact_search_engine_match=False)

    # Final Step, Save Relevant High Probability E-mail usernames
    save_final_high_prob_users(high_prob_real_usernames)

    print(f"\n\nCurrent top {fetch_top_production_records} High Scoring usernames (Final Production Table) Data: "
          f"\naka. Top high-rated usernames gathered From all Running Cycles - "
          f"\n~ Can be used in final confirmation to call Email Validation Service API with access to mx Records ~")
    interrogate_final_table(fetch_top_production_records)


main_script()
