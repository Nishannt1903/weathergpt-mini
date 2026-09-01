from flask import Flask, jsonify, request
from llm_service import generate_weather_response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok"
    })


@app.route("/api/weather", methods=["GET"])
def weather():
    city = request.args.get("city")

    if not city:
        return jsonify({
            "error": "Please provide a city name."
        }), 400

    try:
        # Find the city coordinates
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(
            geo_url,
            params=geo_params,
            timeout=10
        )

        geo_data = geo_response.json()

        if "results" not in geo_data or not geo_data["results"]:
            return jsonify({
                "error": f"City '{city}' was not found."
            }), 404

        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]
        city_name = location["name"]

        # Get weather information
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "hourly": "precipitation_probability",
            "forecast_days": 1,
            "timezone": "auto"
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        weather_data = weather_response.json()

        current = weather_data.get("current", {})
        hourly = weather_data.get("hourly", {})

        rain_probability = 0

        if hourly.get("precipitation_probability"):
            rain_probability = max(
                hourly["precipitation_probability"][:6]
            )

        result = {
            "city": city_name,
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "rain_probability": rain_probability,
            "wind_speed": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code")
        }

        return jsonify(result)

    except requests.RequestException:
        return jsonify({
            "error": "Unable to connect to the weather service."
        }), 500

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500

@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()

    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    # Simple city detection
    cities = [
        "Nagpur", "Pune", "Mumbai", "Delhi",
        "Bengaluru", "Bangalore", "Hyderabad",
        "Chennai", "Kolkata", "Ahmedabad",
        "Jaipur", "Nashik"
    ]

    city = None

    for c in cities:
        if c.lower() in question.lower():
            city = c
            break

    if not city:
        return jsonify({
            "error": "Please mention a city."
        }), 400

    # Get weather from our existing weather endpoint
    with app.test_request_context(
        f"/api/weather?city={city}"
    ):
        weather_response = weather()

    if isinstance(weather_response, tuple):
        weather_data = weather_response[0].get_json()
    else:
        weather_data = weather_response.get_json()

    if "error" in weather_data:
        return jsonify(weather_data), 400

    # Ask Gemini to turn weather data into a natural answer
    ai_answer = generate_weather_response(
        question,
        weather_data
    )

    return jsonify({
        "answer": ai_answer,
        "weather": weather_data
    })
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )