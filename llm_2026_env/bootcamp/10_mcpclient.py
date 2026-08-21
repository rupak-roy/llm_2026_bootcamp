###########################
######### MCP CLIENT ######
###########################


import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def connect_server(server_file):

    server_params = StdioServerParameters(command="python",args=[server_file])
    return server_params


async def main():

    # -----------------------------------------
    # SERVER 1
    # -----------------------------------------

    server1_params = await connect_server("mcp_server_1.py")

    # -----------------------------------------
    # SERVER 2
    # -----------------------------------------
    server2_params = await connect_server("mcp_server_2.py")

    # -----------------------------------------
    # Connect Server 1
    # -----------------------------------------

    async with stdio_client(server1_params) as (read1,write1):
        async with ClientSession(read1,write1) as client1:

            await client1.initialize()
            tools1 = await client1.list_tools()
            print("\nSERVER 1 TOOLS")
            for tool in tools1.tools:
                print(tool.name)

            # Call Server 1
            result1 = await client1.call_tool("get_employee",arguments={"employee_id": "1001" })

            print("\nEmployee Result:")
            print(result1)

            # -----------------------------------------
            # Connect Server 2
            # -----------------------------------------

            async with stdio_client(server2_params) as (read2,write2):

                async with ClientSession(read2, write2) as client2:

                    await client2.initialize()
                    tools2 = await client2.list_tools()
                    print("\nSERVER 2 TOOLS")

                    for tool in tools2.tools:
                        print(tool.name)

                    # Call Server 2
                    result2 = await client2.call_tool(
                        "get_order",arguments={"order_id": "ORD001"})

                    print("\nOrder Result:")
                    print(result2)

if __name__ == "__main__":
    asyncio.run(main())