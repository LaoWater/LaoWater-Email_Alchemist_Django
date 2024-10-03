##########################################
# Step 3: Generating E-mail patterns
# Only Separator allowed "_" - to be used multiple times. "+" and "." can be disregarded due to Gmail handling
#
#
#### Controlled Random Environment (AI) ####
# We will approach this in the following way:
# I. Draw data randomly from the Datasets of Name, others, years, numbers using Probability Distribution
# II. Form pairs for layer 1 data - then apply separator probability distribution based on chunks forming a pair
# III. Final Step: Use a Neural Network Model to rate the email on pre-training with real emails.
# *Reached Bottleneck of being very hard to find active email and in the grey line of ethic/un-ethic
# *Decided to use a simple API call on a prompt/fine-tuned models for exactly this step - rating batches of 100s emails
#
# EDIT: Reached bottleneck of being unable to mx records check per email due to security policies.
# Still, we adapt.
# For at the end of the day, it is but a tool - and it is left to One's imagination the many ways of achieving a task.
##########################################

from .step2_MariaDB_database_engine import connect_to_database, separate_names, create_and_populate_numeric_tables
import random
from itertools import combinations


# Load Database Values
class DatabaseLoader:
    def __init__(self):
        self.connection = connect_to_database()
        self.cursor = self.connection.cursor()

    def load_words(self):
        query = "SELECT * FROM words order by NoOfLetters, Word"
        self.cursor.execute(query)
        words = self.cursor.fetchall()
        return [{"word": row[1], "NoOfLetters": row[2]} for row in words]

    def load_names(self):
        query = "SELECT * FROM names order by NoOfLetters, Word"
        self.cursor.execute(query)
        names = self.cursor.fetchall()
        return [{"word": row[1], "NoOfLetters": row[2]} for row in names]

    def load_common_years(self):
        query = "SELECT * FROM common_years"
        self.cursor.execute(query)
        common_years = self.cursor.fetchall()
        return [{"ID": row[0], "word": row[1]} for row in common_years]

    def load_common_numbers(self):
        query = "SELECT * FROM common_numbers"
        self.cursor.execute(query)
        common_numbers = self.cursor.fetchall()
        return [{"ID": row[0], "word": row[1]} for row in common_numbers]

    def close_connection(self):
        self.cursor.close()
        self.connection.close()


class EmailGenerator:
    def __init__(self, words_data, names_data, years_data, numbers_data):
        self.words_data = words_data
        self.names_data = names_data
        self.years_data = years_data
        self.numbers_data = numbers_data

    @staticmethod
    def layer_1_select_number_of_elements():
        """Selects the number of elements to be used in the email based on probabilities."""
        elements_count = random.choices(
            population=[2, 3, 4],
            weights=[0.4, 0.35, 0.25],
            k=1
        )[0]
        return elements_count

    def layer_2_select_elements(self, elements_count):
        """Selects elements (name, word, year, number) based on probabilities and rules."""
        elements = []
        available_choices = [
            ("name", self.names_data),
            ("word", self.words_data),
            ("year", self.years_data),
            ("number", self.numbers_data)
        ]
        weights = [0.33, 0.29, 0.16, 0.22]
        normalized_weights_first_element = [0.63, 0.47]

        element_type_count = {"name": 0, "word": 0, "year": 0, "number": 0}

        # Ensure that numbers/years don't appear as the first element
        for i in range(elements_count):
            if i == 0:
                # For the first element, exclude years and numbers
                element_type = random.choices(
                    population=["name", "word"],
                    weights=normalized_weights_first_element,
                    k=1
                )[0]
            else:
                # For subsequent el, allow all types and balance weights considering the 1st element is forced-string
                element_type = random.choices(
                    population=["name", "word", "year", "number"],
                    weights=weights,
                    k=1
                )[0]

                # Ensure only one number or year is selected per email
                if element_type in ["year", "number"] and any(el[0] in ["year", "number"] for el in elements):
                    element_type = random.choices(
                        population=["name", "word"],
                        weights=[0.57, 0.43],
                        k=1
                    )[0]

                # Ensure no full username consists of the same type of element if elements_count >= 3
                if elements_count >= 3:
                    # Track how many elements of each type we've added
                    element_type_count[element_type] += 1
                    # If we already have two of the same type, force a different type
                    if element_type_count[element_type] >= 2:
                        # Select a different type of element, excluding the current element type
                        allowed_types = [t for t in ["name", "word", "year", "number"] if element_type_count[t] < 2]
                        if allowed_types:
                            element_type = random.choice(allowed_types)

            # Pick a random element from the selected category
            selected_element = random.choice(next(data for t, data in available_choices if t == element_type))
            elements.append((element_type, selected_element["word"]))

        return elements

    def generate_email(self):
        """Generates an email address based on the selection from Layer 1 and 2."""
        elements_count = self.layer_1_select_number_of_elements()
        elements = self.layer_2_select_elements(elements_count)

        email_username_parts = []
        separator_added = False

        for i, element in enumerate(elements):
            email_username_parts.append(element[1])

            # Apply separator logic
            if i < len(elements) - 1:  # Don't add a separator after the last element
                if not separator_added:
                    # First separator has a 65% chance of being added
                    add_separator = random.random() < 0.65
                    if add_separator:
                        email_username_parts.append("_")
                        separator_added = True
                else:
                    # Subsequent separators have an 11% chance
                    add_separator = random.random() < 0.11
                    if add_separator:
                        email_username_parts.append("_")

        # Join elements to form the username
        email_username = "".join(email_username_parts)

        # Append @gmail.com
        email_address = f"{email_username}@gmail.com"

        return email_username, email_address


def load_data(print_loading_data):
    db_loader = DatabaseLoader()

    words = db_loader.load_words()
    names = db_loader.load_names()
    common_years = db_loader.load_common_years()
    common_numbers = db_loader.load_common_numbers()

    db_loader.close_connection()

    if print_loading_data:
        print(f" Extracted cleaned Database Data: \n Words: {words}")
        print(f" Names: {names}")
        print(f" Years: {common_years}")
        print(f" Numbers: {common_numbers} \n")

    return words, names, common_years, common_numbers


def generate_usernames(count):
    usernames = []

    for _ in range(count):
        record_username, record_full_email = email_generator.generate_email()
        usernames.append(record_username)
    return {"usernames": usernames}


########################
## Main Script Starts ##
## Load Database Data ##
## Use print_loading_data = True to see all processing steps ##
########################

# Initializing Class Variable & Load Data
max_retries = 3
retries = 0
words_data, names_data, common_years_data, common_numbers_data = None, None, None, None

while retries < max_retries:
    try:
        # Try loading the data
        words_data, names_data, common_years_data, common_numbers_data = load_data(print_loading_data=False)
        print("Data loaded successfully.")
        break  # Exit the loop if loading is successful
    except Exception as e:
        # Handle the error and retry
        print(f"Error loading data: {e}")
        print("Attempting to create and populate numeric tables...")

        # Execute the function to create and populate the tables
        create_and_populate_numeric_tables()

        # Increment the retry counter
        retries += 1

        # If the maximum retries have been reached, stop trying
        if retries == max_retries:
            print("Max retries reached. Could not load data.")
            raise  # Re-raise the exception to halt execution or handle as needed

email_generator = EmailGenerator(words_data, names_data, common_years_data, common_numbers_data)

if __name__ == "__main__":

    # Generate 10 emails as an example
    print("Starting Main Script... \n")
    generated_usernames = generate_usernames(10)

    print(generated_usernames)

