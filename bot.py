import os
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# এনভায়রনমেন্ট থেকে টোকেন নিন (কোডে টোকেন লিখবেন না)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ইমেইল জেনারেট ফাংশন
async def gen_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1").json()
    email = response[0]
    # ইউজার ডেটাতে ইমেইল সেভ করে রাখুন
    context.user_data['email'] = email
    await update.message.reply_text(f"আপনার অস্থায়ী ইমেইল: `{email}`\n\nইমেইলটি কপি করতে ট্যাপ করুন।\n\nইনবক্স চেক করতে লিখুন: /check", parse_mode='Markdown')

# ইনবক্স চেক ফাংশন
async def check_inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = context.user_data.get('email')
    if not email:
        await update.message.reply_text("আগে /genemail দিয়ে একটি ইমেইল তৈরি করুন।")
        return
    
    login, domain = email.split('@')
    url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
    messages = requests.get(url).json()

    if not messages:
        await update.message.reply_text("আপনার ইনবক্সে কোনো নতুন মেসেজ নেই।")
    else:
        for msg in messages:
            await update.message.reply_text(f"Sender: {msg['from']}\nSubject: {msg['subject']}\nID: {msg['id']}")

# রেন্ডার সচল রাখার জন্য ওয়েব সার্ভার
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # ওয়েব সার্ভার চালু করুন
    Thread(target=run).start()
    
    # বট স্টার্ট করুন
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('genemail', gen_email))
    application.add_handler(CommandHandler('check', check_inbox))
    
    application.run_polling()
