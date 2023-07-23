from sentence_transformers import SentenceTransformer, util
from dict_keywords import keywords 
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


with open('links_and_captions.txt', 'r', encoding='utf8') as f:
    lines = f.readlines()


jobs = [{'link': lines[i].strip(), 'caption': lines[i+1].strip() if i+1 < len(lines) else ""} for i in range(0, len(lines), 2)]

model = SentenceTransformer('all-MiniLM-L6-v2')

job_descriptions = [job['caption'] for job in jobs]

job_vectors = model.encode(job_descriptions, convert_to_tensor=True)

returned_job_indices = []
context = ""
last_query = ""

def search_jobs(query):
    global last_query
    cos_similarity_threshold = 0.3
    query_words = set(query.upper().split())
    keyword_keys = [key for key in keywords if key in query_words]
    
    for key in keyword_keys:
        query += " " + " ".join(keywords[key])

    query_vector = model.encode(query, convert_to_tensor=True)
    cos_similarities = util.pytorch_cos_sim(query_vector, job_vectors)
    cos_similarities_list = cos_similarities.tolist()[0]

    for index in returned_job_indices:
        if index < len(cos_similarities_list):
            cos_similarities_list[index] = -1

    if len(returned_job_indices) >= len(cos_similarities_list):
        return None

    max_cos_similarity = max(cos_similarities_list)
    if max_cos_similarity < cos_similarity_threshold:
        return None  

    top_job_index = cos_similarities_list.index(max_cos_similarity)
    returned_job_indices.append(top_job_index)
    return jobs[top_job_index]


def generate_response(query):
    global context, last_query, returned_job_indices

    if query.lower() == "get started":
        context = "asked_for_job_details"
        last_query = ""
        returned_job_indices = []
        return "Could you please provide details about the type of job or internship you're looking for?"

    elif context == "asked_for_job_details":
        if query.lower() == 'next':
            if len(returned_job_indices) < len(jobs):
                job = search_jobs(last_query)  
                if job is not None:  
                    job['link'] = job['link'].replace('Link: ', '')
                    return f"I found a job that might match your query!<br/><br/>Please visit this link: <a href='{job['link']}'>{job['link']}</a><br/><br/>Please indicate your next step by typing one of the following options:<br/><b>Yes</b> if this job meets your expectations and you don't need to explore other options.<br/><b>Next</b> if you want to view another job based on your initial preferences.<br/><b>Refine</b> if you'd like to add more specific criteria to better suit your job search.<br/><b>Restart</b> if you prefer to begin a new search for a different job role."
                else:
                    context = ""
                    last_query = ""
                    return "I'm sorry, I couldn't find any more jobs that match your query. Type 'Get started' to begin."
            else:
                context = ""
                last_query = ""
                return "I'm sorry, I couldn't find any more jobs that match your query. Type 'Get started' to begin."
        elif query.lower() == 'yes':
            context = ""
            last_query = ""
            return "Great! If you need more assistance, type 'Get started'."
        

        elif query.lower() == 'refine':
            context = "refine_search"
            return "Please provide additional details to refine your job search."
        elif query.lower() == 'restart':
            context = ""
            last_query = ""
            return "Let's start a new search. Type 'Get started' to begin."
        else:
            last_query = query
            job = search_jobs(last_query)
            if job is not None:
                context = "asked_for_job_details"
                job['link'] = job['link'].replace('Link: ', '')
                return f"I found a job that might match your query!<br/><br/>Please visit this link: <a href='{job['link']}'>{job['link']}</a><br/><br/>Please indicate your next step by typing one of the following options:<br/><b>Yes</b> if this job meets your expectations and you don't need to explore other options.<br/><b>Next</b> if you want to view another job based on your initial preferences.<br/><b>Refine</b> if you'd like to add more specific criteria to better suit your job search.<br/><b>Restart</b> if you prefer to begin a new search for a different job role."
            else:
                context = "asked_for_job_details"
                return "I'm sorry, I couldn't find any jobs that match your query. Type 'restart' to begin a new search" 
            

    elif context == "refine_search":
        last_query += " " + query
        job = search_jobs(last_query)
        if job is not None:
            context = "asked_for_job_details"
            job['link'] = job['link'].replace('Link: ', '')
            return f"I found a job that might match your query!<br/><br/>Please visit this link: <a href='{job['link']}'>{job['link']}</a><br/><br/>Please indicate your next step by typing one of the following options:<br/><b>Yes</b> if this job meets your expectations and you don't need to explore other options.<br/><b>Next</b> if you want to view another job based on your initial preferences.<br/><b>Refine</b> if you'd like to add more specific criteria to better suit your job search.<br/><b>Restart</b> if you prefer to begin a new search for a different job role."
        else:
            context = "refine_search"
            return "I'm sorry, I couldn't find any jobs that match your new criteria. Could you please provide more details to refine your job search?"

    
    else:
        context = ""
        return "Type 'Get started' to begin."

@app.route('/api/ask', methods=['POST'])
def ask():
    x = request.get_json()
    response = generate_response(str(x['prompt']))
    return jsonify(str(response))

if __name__ == '__main__':
    app.run(debug=True)