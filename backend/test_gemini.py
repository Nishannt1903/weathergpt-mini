from llm_service import generate_weather_response


weather = {
    "city": "Nagpur",
    "temperature": 28,
    "humidity": 75,
    "rain_probability": 70,
    "wind_speed": 12,
    "weather_code": 61
}

question = "Should I carry an umbrella in Nagpur?"

answer = generate_weather_response(question, weather)

print("\nWeatherGPT says:")
print(answer)