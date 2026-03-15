from pydantic import BaseModel


class LeadGenRequest(BaseModel):
    """Request parameters to search For-Sale-By-Owner home listings"""
    location: str
    criteria: str