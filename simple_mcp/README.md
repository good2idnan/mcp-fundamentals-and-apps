# 🧮 Simple Math MCP Server

A basic "getting started" MCP server that demonstrates the three core primitives: **Tools**, **Resources**, and **Prompts**.

## 🚀 Features
- **Tools**: `add`, `multiply` (Simple math operations)
- **Resources**: `echo://{text}` (A dynamic resource that mirrors input)
- **Prompts**: `math_assistant` (A pre-configured system prompt)

## 🛠️ Setup & Running

### 1. Install dependencies
Required: `mcp[cli]`
```bash
pip install mcp[cli]
```

### 2. Run the server
```bash
python server.py
```

### 3. Test in MCP Inspector
Make sure you have the MCP CLI installed:
```bash
mcp dev server.py
```

## 🔌 Connection for Claude Desktop
Add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "math-simple": {
      "command": "python",
      "args": ["/path/to/simple_mcp/server.py"]
    }
  }
}
```
