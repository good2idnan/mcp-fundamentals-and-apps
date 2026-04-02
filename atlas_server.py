import os
import httpx
import psutil
import time
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Atlas Workspace Assistant", dependencies=["httpx", "psutil"])

NOTES_DIR = os.path.abspath(".notes")
if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)

# ── Helpers ──────────────────────────────────────────────
def get_coordinates(location: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": location, "count": 1, "language": "en", "format": "json"}
    response = httpx.get(url, params=params)
    data = response.json()
    if not data.get("results"):
        return None, None
    result = data["results"][0]
    return result["latitude"], result["longitude"]

# ── Tools ────────────────────────────────────────────────

@mcp.tool()
def get_weather(location: str) -> str:
    """Get the current weather for any city."""
    lat, lon = get_coordinates(location)
    if lat is None:
        return f"Could not find location: {location}"

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weathercode,windspeed_10m",
        "timezone": "auto"
    }
    data = httpx.get(url, params=params).json()
    curr = data["current"]
    return f"Weather in {location}: {curr['temperature_2m']}°C, Wind: {curr['windspeed_10m']}km/h"

@mcp.tool()
def add_note(title: str, content: str) -> str:
    """Save a persistent note to the workspace."""
    filename = "".join(x for x in title if x.isalnum() or x in " -_").strip() + ".txt"
    filepath = os.path.join(NOTES_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return f"✅ Note '{title}' saved successfully."

@mcp.tool()
def list_notes() -> list[str]:
    """List all saved notes in the workspace."""
    if not os.path.exists(NOTES_DIR):
        return []
    return [f[:-4] for f in os.listdir(NOTES_DIR) if f.endswith(".txt")]

@mcp.tool()
def list_files(directory: str = ".") -> list[str]:
    """List files in the workspace (security-constrained to project root)."""
    # Simple security: don't allow going above current directory
    safe_path = os.path.abspath(directory)
    if not safe_path.startswith(os.getcwd()):
        return ["Error: Access denied (Outside workspace)"]
    
    try:
        items = os.listdir(safe_path)
        return [f"{'[DIR] ' if os.path.isdir(os.path.join(safe_path, i)) else '[FILE] '}{i}" for i in items]
    except Exception as e:
        return [f"Error: {str(e)}"]

@mcp.tool()
def read_workspace_file(filename: str) -> str:
    """Read the content of a file in the workspace."""
    safe_path = os.path.abspath(filename)
    if not safe_path.startswith(os.getcwd()):
        return "Error: Access denied (Outside workspace)"
    
    try:
        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

# ── Resources ───────────────────────────────────────────

@mcp.resource("system://metrics")
def system_metrics() -> str:
    """Live system performance data (CPU, RAM, Uptime)."""
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    return f"CPU: {cpu}% | RAM: {ram}% | System Boot: {boot_time}"

@mcp.resource("notes://{title}")
def note_resource(title: str) -> str:
    """Access a specific note as a resource."""
    filename = f"{title}.txt"
    filepath = os.path.join(NOTES_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return "Note not found."

# ── Prompts ─────────────────────────────────────────────

@mcp.prompt()
def workspace_expert() -> str:
    """Become an expert workspace assistant."""
    return (
        "You are Atlas, the intelligent workspace manager.\n"
        "You have access to weather data, local files, and a personal note-taking system.\n"
        "Help the user stay organized, summarize their files, and keep track of their projects."
    )

if __name__ == "__main__":
    mcp.run()
