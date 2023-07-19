
import nltk
import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Download necessary NLTK corpora if not already downloaded
nltk.download('punkt')
nltk.download('stopwords')

def clean_text(text):
    # Convert text to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Tokenize: Split the sentence into words
    word_tokens = word_tokenize(text)

    # Remove stopwords
    filtered_text = [word for word in word_tokens if word not in stopwords.words('english')]
    
    return filtered_text

# Example usage:

# Define the text
text = """
[SALES INTERNS] [PRODUCT DEVELOPMENT AND DESIGN INTERNS]
We are looking for interns! 
Join the Jacinto & Lirio Team in our mission to solve the water hyacinth problem! 
Jacinto & Lirio provides beautifully handcrafted plant leather goods which are impressively multi-functional yet stylish conversational pieces with a lifestyle appeal for professionals and companies who want to create a strong patriotic, environmental, and socio-ethical statement. More details about the company can be found at www.jacintoandlirio.com 
Internship Duration Range: 
Apprentice: 3 Months (480-576 hours) 
Team Leader Intern: 6 Months (960 hours) 
Senior Core Intern: 1 Year or more 
Sales Intern 
Job Description: 
- In charge of securing promotional giveaways to clients, wedding giveaways customers, and reseller for the company 
- Responsible for researching and identifying sales opportunities and generating leads 
- Maintaining relationships with all potential and existing clients by providing support, information, and guidance 
- Ensuring proper servicing and after-sales support to clients 
- Form Partnerships 
- Generating monthly actions to meet sales targets 
- Customer relationship management 
Product Development and Design Intern 
Job Description: 
- Market and Product Research (Local & International) 
- Product Proposal 
- Design Process 
NOTES: 
No internship allowances but sales commissions will be given for sales roles 
Work From Home (WFH) 
8 hours/day, Monday-Saturday (flexible and can be adjusted according to class schedule) 
You can also message me for inquiries or concerns. Interested applicants may send their resume and/or portfolio, top 2 desired positions, and internship duration: 
TO: jacintoandliriohrinternteam@gmail.com 
CC: jacintoandlirioteam@jacintoandlirio.com 
SUBJECT: <Last Name, First Name>_J&L Internship Application 
"""
print(clean_text(text))
