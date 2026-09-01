import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=api_key)


def generate_weather_response(user_question, weather_data):
    prompt = f"""
You are WeatherGPT, a helpful weather assistant.

The user asked:
"{user_question}"

Here is the REAL weather data:

City: {weather_data.get("city")}
Temperature: {weather_data.get("temperature")}°C
Humidity: {weather_data.get("humidity")}%
Rain probability: {weather_data.get("rain_probability")}%
Wind speed: {weather_data.get("wind_speed")} km/h
Weather code: {weather_data.get("weather_code")}

Answer the user's question naturally and briefly.

Rules:
- Use ONLY the weather information provided above.
- Never invent weather information.
- Give practical advice when appropriate.
- If the user asks about an umbrella, discuss the rain probability.
- If the user asks about outdoor activities, consider rain, temperature and wind.
- Keep the answer under 80 words.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text