from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Simple Calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

@mcp.resource("echo://{text}")
def echo_resource(text: str) -> str:
    """A simple resource that echoes back text."""
    return f"Resource content: {text}"

@mcp.prompt()
def math_assistant() -> str:
    """Returns a prompt to make the LLM a math expert."""
    return "You are a math tutor. Explain steps clearly using the calculator tools provided."

if __name__ == "__main__":
    mcp.run()
