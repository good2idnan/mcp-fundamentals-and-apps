import gradio as gr
import httpx

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


def get_condition(code: int) -> str:
    if code == 0:              return "☀️ Clear sky"
    elif code in [1, 2, 3]:   return "⛅ Partly cloudy"
    elif code in [45, 48]:    return "🌫️ Foggy"
    elif code in [51,53,55,61,63,65]: return "🌧️ Rainy"
    elif code in [71, 73, 75]:return "❄️ Snowy"
    elif code in [95, 96, 99]:return "⛈️ Thunderstorm"
    else:                      return "🌤️ Mixed conditions"


# ── Core Tool Function ────────────────────────────────────
def get_weather(location: str) -> str:
    """
    Get the current real weather for any city or location worldwide.

    Args:
        location (str): The city or location name to get weather for (e.g. 'Jeddah', 'New York')

    Returns:
        str: Current weather including condition, temperature, humidity, and wind speed
    """
    lat, lon = get_coordinates(location)
    if lat is None:
        return f"❌ Could not find location: **{location}**. Please check the spelling."

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

    condition = get_condition(current["weathercode"])
    temp_c   = current["temperature_2m"]
    temp_f   = round((temp_c * 9 / 5) + 32, 1)
    humidity = current["relative_humidity_2m"]
    wind     = current["windspeed_10m"]

    return (
        f"### 📍 Weather in {location}\n\n"
        f"| Property     | Value                  |\n"
        f"|--------------|------------------------|\n"
        f"| Condition    | {condition}            |\n"
        f"| Temperature  | {temp_c}°C / {temp_f}°F |\n"
        f"| Humidity     | {humidity}%            |\n"
        f"| Wind Speed   | {wind} km/h            |"
    )


# ── Gradio UI ─────────────────────────────────────────────
with gr.Blocks(title="🌤️ Weather MCP Server", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🌤️ Weather MCP Server
    > Real-time weather powered by **Open-Meteo** — also exposed as an **MCP Server**
    """)

    with gr.Row():
        with gr.Column(scale=2):
            location_input = gr.Textbox(
                label="📍 Location",
                placeholder="e.g. Jeddah, London, Tokyo...",
                lines=1
            )
            submit_btn = gr.Button("Get Weather 🌍", variant="primary")

        with gr.Column(scale=3):
            output = gr.Markdown(label="Weather Result")

    # Quick city buttons
    gr.Markdown("### 🚀 Quick Cities")
    with gr.Row():
        for city in ["Jeddah", "Riyadh", "Lahore", "London", "New York", "Tokyo"]:
            gr.Button(city).click(
                fn=get_weather,
                inputs=gr.State(city),
                outputs=output
            )

    submit_btn.click(fn=get_weather, inputs=location_input, outputs=output)
    location_input.submit(fn=get_weather, inputs=location_input, outputs=output)

    gr.Markdown("""
    ---
    ### 🔌 Connect as MCP Server
    Add this to your `agent.json` or `mcp.json`:
```json
    {
      "type": "sse",
      "url": "http://localhost:7860/gradio_api/mcp/sse"
    }
```
    View MCP schema at: `http://localhost:7860/gradio_api/mcp/schema`
    """)


if __name__ == "__main__":
    demo.launch(mcp_server=True)