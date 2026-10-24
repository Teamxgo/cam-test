import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Your Bot Token from BotFather
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8928916946:AAEYVCHLdoVB-l0svDNHInRmc25myCz8pnw')
WEB_URL = "https://teamxgo.github.io/cam-test/"

@app.route('/')
def home():
    return "Telegram Bot Backend is Live!"

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.json
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        
        if text == '/start':
            # When you type /start, the bot sends your camera link with your chat ID attached!
            link = f"{WEB_URL}?chat_id={chat_id}"
            send_message(chat_id, f"🔗 **Your Live Stream Link:**\n{link}\n\nOpen this link in your phone browser to start streaming.")
        elif text == '/status':
            send_message(chat_id, "🟢 Bot server is active and online.")
            
    return 'OK', 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
