from fastmcp import FastMCP
import requests

mcp = FastMCP("hotel-server")
HOTEL_API_BASE = "https://standing-fish-574.convex.site/hotels"


@mcp.tool()
def list_hotels() -> list[dict]:
    """Get all available hotels."""
    r = requests.get(HOTEL_API_BASE)
    return r.json().get("hotels", []) if r.ok else []


@mcp.tool()
def search_hotels(city: str, checkIn: str = None, checkOut: str = None) -> list[dict]:
    """Search hotels by city and optional dates."""
    params = {"city": city}
    if checkIn:
        params["checkIn"] = checkIn
    if checkOut:
        params["checkOut"] = checkOut
    r = requests.get(f"{HOTEL_API_BASE}/search", params=params)
    return r.json().get("hotels", []) if r.ok else []


@mcp.tool()
def book_hotel(hotel_id: str, guest_name: str, guest_email: str,
               check_in_date: str, check_out_date: str, room_type: str) -> dict:
    """Book a hotel room."""
    payload = {
        "hotelId": hotel_id, "guestName": guest_name, "guestEmail": guest_email,
        "checkInDate": check_in_date, "checkOutDate": check_out_date, "roomType": room_type,
    }
    r = requests.post(f"{HOTEL_API_BASE}/book", json=payload)
    return r.json()


if __name__ == "__main__":
    mcp.run()