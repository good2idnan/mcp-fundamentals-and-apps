from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("Weather Service")

# ── Helpers ──────────────────────────────────────────────
def get_coordinates(location: str):
    """Get lat/lon for a city using Open-Meteo geocoding"""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": location, "count": 1, "language": "en", "format": "json"}
    response = httpx.get(url, params=params)
    data = response.json()
    if not data.get("results"):
        return None, None
    result = data["results"][0]
    return result["latitude"], result["longitude"]


def fetch_weather(location: str) -> str:
    """Core logic reused by tool, resource, and prompt"""
    lat, lon = get_coordinates(location)
    if lat is None:
        return f"Could not find location: {location}"

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weathercode,windspeed_10m,relative_humidity_2m",
        "temperature_unit": "celsius",
        "windspeed_unit": "kmh",
        "timezone": "auto"
    }
    data = httpx.get(url, params=params).json()
    current = data["current"]

    code = current["weathercode"]
    if code == 0:
        condition = "Clear sky"
    elif code in [1, 2, 3]:
        condition = "Partly cloudy"
    elif code in [45, 48]:
        condition = "Foggy"
    elif code in [51, 53, 55, 61, 63, 65]:
        condition = "Rainy"
    elif code in [71, 73, 75]:
        condition = "Snowy"
    elif code in [95, 96, 99]:
        condition = "Thunderstorm"
    else:
        condition = "Mixed conditions"

    temp_c = current["temperature_2m"]
    temp_f = round((temp_c * 9 / 5) + 32, 1)
    humidity = current["relative_humidity_2m"]
    wind = current["windspeed_10m"]

    return (
        f"Weather in {location}:\n"
        f"  Condition  : {condition}\n"
        f"  Temperature: {temp_c}°C / {temp_f}°F\n"
        f"  Humidity   : {humidity}%\n"
        f"  Wind Speed : {wind} km/h"
    )


# ── Tool ─────────────────────────────────────────────────
# Called by the LLM agent to get weather on demand
@mcp.tool()
def get_weather(location: str) -> str:
    """Get the real current weather for a specific location"""
    return fetch_weather(location)


# ── Resource ─────────────────────────────────────────────
# Exposes weather as a readable URI — like a data source
# Access via:  weather://Jeddah
@mcp.resource("weather://{location}")
def weather_resource(location: str) -> str:
    """Weather data accessible as a resource URI"""
    return fetch_weather(location)


# ── Prompt ───────────────────────────────────────────────
# Returns a pre-built prompt string the LLM can use
@mcp.prompt()
def weather_prompt(location: str) -> str:
    """Generate a weather summary prompt for a location"""
    data = fetch_weather(location)
    return (
        f"You are a helpful weather assistant.\n"
        f"Here is the current weather data:\n\n"
        f"{data}\n\n"
        f"Please give the user a friendly, conversational weather summary."
    )


if __name__ == "__main__":
    mcp.run()
