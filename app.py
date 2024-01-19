import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session

from helper.bot import ConversationalQA


load_dotenv()
conversational_qa = ConversationalQA()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route('/api/conversation', methods=['GET', 'POST'])
def conversation():
    if 'conversations' not in session:
        session['conversations'] = {}
    if request.method == 'POST':
        question = request.form.get('question')
        response = conversational_qa.conversation({
            "question": question,
            "chat_history": session['conversations']
        })
        session['conversations'][question] = response['answer']
    return jsonify(response['answer'])

@app.route('/api/clear', methods=['POST'])
def clear():
    session.clear()
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)