from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from sentence_transformers import SentenceTransformer, util
import spacy
import torch
from dict_keywords import keywords 

nlp = spacy.load("en_core_web_sm")

# Load your data
with open('links_and_captions.txt', 'r', encoding='utf8') as f:
    lines = f.readlines()

# Each job is represented by two lines: link and caption
jobs = [{'link': lines[i].strip(), 'caption': lines[i+1].strip() if i+1 < len(lines) else ""} for i in range(0, len(lines), 2)]


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
job_descriptions = [job['caption'] for job in jobs]

# Convert the job descriptions to vectors
job_vectors = model.encode(job_descriptions, convert_to_tensor=True)

returned_job_indices = []
context = ""
last_query = ""

def search_jobs(query):
    global last_query

    # Determine which, if any, keys from your dictionary are in the query
    query_words = set(query.upper().split())  # This assumes that the query is a single string of words separated by spaces
    keyword_keys = [key for key in keywords if key in query_words]
    
    # Add the additional keywords associated with the found keys
    for key in keyword_keys:
        query += " " + " ".join(keywords[key])

    last_query = query

    # Convert the query to a vector
    query_vector = model.encode(query, convert_to_tensor=True)

    # Compute cosine similarities between the query and all job descriptions
    cos_similarities = util.pytorch_cos_sim(query_vector, job_vectors)

    # Convert the cos_similarities tensor to a Python list
    cos_similarities_list = cos_similarities.tolist()[0]

    # Set the similarities of the jobs we've already returned to -1
    for index in returned_job_indices:
        if index < len(cos_similarities_list):
            cos_similarities_list[index] = -1

    # Check if we have any jobs left to suggest
    if len(returned_job_indices) >= len(cos_similarities_list):
        return None

    # Get the top job with the highest similarity score
    top_job_index = cos_similarities_list.index(max(cos_similarities_list))

    # Remember this index so we don't return this job again
    returned_job_indices.append(top_job_index)

    return jobs[top_job_index]


def generate_response(query):
    global context, last_query
    doc = nlp(query)

    entities = [str(ent).lower() for ent in doc.ents]
    keywords = ["job", "internship", "work", "career", "opportunity", "role","duty","occupation","position","responsibility"]

    if context == "asked_for_job_details":
        if 'no' in query.lower():
            if len(returned_job_indices) < len(jobs):
                job = search_jobs(last_query)  # Use the last query instead of the current one
                if job is not None:  # Check if job is None
                    return f"I found another job that might match your query! Please visit this link: {job['link']}\n\nPlease indicate your next step by typing one of the following options:\n\nYes if this job meets your expectations and you don't need to explore other options.\nNo if you want to view another job based on your initial preferences.\nRefine if you'd like to add more specific criteria to better suit your job search.\nRestart if you prefer to begin a new search for a different job role."
                else:
                    context = ""
                    return "I'm sorry, I couldn't find any more jobs that match your query."
            else:
                return "I'm sorry, I couldn't find any more jobs that match your query."
        elif 'yes' in query.lower():
            context = ""
            return "Great! If you need more assistance, type 'Get started'."
        elif 'refine' in query.lower():
            context = "refine_search"
            return "Please provide additional details to refine your job search."
        elif 'restart' in query.lower():
            context = ""
            returned_job_indices.clear()
            last_query = ""
            return "Let's start a new search. Type 'Get started' to begin."
        else:
            job = search_jobs(query)
            if job is not None:
                context = "asked_for_job_details"
                return f"I found a job that might match your query! Please visit this link: {job['link']}\n\nPlease indicate your next step by typing one of the following options:\n\nYes if this job meets your expectations and you don't need to explore other options.\nNo if you want to view another job based on your initial preferences.\nRefine if you'd like to add more specific criteria to better suit your job search.\nRestart if you prefer to begin a new search for a different job role."
            else:
                context = "asked_for_job_details"
                return "I'm sorry, I couldn't find any jobs that match your query. Could you please provide more details about the type of job or internship you're looking for?" 

    elif context == "refine_search":
        last_query += " " + query
        job = search_jobs(last_query)
        if job is not None:
            context = "asked_for_job_details"
            return f"I found a job that might match your query! Please visit this link: {job['link']}\n\nPlease indicate your next step by typing one of the following options:\n\nYes if this job meets your expectations and you don't need to explore other options.\nNo if you want to view another job based on your initial preferences.\nRefine if you'd like to add more specific criteria to better suit your job search.\nRestart if you prefer to begin a new search for a different job role."
        else:
            context = "refine_search"
            return "I'm sorry, I couldn't find any jobs that match your new criteria. Could you please provide more details to refine your job search?"

    elif query.lower() == "get started":
        context = "asked_for_job_details"
        return "Could you please provide details about the type of job or internship you're looking for?"

    else:
        # When the query is not related to a job search, use ChatterBot to generate a response.
        context = ""
        return "Type 'Get started' to begin."

        


print("Hello! I am Aids. I can help you find jobs and internships. How can I assist you today?")

while True:
    query = input()
    response = generate_response(query)
    print(response)