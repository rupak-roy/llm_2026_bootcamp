#######################################
####### MCP SERVER 2: ORDER SERVER ####
#######################################

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Order Server")

@mcp.tool()
def get_order(order_id: str) -> dict:
    """Get order information."""

    orders = {
        "ORD001": {
            "customer": "ABC Corp",
            "product": "Laptop",
            "quantity": 10,
            "status": "Shipped"
        },
        "ORD002": {
            "customer": "XYZ Corp",
            "product": "Monitor",
            "quantity": 20,
            "status": "Processing"
        }
    }

    return orders.get(order_id,{"error": "Order not found"})


@mcp.tool()
def get_customer_orders(customer: str) -> list:
    """Get orders for a customer."""

    return [{
            "order_id": "ORD001",
            "customer": customer,
            "status": "Shipped"}]


if __name__ == "__main__":
    mcp.run()