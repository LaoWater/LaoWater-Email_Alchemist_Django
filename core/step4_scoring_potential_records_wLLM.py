# ######################################### #########################################
# ######################################### #########################################
# Step 4: Scoring Generated Usernames with AI Agents
#
# After generating a list of usernames, we will evaluate their plausibility using AI-driven
# scoring agents. We rely on multiple agents, each providing a score for the likelihood of a username being real,
# based on linguistic and pattern analysis.
#
# AI-Driven Evaluation Workflow
# I. Generate a batch of usernames using controlled random patterns from previously defined datasets.
# II. Utilize three different AI agents to independently score each username.
# III. Aggregate(Sum and Average) the scores from all agents and calculate an average score for each username.
# IV. Sort usernames based on their average score, selecting the top-performing ones.
# V. Store the top N usernames in a MariaDB database for future use.
#
# This allows us to create a controlled environment for generating and evaluating usernames with the help of AI.
# The scoring process is further enhanced by integrating a database to save well-rated usernames, nullyfing API cost.
#
# This step not only enhances the generation and evaluation of usernames
# but also introduces a scalable and robust storage solution for future analysis or use.
# ######################################### #########################################
# ######################################### #########################################

import json
import re
import time
from openai import OpenAI
from .step3_generate_emails_patterns import generate_usernames, load_data
from .step1_words_generator_and_store_in_MariaDB import connect_to_database
from .step2_MariaDB_database_engine import interrogate_table, interrogate_scoring_table


def emails_scoring_agent_1(list_of_emails, model="gpt-4o-mini", temperature=0.8):
    client = OpenAI()
    messages = [
        {
            "role": "system",
            "content": "You are an assistant specializing in evaluating the plausibility of usernames. "
                       "For each username, you will assign a score from 0.01 (highly unlikely to be real) to "
                       "0.99 (highly likely to be real) based on patterns, typing flow, sentiment analysis, "
                       "and other linguistic factors."
        },
        {
            "role": "user",
            "content": f"""
Please analyze the following list of usernames and emails. For each username, provide a score between 0.01 and 0.99 
indicating its likelihood of being real. Return the results in JSON format.

List:
{list_of_emails}

Example format:
[
    {{"username1": score1}},
    {{"username2": score2}},
    ...
]
"""
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=3333
    )

    response_text = response.choices[0].message.content
    return response_text


def emails_scoring_agent_2(list_of_emails, model="gpt-4o-mini", temperature=0.8):
    client = OpenAI()
    messages = [
        {
            "role": "system",
            "content": "As an expert in linguistic patterns and user behavior, you evaluate the authenticity "
                       "of usernames. Score each username from 0.01 "
                       "(very unlikely to be real) to 0.99 (very likely to be real), "
                       "considering factors like repetition, typing flow, and sentiment."
        },
        {
            "role": "user",
            "content": f"""
Evaluate the following usernames and emails. Assign a score to each username based on 
its likelihood of being genuine. Provide the results in JSON format.

Usernames and Emails:
{list_of_emails}

Example format:
[
    {{"username1": score1}},
    {{"username2": score2}},
    ...
]
"""
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=3333
    )

    response_text = response.choices[0].message.content
    return response_text


def emails_scoring_agent_3(list_of_emails, model="gpt-4o-mini", temperature=0.8):
    client = OpenAI()
    messages = [
        {
            "role": "system",
            "content": "You are a critical analyzer of usernames, assessing their probability of being real. "
                       "For each username, provide a score from 0.01 (highly improbable) to 0.99 (highly probable), "
                       "using insights from patterns, typing flow, and word sentiment."
        },
        {
            "role": "user",
            "content": f"""
Analyze the following usernames and emails. 
For each, assign a probability score and return the results in JSON format.

Data:
{list_of_emails}

Example format:
[
    {{"username1": score1}},
    {{"username2": score2}},
    ...
]
"""
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=3333
    )

    response_text = response.choices[0].message.content
    return response_text


def extract_json_from_response(response_text):
    """
    Extracts the JSON-like part from the response text by removing extra characters.
    """
    # Use regex to capture the part inside the square brackets
    json_like_part = re.search(r"\[\s*{.*?}\s*\]", response_text, re.DOTALL)

    if json_like_part:
        json_string = json_like_part.group(0)
        try:
            # Convert it into a valid Python object
            return json.loads(json_string)
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON from the extracted string.")
            print(f"Extracted string: {json_string}")
            return []
    else:
        print("Error: Failed to find JSON-like part in the response.")
        return []


def calculate_average_scores(agent_results):
    average_scores = {}

    for agent_result in agent_results:
        # Each agent_result is a list of dictionaries
        for entry in agent_result:
            # Each entry is a dictionary with one key-value pair
            for usern, score in entry.items():
                if usern not in average_scores:
                    average_scores[usern] = 0
                average_scores[usern] += score

    # Divide each total score by the number of agents to get the average
    num_agents = len(agent_results)
    for usern in average_scores:
        average_scores[usern] /= num_agents

    # Sort usernames by score, from high to low
    sorted_usern = sorted(average_scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_usern


def generate_usernames_with_AI_Scoring_agents(no_of_raw, no_of_sorted):
    # Generate usernames
    print("Phase I: Generating usernames...")
    generated_usernames = generate_usernames(no_of_raw)
    print(f"Generated Usernames: {generated_usernames}\n")

    # Call all three agents
    print("Calling Agent 1 for scoring...")
    result_1_raw = emails_scoring_agent_1(generated_usernames)
    result_1 = extract_json_from_response(result_1_raw)
    print(f"Agent 1 Results: {json.dumps(result_1, separators=(',', ':'), ensure_ascii=False)}\n")

    print("Calling Agent 2 for scoring...")
    result_2_raw = emails_scoring_agent_2(generated_usernames)
    result_2 = extract_json_from_response(result_2_raw)
    print(f"Agent 2 Results: {json.dumps(result_2, separators=(',', ':'), ensure_ascii=False)}\n")

    print("Calling Agent 3 for scoring...")
    result_3_raw = emails_scoring_agent_3(generated_usernames)
    result_3 = extract_json_from_response(result_3_raw)
    print(f"Agent 3 Results: {json.dumps(result_3, separators=(',', ':'), ensure_ascii=False)}\n")
    time.sleep(0.55)

    # Collect results from all agents
    print("Aggregating results from all agents...")
    time.sleep(1.5)
    all_agent_results = [result_1, result_2, result_3]

    # Calculate the average scores and sort the usernames
    print("\nCalculating average scores and sorting usernames...")
    time.sleep(1.33)
    sorted_usernames = calculate_average_scores(all_agent_results)

    # Pretty print the results and collect top usernames
    # print("\nAll processed Usernames ranked by average score (from high to low):")
    time.sleep(0.55)
    top_usernames = []
    for idx, (username, avg_score) in enumerate(sorted_usernames):
        # print(f"Username: {username}, Average Score: {avg_score:.2f}")
        if idx < no_of_sorted:
            top_usernames.append((username, avg_score))

    time.sleep(1)
    print(f"Calculated High-Performing usernames from this cycle: {top_usernames}")
    time.sleep(1.33)
    ###########################
    # Connect to the database
    # Store top no_of_sorted usernames
    #####################################

    conn = connect_to_database()
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS high_rated_unames (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        score DECIMAL(5,2) NOT NULL
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
    '''
    cursor.execute(create_table_query)
    conn.commit()

    # Insert the top usernames into the table
    insert_query = '''
    INSERT INTO high_rated_unames (username, score) VALUES (%s, %s)
    '''
    cursor.executemany(insert_query, top_usernames)
    conn.commit()

    print(f"\nInserted top {no_of_sorted} high scoring usernames into the database (high_rated_unames).")
    time.sleep(1.33)

    # Close the database connection
    cursor.close()
    conn.close()


########################
## Main Script Starts ##
## Generate usernames in Step 3 logic ##
########################

if __name__ == "__main__":

    # Provide Number of Raw usernames to score and limit number for sorted high scoring usernames to be stored & used.
    generate_usernames_with_AI_Scoring_agents(50,7)

    # Query Database for AI results#
    interrogate_scoring_table()

