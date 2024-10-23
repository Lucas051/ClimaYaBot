from telegram import Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv
from logger import logger

import requests
import os
import openai

load_dotenv()

weather_api_key = os.getenv('WEATHER_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

# Get coordinates using Geocoding API
async def get_coordinates(city_name: str):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={weather_api_key}"
    response = requests.get(url).json()
    
    if response:
        city_info = response[0]
        return city_info['lat'], city_info['lon']
    return None, None

# Get city weather
async def get_weather(city_name: str):
    lat, lon = await get_coordinates(city_name)
    if lat is None or lon is None:
        return "Ciudad no encontrada 🤔 Vuelve a Intentarlo."

    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric&lang=es"
    weather_data = requests.get(weather_url).json()

    if 'main' in weather_data:
        temp = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        min = weather_data['main']['temp_min']
        max = weather_data['main']['temp_max']
        pressure = weather_data['main']['pressure']
        humidity = weather_data['main']['humidity']
        
        return f"Actualmente {city_name} tiene una temperatura de {temp}°C con {description}.\nCon temperaturas mínimas de: {min}°C\nCon temperaturas máximas de: {max}°C\nLa presión atmosférica: {pressure}hPa\nHumedad: {humidity}%\nQue tengas un buen día! 👋"
    else:
        return "No se pudo obtener el clima."

async def ask_for_city(update: Update):
    await update.callback_query.message.reply_text("Por favor, escribe el nombre de la ciudad para consultar el clima.")

# Handle user response
async def send_weather(update: Update, user_state):
    city_name = update.message.text
    weather_report = await get_weather(city_name)
    await update.message.reply_text(weather_report)

    await update.message.reply_text("¿Te gustaría saber algo más? Escribe tu pregunta o responde con /no.")
  
    chat_id = update.message.chat_id
    user_state[chat_id] = {
        "state": "ask_more",
        "weather_report": weather_report  # Store weather report to give context to openai
    }

# Handle additional questions with openai
async def handle_additional_question(update: Update, user_state):
    chat_id = update.message.chat_id
    if user_state.get(chat_id, {}).get("state") == "ask_more":
        user_question = update.message.text
        
        # Log user´s question
        logger.info(f"User {chat_id} asked: {user_question}")

        weather_report = user_state[chat_id]["weather_report"]

        # Include weather report in the question
        user_question = f"{weather_report}\n\n{user_question}"
        
     

        openai.api_key = openai_api_key
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "Eres un asistente amigable que responde preguntas sobre cualquier tema, utiliza emojis relacionados a las palabras clave de tu respuesta"},
                {"role": "user", "content": user_question}],
        )
        answer = response.choices[0].message.content
           
        #Log AI response
        logger.info(f"IA responded to user {chat_id}: {answer}")
        
        await update.message.reply_text(answer)
        await update.message.reply_text("¿Te gustaría saber algo más? Escribe tu pregunta o responde con /no.")

