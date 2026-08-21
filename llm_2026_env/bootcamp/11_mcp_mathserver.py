from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a:int,b:int)->int:
    """ summary_

    Add to number
    """
    return a+b

@mcp.tool()
def multiple(a:int,b:int)->int:
    """
    multiply two numbers
    """
    return a*b

#the transport-"stdio" arguemnt tells the server to :
# use standard input/output(stdin and stdout) to receive and response to tool function calls 

if __name__ == "__main__":
    mcp.run(transport = "stdio")

