from dotenv import load_dotenv
import os

from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPEN_AI_TOKEN = os.getenv("OPEN_AI_TOKEN")
if not TOKEN:
    raise ValueError("Telegram Bot Token is missing. Check your .env file.")
if not OPEN_AI_TOKEN:
    raise ValueError("Open AI token is missing. Check your .env file.")


# тут будемо писати наш код :)

async def start(update, context):    
    msg = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, msg)
    await show_main_menu(update, context, {
        "start": "Main menu",
        "profile": "Generate Tinder-profile \uD83D\uDE0E",
        "opener": "Message for acquaintance \uD83E\uDD70",
        "message": "Texting on your behalf \uD83D\uDE08",
        "date": "Chatting with the stars \uD83D\uDD25",
        "gpt": "Ask a question to ChatGPT \uD83E\uDDE0",
    })
    
async def gpt(update, context):
    dialog.mode = "gpt"
    await send_photo(update, context, "gpt")
    msg = load_message("gpt")
    await send_text(update, context, msg)
    
async def gpt_dialog(update, context):
    text = update.message.text
    prompt = load_prompt("gpt")
    answer = await chatgpt.send_question(prompt, text)
    await send_text(update, context, answer)
    
async def hello(update, context):
    #await send_text(update, context, "Hi, user! " + update.message.text)
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    #await send_text_buttons(update, context, "Hi, user! " + update.message.text, {"start":"START", "stop":"STOP"})
    
# async def buttons_handler(update, context):
#     query = update.callback_query.data
#     if query == "start":
#         await send_text(update, context, "Started")
#     elif query == "stop":
#         await send_text(update, context, "Stopped")
    
    
dialog = Dialog()
dialog.mode = None

chatgpt = ChatGptService(token=OPEN_AI_TOKEN)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
#app.add_handler(CallbackQueryHandler(buttons_handler))
app.run_polling()
