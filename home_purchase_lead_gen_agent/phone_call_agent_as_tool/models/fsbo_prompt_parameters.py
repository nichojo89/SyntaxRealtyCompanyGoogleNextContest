from typing import Optional
from pydantic import BaseModel, Field

DEFAULT_NOT_AVAILABLE = "NOT AVAILABLE"
class FSBOPromptParameters(BaseModel):
    sale_property_address: str = Field(
        description="Address of the property",
        alias="sale_property_address",
        default=DEFAULT_NOT_AVAILABLE
    )
    available_appointment_times: Optional[list[str]] = Field(
        description="Address of the property",
        alias="available_appointment_times",
        default=[]
    )
    property_sale_listing_price: str = Field(
        description="Listed sale price for the property in currency format.",
        alias="property_sale_listing_price",
        default=DEFAULT_NOT_AVAILABLE
    )
    property_sale_listing_date: str = Field(
        description="The date the property was listed for sale.",
        alias="property_sale_listing_date",
        default=DEFAULT_NOT_AVAILABLE
    )
    sale_property_condition: str = Field(
        description="Your evaluation of what condition the property is in.",
        alias="sale_property_condition",
        default=DEFAULT_NOT_AVAILABLE
    )
    sale_property_acquired_by_owner_amount: str = Field(
        description="(OPTIONAL) The amount the home-owner purchased the property before they tried to sell it.",
        alias="sale_property_acquired_by_owner_amount",
        default=DEFAULT_NOT_AVAILABLE
    )
    sale_property_acquired_by_owner_year: str = Field(
        description="(OPTIONAL) The year the home-owner purchased the property before they tried to sell it.",
        alias="sale_property_acquired_by_owner_year",
        default=DEFAULT_NOT_AVAILABLE
    )
    local_rent_estimation: str = Field(
        description="Your evaluation of what you think local rent in the area is for similar properties.",
        alias="local_rent_estimation",
        default=DEFAULT_NOT_AVAILABLE
    )
