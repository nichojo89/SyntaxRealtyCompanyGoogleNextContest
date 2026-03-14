from datetime import date, datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field, AfterValidator
from home_purchase_lead_gen_agent.utils.datetime import parse_mm_dd_yyyy

class PropertyLeads(BaseModel):
    property_name: str = Field(
        description="List of property sale leads",
        alias="PROPERTY_SALE_LEADS",
        default=[]
    )

class PropertyLead(BaseModel):
    sale_property_address: str = Field(
        description="Address of the property",
        alias="SALE_PROPERTY_ADDRESS",
        default="Not listed"
    )
    sale_property_sale_listing_price: str = Field(
        description="Sale price of the property",
        alias="SALE_PROPERTY_SALE_LISTING_PRICE",
        default="Not listed"
    )
    sale_property_sale_listing_date: Annotated[Optional[date], AfterValidator(parse_mm_dd_yyyy)] = Field(
        description="Date the property was listed",
        alias="SALE_PROPERTY_SALE_LISTING_DATE",
        default_factory=lambda: datetime.now().date()
    )