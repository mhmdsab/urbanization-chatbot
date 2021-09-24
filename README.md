# urbanization-chatbot

Demo chatbot that is cabaple of obtaining the capital and population for some countries.

The chatbot covers the following intents:

1- greeting

2- goodbye

3- Check Capital with the following steps:

- Select Country

- Display capital of that country

4. Check Population with the following steps:

- Select Country

- Display the population of that country.

The chatbot handles fallback scenario as follows:
- if a message of unknown intent is sent, the chatbot will respond with fallback answer.
- if the chatbot failed to identify the intent for 3 successive times, it will respond with quick replies of the services provided.

The chatbot handles API call failure scenarios.


# How to set up

To set up the chatbot follow the steps below:

1- clone the repo

2- head inside the repo folder and open the terminal

3- run "pip install -r requirements.txt"

4- run "pip install "rasa-x==0.40.0 --extra-index-url https://pypi.rasa.com/simple"

5- run "python -m spacy download en_core_web_md"

6- run rasa x

7- in another terminal run rasa run actions





