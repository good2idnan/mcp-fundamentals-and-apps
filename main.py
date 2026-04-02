from mcp.client.fastmcp import FastMCP

async def main():
    client = FastMCP("http://localhost:3001")
    
    # Call a tool
    weather = await client.call_tool("get_weather", location="New York")
    print(weather)
    
    # Read a resource
    resource = await client.read_resource("weather://New York")
    print(resource)
    
    # Run a prompt
    prompt = await client.run_prompt("weather_prompt", location="New York")
    print(prompt)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
