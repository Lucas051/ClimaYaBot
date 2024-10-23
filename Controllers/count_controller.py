from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
  
async def show_count_menu(update: Update, user_state):
     chat_id = update.callback_query.message.chat.id
    
     if "count" not in user_state[chat_id]:
        user_state[chat_id]["count"] = 0 
         
     await update.callback_query.message.reply_text(
            f'Contador: {user_state[chat_id]["count"]}\n• Escribe un mensaje para seguir contando.\n• Escribe /exit para salir al menú.',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Resetear Conteo", callback_data="reset_count")],
            ]))

async def count_messages(update: Update, user_state):
    chat_id = update.message.chat_id
    
    user_state[chat_id]["count"] += 1
    await update.message.reply_text(f'Contador: {user_state[chat_id]["count"]}')
        


