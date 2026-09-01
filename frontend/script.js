const questionInput = document.getElementById("question");
const askButton = document.getElementById("askButton");

const loading = document.getElementById("loading");
const response = document.getElementById("response");

const answer = document.getElementById("answer");
const temperature = document.getElementById("temperature");
const humidity = document.getElementById("humidity");
const rain = document.getElementById("rain");
const wind = document.getElementById("wind");


async function askWeatherGPT() {

    const question = questionInput.value.trim();

    if (!question) {
        alert("Please enter a weather question.");
        return;
    }

    loading.classList.remove("hidden");
    response.classList.add("hidden");

    try {

        const result = await fetch(
            "http://10.184.4.139:5000/api/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );

        const data = await result.json();

        if (!result.ok) {
            throw new Error(
                data.error || "Request failed."
            );
        }

        const weather = data.weather;

        // Gemini answer
        answer.textContent = data.answer;

        // Weather information
        temperature.textContent =
            `${weather.temperature}°C`;

        humidity.textContent =
            `${weather.humidity}%`;

        rain.textContent =
            `${weather.rain_probability}%`;

        wind.textContent =
            `${weather.wind_speed} km/h`;

        response.classList.remove("hidden");

    } catch (error) {

        console.error(error);

        alert(
            "Unable to get weather data. Make sure the backend is running."
        );

    } finally {

        loading.classList.add("hidden");
    }
}


askButton.addEventListener(
    "click",
    askWeatherGPT
);