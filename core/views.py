import time
import os
import io
import sys
from django.shortcuts import render
from .step2_MariaDB_database_engine import (
    connect_to_database,
    interrogate_table,
    interrogate_final_table,
    insert_into_table,
    delete_table,
    separate_names,
    create_and_populate_numeric_tables,
    interrogate_scoring_table
)
from .step4_scoring_potential_records_wLLM import generate_usernames_with_AI_Scoring_agents
from .step1_words_generator_and_store_in_MariaDB import regenerate_data
from .step5_custom_search_engine_API import scrape_google_for_validity, save_final_high_prob_users


# Helper to capture console output
class CaptureOutput(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = io.StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout


# Function to process user-uploaded file and insert data into database
def process_user_file_and_insert_data(subdirectory=r'User Upload', file_name='Names_and_words.txt', overwrite=False):
    """Reads the file from the specified subdirectory and inserts data into 'names' and 'words' tables."""

    file_path = os.path.join(subdirectory, file_name)

    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found.")
        return

    with open(file_path, 'r') as file:
        lines = file.readlines()

    if overwrite:
        delete_table('words')
        delete_table('names')

    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace
        if line:  # Ensure the line is not empty
            table_name = 'names' if line[0].isupper() else 'words'
            insert_into_table(table_name, line)


# Function to regenerate the original dataset with specified letter constraints
def regenerate_original_data(min_letters=3, max_letters=5):
    create_and_populate_numeric_tables()
    regenerate_data(min_letters, max_letters)
    separate_names()


# Main script logic
def main_script():
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

    # Generate usernames based on chosen Dataset and Email Patterns Neural Network
    generate_usernames_with_AI_Scoring_agents(no_of_raw=no_of_raw_generated_usernames,
                                              no_of_sorted=int(no_of_raw_generated_usernames / 7))
    time.sleep(1.5)

    limit_ai_high_scoring_records = 10
    # Review Current High Scoring usernames
    print(f"\nCurrent top {limit_ai_high_scoring_records} High Scoring usernames from current cycle: ")
    interrogate_scoring_table(limit_records=limit_ai_high_scoring_records)

    # Final processing: Searching for top high-scoring usernames on Google and validating them
    high_prob_real_usernames = scrape_google_for_validity(10, remove_record_after=True,
                                                          exact_search_engine_match=False)

    # Save relevant high-probability usernames
    save_final_high_prob_users(high_prob_real_usernames)

    # Display final usernames
    print(f"\n\nCurrent top {limit_ai_high_scoring_records} Final High Scoring usernames (Final Production Table):")
    interrogate_final_table(fetch_top_production_records)


# Django view that runs the main script and captures the output
def process_usernames(request):
    output = []
    with CaptureOutput() as output:
        # Flags for customization (you can make these dynamic via the front end)
        upload_your_own_data = False
        overwrite_existing_data = False
        regenerate_original_datasets = False

        # Optionally regenerate original dataset
        if regenerate_original_datasets:
            regenerate_original_data(3, 5)

        # Optionally process user-provided data
        if upload_your_own_data:
            process_user_file_and_insert_data(overwrite=overwrite_existing_data)

        # Run the main script to generate usernames
        main_script()

    # Pass the captured output to the template for display
    return render(request, 'result.html', {'output': output})


def home(request):
    return render(request, 'home.html')


def index(request):
    return render(request, 'index.html')
