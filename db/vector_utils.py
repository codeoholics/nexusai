
import torch

# import nltk
# from nltk.corpus import stopwords
# from nltk.stem import WordNetLemmatizer
import string
from transformers import DistilBertTokenizer, DistilBertModel

import aiclients.openai_client

# Load DistilBERT model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertModel.from_pretrained('distilbert-base-uncased')
from shared import logger

log = logger.get_logger(__name__)

# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

# def preprocess_text(text):
#     # Lowercasing
#     text = text.lower()
#
#     # Removing punctuation
#     text = text.translate(str.maketrans('', '', string.punctuation))
#
#     # Tokenization
#     tokens = nltk.word_tokenize(text)
#
#     # Removing stopwords
#     stop_words = set(stopwords.words('english'))
#     tokens = [word for word in tokens if word not in stop_words]
#
#     # Lemmatization
#     lemmatizer = WordNetLemmatizer()
#     tokens = [lemmatizer.lemmatize(word) for word in tokens]
#
#     return ' '.join(tokens)
#
def clean_string(input_string):
    # Convert the string to lowercase
    input_string = input_string.lower()

    # Define the set of allowed characters (for example, alphanumeric and some punctuation)
    allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789 .,!?')

    # Use a list comprehension to filter out unwanted characters
    filtered_string = ''.join(char for char in input_string if char in allowed_chars)
    log.info(len(input_string))

    return input_string
def string_to_vector(tag):
    tag = clean_string(tag)
    inputs = tokenizer(tag, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        output = model(**inputs)
    vector_list = output.last_hidden_state[0][0].numpy().tolist()  # Convert numpy array to list
    return vector_list
def string_to_vectorol(tag):
    tag = clean_string(tag)
    result = aiclients.openai_client.create_openai_embedding(tag)
    return result[0]
