from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests

from llm_service import generate_weather_response


# ---------------------------------------------------------
# Flask setup
# ---------------------------------------------------------

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------

@app.route("/")
def home():
    return send_from_directory(
        "../frontend",
        "index.html"
    )


@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(
        "../frontend",
        filename
    )


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok"
    })


# ---------------------------------------------------------
# Weather API
# ---------------------------------------------------------

@app.route("/api/weather", methods=["GET"])
def weather():

    city = request.args.get("city")

    if not city:
        return jsonify({
            "error": "Please provide a city name."
        }), 400

    try:

        # Find city coordinates
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

        # Get weather
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "wind_speed_10m,"
                "weather_code"
            ),
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


# ---------------------------------------------------------
# AI Weather Question
# ---------------------------------------------------------

@app.route("/api/ask", methods=["POST"])
def ask():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is missing."
            }), 400

        question = data.get(
            "question",
            ""
        ).strip()

        if not question:
            return jsonify({
                "error": "Please enter a question."
            }), 400

        # Cities for MVP
        cities = [
            "Nagpur",
            "Pune",
            "Mumbai",
            "Delhi",
            "Bengaluru",
            "Bangalore",
            "Hyderabad",
            "Chennai",
            "Kolkata",
            "Ahmedabad",
            "Jaipur",
            "Nashik",
            "Surat",
            "Indore",
            "Bhopal",
            "Aurangabad",
            "Thane",
            "Noida",
            "Gurgaon",
            "Lucknow"
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

        # -------------------------------------------------
        # Get weather
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Get current weather
        # -------------------------------------------------

        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "wind_speed_10m,"
                "weather_code"
            ),
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

        clean_weather = {
            "city": city_name,
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "rain_probability": rain_probability,
            "wind_speed": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code")
        }

        # -------------------------------------------------
        # Gemini
        # -------------------------------------------------

        ai_answer = generate_weather_response(
            question,
            clean_weather
        )

        # -------------------------------------------------
        # Final response
        # -------------------------------------------------

        return jsonify({
            "answer": ai_answer,
            "weather": clean_weather
        })

    except requests.RequestException:
        return jsonify({
            "error": "Unable to connect to weather service."
        }), 500

    except Exception as error:

        print("Backend error:", error)

        return jsonify({
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# Run server
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )