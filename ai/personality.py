import requests
import pandas as pd
import random
from keys import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# DATASET STUFF
file_path = r'db\datasetai.csv'
data = pd.read_csv(file_path)

def preprocess_data(df):
    return df[['Personality', 'Catchphrase', 'Favorite Saying', 'Style 1', 'Style 2']]
preprocessed_data = preprocess_data(data)

def find_personality(user_description, data):
    vectorizer = TfidfVectorizer()
    combined_texts = data['Personality'].tolist() + [user_description]
    tfidf_matrix = vectorizer.fit_transform(combined_texts)
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    closest_index = cosine_sim.argmax()
    return data.iloc[closest_index]['Personality']

def fav_saying(personality, data):
    phrase = data[data['Personality'] == personality]['Favorite Saying'].tolist()
    return random.choice(phrase)

#MODEL
pet_model = "@hf/mistral/mistral-7b-instruct-v0.2"
API_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{count_id}/ai/run/"

def run(model, inputs):
    headers = {"Authorization": workers_key}
    input_data = {
        "messages": inputs,
        "temperature": .9,  # creativity
        "max_tokens": 30
    }
    try:
        response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input_data)
        response.raise_for_status()
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

print(" Legend has it that many years ago, humans were born with their own companion creature to accompany them on their journey through life; as humans care for it, the creature grows. What is the personality of your dream companion? (Describe it: personality, etc.)")
user_pet = (str(input()))
name = (str(input("Name: ")))

match = find_personality(user_pet, preprocessed_data)
fav_phrase = fav_saying(match, preprocessed_data)
user_pet = user_pet + fav_phrase

my_prompt = f"Act as if you are the pet with the personality: {match}. Your name is {name}. Do not mention that you are an AI or that you are not real. Simply respond as if youve just been born. Keep your response within 30 tokens and complete your sentence."

inputs = [
    { "role": "system", "content": f"{my_prompt}" },
    { "role": "user", "content": f"{user_pet}" }
]
output = run(pet_model, inputs)
