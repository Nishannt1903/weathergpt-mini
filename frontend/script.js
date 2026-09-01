const questionInput = document.getElementById("question");
const askButton = document.getElementById("askButton");

const loading = document.getElementById("loading");
const response = document.getElementById("response");

const answer = document.getElementById("answer");
const temperature = document.getElementById("temperature");
const humidity = document.getElementById("humidity");
const rain = document.getElementById("rain");
const wind = document.getElementById("wind");


function findCity(question) {

    const knownCities = [
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
        "Nashik"
    ];

    for (const city of knownCities) {
        if (question.toLowerCase().includes(city.toLowerCase())) {
            return city;
        }
    }

    return null;
}


function createRecommendation(weather) {

    const rainProbability = weather.rain_probability;

    if (rainProbability >= 60) {
        return `Yes, I recommend carrying an umbrella. There is a ${rainProbability}% chance of rain.`;
    }

    if (rainProbability >= 30) {
        return `You may want to carry an umbrella just in case. There is a ${rainProbability}% chance of rain.`;
    }

    return `You probably don't need an umbrella. The chance of rain is only ${rainProbability}%.`;
}


async function askWeatherGPT() {

    const question = questionInput.value.trim();

    if (!question) {
        alert("Please enter a weather question.");
        return;
    }

    const city = findCity(question);

    if (!city) {
        alert("Please mention a city, for example: Nagpur, Pune or Mumbai.");
        return;
    }

    loading.classList.remove("hidden");
    response.classList.add("hidden");

    try {

        const url =
            `http://10.184.4.139:5000/api/weather?city=${encodeURIComponent(city)}`;

        const result = await fetch(url);

        const weather = await result.json();

        if (!result.ok) {
            throw new Error(weather.error || "Weather request failed.");
        }

        answer.textContent = createRecommendation(weather);

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

        alert("Unable to get weather data. Make sure the backend is running.");

        console.error(error);

    } finally {

        loading.classList.add("hidden");
    }
}


askButton.addEventListener("click", askWeatherGPT);