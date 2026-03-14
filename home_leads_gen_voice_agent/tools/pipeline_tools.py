import httpx

BASE_URL = "http://127.0.0.1:8001/pipeline"


async def run_lead_generation(location: str, criteria: str) -> str:
    """
    Use this tool to search for homes that have been on the market for a long time.
    Runs a lead generation pipeline to find FSBO or stale MLS listings.

    Args:
        location (str): The city, state, or zip code to search in.
        criteria (str): Any additional search criteria such as price range, property type, or days on market.
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/lead-generation",
            json={"location": location, "criteria": criteria}
        )
        response.raise_for_status()
        return response.json()["result"]

async def run_marketing_content(sale_property_address: str, sale_property_sale_listing_date: str = None) -> str:
    """
    Use this tool to generate a high-quality text message to send to a home owner.
    Iteratively creates and refines a pitch until it scores 90 or above.

    Args:
        sale_property_address (str): The full address of the property to generate a pitch for.
        sale_property_sale_listing_date (str): The date the property was listed for sale.
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/marketing-content",
            json={
                "sale_property_address": sale_property_address,
                "sale_property_sale_listing_date": sale_property_sale_listing_date
            }
        )
        response.raise_for_status()
        return response.json()["result"]