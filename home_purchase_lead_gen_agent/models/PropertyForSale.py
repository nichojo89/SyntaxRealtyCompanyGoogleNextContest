from datetime import date, datetime
from typing import Annotated
from pydantic import BaseModel, Field, AfterValidator
from home_purchase_lead_gen_agent.utils.datetime import parse_mm_dd_yyyy


class PropertyForSale(BaseModel):
    sale_property_address: str = Field(
        description="Address of the property",
        alias="SALE_PROPERTY_ADDRESS",
        default="52 E Burdick St, Oxford, MI 48371"
    )
    sale_property_sale_listing_price: str = Field(
        description="Sale price of the property",
        alias="SALE_PROPERTY_SALE_LISTING_PRICE",
        default="$235,000"
    )
    sale_property_sale_listing_date: Annotated[date, AfterValidator(parse_mm_dd_yyyy)] = Field(
        description="Date the property was listed",
        alias="SALE_PROPERTY_SALE_LISTING_DATE",
        default=datetime.now().date()
    )
    sale_property_condition: str = Field(
        description="Condition of the property",
        alias="SALE_PROPERTY_CONDITION",
        default="Fair condition"
    )
    sale_property_acquired_by_owner_amount: str = Field(
        description="Amount the owner acquired the property for",
        alias="SALE_PROPERTY_ACQUIRED_BY_OWNER_AMOUNT",
        default="$138,000"
    )
    sale_property_acquired_by_owner_year: int = Field(
        description="Year the owner acquired the property",
        alias="SALE_PROPERTY_ACQUIRED_BY_OWNER_YEAR",
        default=2022
    )
    local_rent_estimation: str = Field(
        description="Local rent estimation",
        alias="LOCAL_RENT_ESTIMATION",
        default="$1,300"
    )
    comparable_property_address: str = Field(
        description="Comparable property address",
        alias="COMPARABLE_PROPERTY_ADDRESS",
        default="1234 Lapeer rd. Oxford MI"
    )
    buyers_name: str = Field(
        description="Buyer's name or realtor name",
        alias="BUYERS_NAME",
        default="REALTOR_NAME"
    )
    buyers_loan_application_amount: str = Field(
        description="Buyer's loan application amount",
        alias="BUYERS_LOAN_APPLICATION_AMOUNT",
        default="$145,000"
    )
    buyers_loan_amount: str = Field(
        description="Buyer's loan amount",
        alias="BUYERS_LOAN_AMOUNT",
        default="$150,000"
    )
    buyers_down_payment: str = Field(
        description="Buyer's down payment",
        alias="BUYERS_DOWN_PAYMENT",
        default="$30,000"
    )
    low_ball_amount: str = Field(
        description="Low ball offer amount",
        alias="LOW_BALL_AMOUNT",
        default="$130,000"
    )