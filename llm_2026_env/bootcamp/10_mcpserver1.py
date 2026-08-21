
####################################
##### MCP SERVER1: EMPLOYEE DATABASE MCP
#####################################


from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Employee Server")

@mcp.tool()
def get_employee(employee_id: str) -> dict:
    """Get employee information."""

    employees = {
        "1001": {"name": "John",
            "department": "IT",
            "role": "Developer"},
        "1002": {"name": "Sarah",
            "department": "HR",
            "role": "Manager"}
    }

    return employees.get(employee_id,{"error": "Employee not found"})


@mcp.tool()
def list_employees() -> list:
    """List all employees."""

    return [
        {"id": "1001", "name": "John"},
        {"id": "1002", "name": "Sarah"}
    ]


if __name__ == "__main__":
    mcp.run()

