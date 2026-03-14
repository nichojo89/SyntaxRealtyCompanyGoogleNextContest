from datetime import date, datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field, AfterValidator
from home_purchase_lead_gen_agent.utils.datetime import parse_mm_dd_yyyy


class PropertyForSale(BaseModel):
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
    sale_property_condition: str = Field(
        description="Condition of the property",
        alias="SALE_PROPERTY_CONDITION",
        default="Unknown"
    )
    sale_property_acquired_by_owner_amount: str = Field(
        description="Amount the owner acquired the property for",
        alias="SALE_PROPERTY_ACQUIRED_BY_OWNER_AMOUNT",
        default="Not listed"
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
    local_rent_estimation: str = Field(
        description="Local rent estimation",
        alias="LOCAL_RENT_ESTIMATION",
        default="Not listed"
    )
    comparable_property_address: str = Field(
        description="Comparable property address",
        alias="COMPARABLE_PROPERTY_ADDRESS",
        default="Not listed"
    )
    buyers_name: str = Field(
        description="Buyer's name or realtor name",
        alias="BUYERS_NAME",
        default="Not listed"
    )
    buyers_loan_application_amount: str = Field(
        description="Buyer's loan application amount",
        alias="BUYERS_LOAN_APPLICATION_AMOUNT",
        default="Not listed"
    )
    buyers_loan_amount: str = Field(
        description="Buyer's loan amount",
        alias="BUYERS_LOAN_AMOUNT",
        default="Not listed"
    )
    buyers_down_payment: str = Field(
        description="Buyer's down payment",
        alias="BUYERS_DOWN_PAYMENT",
        default="Not listed"
    )
    low_ball_amount: str = Field(
        description="Low ball offer amount",
        alias="LOW_BALL_AMOUNT",
        default="Not listed"
    )