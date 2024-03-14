from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

app = Flask(__name__)


data = pd.read_csv("./dataset.csv")

# Vectorize the text data
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(data["phrase"])

# Function to preprocess the text
def preprocess_text(text):
    return text.lower()

# Preprocess the text data
data["processed_phrase"] = data["phrase"].apply(preprocess_text)

# Update the vectorizer with the preprocessed text data
tfidf_matrix = vectorizer.fit_transform(data["processed_phrase"])

# Store conversation state globally
conversation_state = {}

# Function to get response from the chatbot
def get_response(input_text):
    input_text = preprocess_text(input_text)
    input_vector = vectorizer.transform([input_text])
    similarities = cosine_similarity(input_vector, tfidf_matrix)
    max_similarity_index = similarities.argmax()
    response = data.iloc[max_similarity_index]["prompt"]
    return response

# Function to get precaution advice based on prompt
def get_precaution(prompt):
    advice = data[data["prompt"] == prompt]["precaution"].tolist()
    return random.choice(advice) if advice else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_state

    user_input = request.form['user_input']

    # Check if the user input is empty
    if not user_input.strip():
        response_data = {
            "bot_response": "Bot: It seems like you didn't provide any information. Please enter your symptoms or concerns.",
            "prompt": None,
            "asking_for_advice": False
        }
        return jsonify(response_data)

    prompt = get_response(user_input)

    if prompt and conversation_state.get('asking_for_advice', False):
        conversation_state['asking_for_advice'] = False
        response_data = {
            "bot_response": f"Bot: It sounds like you're experiencing {prompt}.",
            "prompt": prompt,
            "asking_for_advice": True
        }
        return jsonify(response_data)
    elif prompt:
        conversation_state['asking_for_advice'] = True
        response_data = {
            "bot_response": f"Bot: It sounds like you're experiencing {prompt}.",
            "prompt": prompt,
            "asking_for_advice": True
        }
        return jsonify(response_data)
    else:
        conversation_state = {}  # Reset the conversation state if no prompt is found
        response_data = {
            "bot_response": "Bot: It seems like I couldn't identify the specific issue. If you have any health concerns, please consult with a healthcare professional. Have a happy and healthy day!",
            "prompt": None,
            "asking_for_advice": False
        }
        return jsonify(response_data)

@app.route('/get_precaution', methods=['POST'])
def get_precaution_route():
    try:
        prompt = request.json['prompt']
        print(prompt)
        advice = get_precaution(prompt)
        if advice is not None:
            precaution_data = {
                "precaution": advice
            }
            return jsonify(precaution_data)
        else:
            return jsonify({"error": "No advice available for the given prompt."})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
