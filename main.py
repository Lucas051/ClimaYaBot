from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

from Controllers.count_controller import count_messages, show_count_menu
from Controllers.weather_controller import ask_for_city, send_weather, handle_additional_question

load_dotenv()

user_state = {}

# Initialize the state of a new user
def initialize_user_state(chat_id):
   if chat_id not in user_state: 
        user_state[chat_id] = {
            "state": "/start",  
            "weather_report": None,  
            "count": 0 
        }

# Main Menu
async def show_menu(update: Update, ):
    chat_id = update.message.chat_id
    
    if chat_id not in user_state:
        initialize_user_state(chat_id)
        
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="☀️ Quisiera saber sobre el clima ❄️", callback_data="weather")],
        [InlineKeyboardButton(text="🔢 Quisiera contar cada vez que te escribo 🔢", callback_data="count")],
    ])
    await update.message.reply_text('Elige una opción 👇', reply_markup=keyboard)

# /exit count mode
async def exit_to_menu(update: Update):
    chat_id = update.message.chat_id

    user_state[chat_id]["state"] = "/start"  
    
    await update.message.reply_text("Has salido del modo de conteo 👋")
    await show_menu(update, )

# /exit weather mode
async def exit_from_weather(update: Update):
    initialize_user_state(update.message.chat_id) 
    await update.message.reply_text("Está bien, si necesitas algo más, solo pregúntame! 😁")
    await show_menu(update, )

# Button Controller
async def button_controller(update: Update):
    query = update.callback_query.data
    chat_id = update.callback_query.message.chat_id

    initialize_user_state(chat_id)
    await update.callback_query.answer()

    if query == "weather":
        user_state[chat_id]["state"] = "weather"  # Change state to "weather"
        await ask_for_city(update, )

    elif query == "count":
        user_state[chat_id]["state"] = "count"  # Change state to "count"
        await show_count_menu(update, user_state)

    elif query == "reset_count":
        user_state[chat_id]["count"] = 0 
        await update.callback_query.message.reply_text(f'Contador reseteado a {user_state[chat_id]["count"]} ✅')
        await show_count_menu(update, user_state)


# Message Handler
async def message_handler(update: Update):
    chat_id = update.message.chat_id
    if user_state[chat_id]["state"]  == "count":
        await count_messages(update, user_state)
        
    elif user_state[chat_id]["state"]  == "weather":
        await send_weather(update, user_state)  
        
    elif user_state[chat_id]["state"]  == "ask_more":
        await handle_additional_question(update, user_state) 
        
    else:
        await update.message.reply_text("Por favor elige una opción primero usando /start.")

        
telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = ApplicationBuilder().token(telegram_token).build()

# Handlers
bot.add_handler(CommandHandler("start", show_menu))
bot.add_handler(CommandHandler("exit", exit_to_menu))
bot.add_handler(CommandHandler("no", exit_from_weather))
bot.add_handler(CallbackQueryHandler(button_controller))
bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

bot.run_polling()
