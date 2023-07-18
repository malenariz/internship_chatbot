from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import json
import spacy
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

nlp = spacy.load("en_core_web_sm")

# Load your data
with open('jsonvalidator.json', 'r') as f:
    data = json.load(f)

# Convert data to a DataFrame
df = pd.json_normalize(data)

# Set up the chatbot
chatbot = ChatBot('InternshipChatBot')
trainer = ListTrainer(chatbot)

conversation = [
    "Hello, how can I assist you today?",
    "I'm looking for an internship.",
    "Can you tell me more about the field and location you're interested in?",
    "I'm searching for a job.",
    "What type of job are you interested in and where?",
    "I need a position in software development.",
    "Are there any specific companies or types of companies you're interested in?",
    "What career opportunities do you have?",
    "Could you provide more details about the type of opportunities you're interested in?",
    "I'm looking for work.",
    "Can you provide more details such as the field of work and your preferred location?",
    "I want an opportunity in data science.",
    "Do you have a preference for the type of company or job location?"
    # ... continue to add more statements based on your requirement
]
trainer.train(conversation)
# Load the BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create a list of all job descriptions
job_descriptions = df['description'].tolist()

# Convert the job descriptions to vectors
job_vectors = model.encode(job_descriptions, convert_to_tensor=True)

context = ""

def search_jobs(query):
    # Convert the query to a vector
    query_vector = model.encode(query, convert_to_tensor=True)

    # Convert values to a NumPy array
    values = np.array(job_vectors)

    # Compute cosine similarities between the query and all job descriptions
    cos_similarities = util.pytorch_cos_sim(query_vector, job_vectors)[0]

    threshold = 0.3
    # Get the job with the highest similarity score
    top_similarity = cos_similarities.max().item()

       # Check if the top_job_index is within the range of the DataFrame
    if top_similarity > threshold:
        top_job_index = cos_similarities.argmax()
        if top_job_index < len(df):
            job = df.values[top_job_index]
            job_description = job[0]
            company_name = job[1]
            responsibilities = job[2]
            salary = job[3]
            link = job[4]

            return {
                'description': job_description,
                'company_name': company_name,
                'responsibilities': responsibilities,
                'salary': salary,
                'link': link
            }
    # If the similarity score is below the threshold, return None
    return None


def generate_response(query):
    global context
    doc = nlp(query)

    entities = [str(ent).lower() for ent in doc.ents]  
    keywords = ["job", "internship", "work", "career", "opportunity", "role","duty","occupation","position","responsibility"]

    if context == "asked_for_job_details":
        job = search_jobs(query)
        if job is not None:
            context = ""
            return f"I found a job that might match your query: {job['description']} at {job['company_name']}. The responsibilities include: {job['responsibilities']}. The salary is {job['salary']}. For more details, please visit {job['link']}."
        else:
            return "I'm sorry, I couldn't find any jobs that match your query. Could you please provide more details about the type of job or internship you're looking for?"

    elif any(word in query.lower() for word in keywords) or entities:
        context = "asked_for_job_details"
        return "Could you please provide more details about the type of job or internship you're looking for?"

    else:
        return chatbot.get_response(query)

@app.route('/api/ask', methods=['POST'])
def ask():
    x = request.get_json()
    response = generate_response(str(x['prompt']))
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)