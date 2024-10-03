# AI-Driven Username and Email Generation, Scoring, and Validation System

## Overview

This project is an advanced system designed to **generate, score, and validate usernames and email patterns** using a combination of **AI techniques, neural networks, and external validation tools**. The core functionality revolves around creating realistic email-like usernames, rating them for authenticity using multiple AI agents, and then verifying their plausibility by checking for real-world web presence.

The system can be utilized to understand AI-driven pattern recognition and text analysis techniques, with potential applications in educational research, user validation, and secure system implementations.

### Key Features:
- **Dataset Generation**: Automatically process and clean datasets of words, names, and nicknames using libraries such as NLTK and LangDetect.
- **Data Categorization**: Efficiently categorize input data into distinct tables for names and words.
- **Email Pattern Generation**: Create email-like patterns by combining elements such as names, words, numbers, and years with controlled randomness and separators.
- **AI Scoring**: Use multiple AI agents to evaluate the likelihood of generated usernames being plausible.
- **Web Validation**: Validate the top-scoring usernames by performing a web search and confirming their presence in real-world content.
- **User Data Integration**: Allow users to upload their own datasets to further enhance or customize the email generation process.

---

## Installation

To install and run this project on your local machine, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/repository-name.git
   cd repository-name

2. Set up a virtual environment (optional but recommended):
python -m venv env
source env/bin/activate  # For Linux/macOS
env\Scripts\activate      # For Windows

3. Install the required dependencies:
pip install -r requirements.txt

4. Set up your environment variables:
Create a .env file in the root directory and add the following:
API_KEY=your-google-api-key
SEARCH_ENGINE_ID=your-search-engine-id

5. Set up your MariaDB database:
Make sure you have MariaDB installed and set up. Create the necessary database and tables by running the provided SQL 
scripts or using the code provided in the project.

## Usage
1. Run the main script to generate usernames, score them, and validate them through web scraping:

2. Customize the process by uploading your own datasets:

3. Upload files into the User Upload directory and run the script with appropriate flags to use your custom data in the username generation process.
Final Processing: After generating and validating the usernames, you can review the results stored in the MariaDB tables for further analysis or use.


## Project Workflow
Step 1: Dataset Creation and Storage
The project begins by generating a dataset of words using NLTK and LangDetect. These words are cleaned and categorized, filtering out offensive or irrelevant content. The cleaned data is stored in the email_generation database, under the words and names tables.

Step 2: Data Cleaning and Categorization
The raw dataset is further processed, splitting the data into names/nicknames and other words. This structured dataset is stored in MariaDB for use in the next step.

Step 3: Email Pattern Generation
Using a controlled randomization approach, the project generates email-like patterns by combining elements from the dataset (names, words, numbers). A Neural Network model rates the plausibility of the generated patterns to identify the most realistic ones.

Step 4: AI-Driven Scoring
The generated email patterns are scored using multiple AI agents, which evaluate the likelihood of a username being real based on pattern analysis. The highest-scoring usernames are stored in the database for future analysis.

Step 5: Web Scraping for Validation
Top AI-scored usernames are validated by performing a Google search to check for real-world web presence. Valid usernames that appear in search results are stored in the final production table.

Step 6: User Input and Final Processing
Users can upload their own datasets or adjust the email generation process. The system generates final high-probability usernames that have been both AI-scored and web-validated.


## Ethical Use of the Algorithm
The purpose of this project is to explore the possibilities of AI-driven email and username generation, validation, and scoring. It is designed to be used for ethical, educational, and constructive purposes only.

## Examples of appropriate uses include:

Educational purposes: Learning how AI models can be applied in the context of email pattern generation and validation.
Validating usernames for secure systems: Ensuring usernames follow certain naming conventions for enhanced security.
Research and Development: Testing and developing more accurate models for AI-driven text and pattern recognition.
However, it is crucial to understand that this algorithm must not be used for unethical activities such as spamming, phishing, harvesting personal data, or infringing on others' privacy. The techniques demonstrated in this project should never be employed to deceive individuals or engage in activities that could cause harm or violate ethical standards.

This project is a tool—its responsible use lies entirely in the hands of the user. We strongly encourage all users to respect privacy laws, data protection regulations, security policies, and ethical guidelines when using this tool.


## Contributing
Contributions are welcome! If you'd like to contribute to this project