from datetime import date, datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field, AfterValidator
from home_leads_gen_voice_agent.utils.datetime import parse_mm_dd_yyyy

class PropertyDetails(BaseModel):
    sale_property_address: str = Field(
        description="Address of the property",
        alias="SALE_PROPERTY_ADDRESS",
        default="Not listed"
    )
    PROPERTY_SALE_LISTING_PRICE: str = Field(
        description="Sale price of the property",
        alias="PROPERTY_SALE_LISTING_PRICE",
        default="Not listed"
    )
    sale_property_sale_listing_date: Annotated[Optional[date], AfterValidator(parse_mm_dd_yyyy)] = Field(
        description="Date the property was listed",
        alias="SALE_PROPERTY_SALE_LISTING_DATE",
        default_factory=lambda: datetime.now().date()
    )
    sale_property_condition: str = Field(
        description="Condition of the property",
        alias="SALE_PROPERTY_CONDITION",
        default="Unknown"
    )
    sale_property_acquired_by_owner_amount: Optional[str] = Field(
        description="Amount the owner acquired the property for",
        alias="SALE_PROPERTY_ACQUIRED_BY_OWNER_AMOUNT",
        default=None
    )
    sale_property_acquired_by_owner_year: Optional[int] = Field(
        description="Year the owner acquired the property. Leave null if not listed.",
        alias="SALE_PROPERTY_ACQUIRED_BY_OWNER_YEAR",
        default=None
    )
    source_url: str = Field(
        description="The exact HTTPS source URL where the property listing was found",
        alias="SOURCE_URL",
        default="Not listed"
    )
    phone_number: Optional[str] = Field(
        description="phone number for the contact on the listing page",
        alias="PHONE_NUMBER",
        default="Not listed"
    )
    local_rent_estimation: str = Field(
        description="Local rent estimation",
        alias="LOCAL_RENT_ESTIMATION",
        default="Not listed"
    )

class PropertyDetailsList(BaseModel):
    properties: list[PropertyDetails] = Field(
        description="List of all properties",
        alias="PROPERTIES",
        default=[]
    )