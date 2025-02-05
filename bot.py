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
    
async def date(update, context):
    dialog.mode = "date"
    msg = load_message("date")
    await send_photo(update, context, "date")
    
    await send_text_buttons(update, context, msg, {
        "date_grande": "Ariana Grande",
        "date_robbie": "Margot Robbie",
        "date_zendaya": "Zendaya",
        "date_gosling": "Ryan Gosling",
        "date_hardy": "Tom Hardy",
    })
    

async def date_button(update, context):
    query = update.callback_query.data    
    await update.callback_query.answer()
    await send_photo(update, context, query)
    await send_text(update, context, "Good Choise.\uD83D\uDE05 Your task is to invite a girl or a boy for dating using 5 messages! \U00002764")
    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)
    
async def date_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "Набирає повідомлення...")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)
    #await send_text(update, context, answer)
    
async def message(update, context):
    dialog.mode = "message"
    msg = load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, msg, {
        "message_next": "Написати повідомлення",
        "message_date": "Запросити на побачення"
        
    })
    
    dialog.list.clear()    
    
    
async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)

async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    
    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)
    
    my_message  = await send_text(update, context, "Думаю над варіантами...")
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)
    
    
async def hello(update, context):
    #await send_text(update, context, "Hi, user! " + update.message.text)
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)    
    elif dialog.mode == "message":
        await message_dialog(update, context)
    
    
    
dialog = Dialog()
dialog.mode = None
dialog.list = []

chatgpt = ChatGptService(token=OPEN_AI_TOKEN)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CallbackQueryHandler(date_button, pattern="^date_."))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_."))

app.run_polling()
