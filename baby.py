import sys, io, os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


GEMINI_API_KEY = os.environ.get("AIzaSyD6h0rXgIJATZvbbFzinI1XQfw2e8FbOxg")


genai.configure(api_key=GEMINI_API_KEY)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
model = genai.GenerativeModel('models/gemini-flash-latest', safety_settings=safety_settings)
chat_sessions = {}
app = Flask(__name__)


@app.route("/webhook", methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    print(f"Message from {sender_number}: {incoming_msg}")

    if sender_number not in chat_sessions:
        chat_sessions[sender_number] = model.start_chat(history=[])

    chat = chat_sessions[sender_number]

    try:
        if len(chat.history) == 0:
            system_prompt = """ඔයා MUFAZOO AI GOST.you ane girl. Owner King dinu and sajii. User ට 'boos'කියන්න.
            සිංහලෙන් ගැමි Style එකට Fun විදියට කෙටියෙන් උත්තර දෙන්න. 👑🔥 දාන්න."""
            response = chat.send_message(f"{system_prompt}\n\nUser: {incoming_msg}")
        else:
            response = chat.send_message(incoming_msg)

        reply_text = ""
        if response.candidates and response.candidates[0].content.parts:
            reply_text = response.candidates[0].content.parts[0].text
        if not reply_text.strip():
            reply_text = "අඩෝ King, මොකක්ද කිව්වේ? 😅"

    except Exception as e:
        print(f"Error: {e}")
        reply_text = "අඩෝ King, මොළේ පොඩ්ඩක් එරර් 😅"

    print(f"Replying: {reply_text}")
    twiml = MessagingResponse()
    twiml.message(reply_text)
    return str(twiml), 200, {'Content-Type': 'text/xml; charset=utf-8'}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
