from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

@mcp.tool()
async def get_weather(location:str) ->str:
    """
    Get the current weather in a location
    """
    return "its always raining in California"

if __name__ =="__main__":
    mcp.run(transport="streamable-http") #otuput gives as API