from pydantic import BaseModel


class LeadTextRequest(BaseModel):
    sale_property_address: str
    sale_property_sale_listing_date: str | None