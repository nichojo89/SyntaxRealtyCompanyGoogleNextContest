from pydantic import BaseModel


class LeadTextRequest(BaseModel):
    """Structured output that represents data to be used to help generate a text message"""
    sale_property_address: str
    sale_property_sale_listing_date: str | None