from fastmcp import FastMCP
import requests

mcp = FastMCP("flight-server")
FLIGHT_API_BASE = "https://standing-fish-574.convex.site/flights"


@mcp.tool()
def list_flights() -> list[dict]:
    """Get all available flights."""
    r = requests.get(FLIGHT_API_BASE)
    return r.json().get("flights", []) if r.ok else []


@mcp.tool()
def search_flights(origin: str, destination: str, date: str = None) -> list[dict]:
    """Search flights by origin, destination, and optional date."""
    o = origin.upper() if origin and len(origin) == 3 and origin.isalpha() else origin
    d = destination.upper() if destination and len(destination) == 3 and destination.isalpha() else destination
    params = {"origin": o, "destination": d}
    if date:
        params["date"] = date
    r = requests.get(f"{FLIGHT_API_BASE}/search", params=params)
    return r.json().get("flights", []) if r.ok else []


@mcp.tool()
def book_flight(flight_id: str, passenger_name: str, passenger_email: str) -> dict:
    """Book a flight ticket."""
    payload = {"flightId": flight_id, "passengerName": passenger_name, "passengerEmail": passenger_email}
    r = requests.post(f"{FLIGHT_API_BASE}/book", json=payload)
    return r.json()


if __name__ == "__main__":
    mcp.run()