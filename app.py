import gradio as gr
import psutil
import os
import time
from datetime import datetime

# Import Atlas logic directly into the UI for the "WOW" reactive experience
from atlas_server import get_weather, add_note, list_notes, list_files, read_workspace_file

def get_system_stats():
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    now = datetime.now().strftime("%H:%M:%S")
    return f"CPU: {cpu}%", f"RAM: {ram}%", f"Last Update: {now}"

def refresh_notes():
    notes = list_notes()
    if not notes:
        return "No notes saved yet."
    return "\n".join([f"• {n}" for n in notes])

def refresh_files():
    files = list_files()
    return "\n".join(files)

# ── 🤖 Agent Engine (Simulation) ──────────────────────────
# This maps natural language to tool calls for the prototype
def atlas_agent(message, history):
    msg = message.lower()
    
    if "weather" in msg:
        # Extract city (simplistic)
        words = message.split()
        city = words[-1].strip("?") if len(words) > 1 else "Jeddah"
        result = get_weather(city)
        return result
    
    elif "list files" in msg or "files" in msg:
        files = list_files()
        return "📄 **Workspace Files:**\n" + "\n".join(files)
    
    elif "test" in msg:
        return "System is online. MCP server is active at `atlas_server.py`."
    
    elif "note" in msg and "save" in msg:
        return "To save a note, please use the 'Notes' tab for structured entry!"

    return "I am Atlas. I can check the **weather**, **list files**, or manage your **notes**. Try asking: 'What is the weather in London?'"

# ── 🎨 Gradio UI ──────────────────────────────────────────

with gr.Blocks(title="Atlas: Agentic Workspace", theme=gr.themes.Default(primary_hue="blue", secondary_hue="slate")) as demo:
    
    gr.Markdown("# 🚀 Atlas: The Agentic Cockpit")
    gr.Markdown("> A reactive MCP workspace assistant for managing files, system metrics, and daily tasks.")

    with gr.Tabs():
        # TAB 1: ASSISTANT
        with gr.Tab("🤖 Assistant"):
            gr.ChatInterface(
                atlas_agent,
                description="Chat with Atlas to interact with your workspace via MCP tools.",
                examples=["What is the weather in New York?", "List files", "System status?"]
            )

        # TAB 2: FILES & NOTES
        with gr.Tab("📂 Workspace"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📝 Quick Note")
                    note_title = gr.Textbox(label="Title", placeholder="Meeting notes...")
                    note_content = gr.TextArea(label="Content", placeholder="Discussed MCP deployment...")
                    save_btn = gr.Button("Save Note 💾", variant="primary")
                    note_status = gr.Markdown()
                    
                with gr.Column():
                    gr.Markdown("### 📌 Recent Notes")
                    notes_list = gr.Markdown(value=refresh_notes())
                    refresh_notes_btn = gr.Button("🔄 Refresh Notes")

            gr.Markdown("---")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📁 File Explorer")
                    file_list = gr.Markdown(value=refresh_files())
                    refresh_files_btn = gr.Button("🔄 Scan Workspace")

        # TAB 3: SYSTEM MONITOR
        with gr.Tab("📈 System Monitor"):
            with gr.Row():
                cpu_stat = gr.Label(label="CPU Load")
                ram_stat = gr.Label(label="Memory Usage")
            
            last_update = gr.Text(label="Status", interactive=False)
            
            # Auto-update status every 3 seconds
            demo.load(get_system_stats, None, [cpu_stat, ram_stat, last_update], every=3)

    # ── Event Listeners ──────────────────────────────────────
    save_btn.click(fn=add_note, inputs=[note_title, note_content], outputs=note_status).then(
        fn=refresh_notes, outputs=notes_list
    )
    refresh_notes_btn.click(fn=refresh_notes, outputs=notes_list)
    refresh_files_btn.click(fn=refresh_files, outputs=file_list)

    gr.Markdown("""
    ---
    ### 🔌 Developer Integration
    Atlas also runs as a full **MCP Server**. Connect your professional agent (Claude Desktop) using:
    ```json
    {
      "type": "stdio",
      "command": "python",
      "args": ["atlas_server.py"]
    }
    ```
    """)

if __name__ == "__main__":
    demo.launch()
