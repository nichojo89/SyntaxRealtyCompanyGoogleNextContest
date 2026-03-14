from pydantic import BaseModel, Field


class TextMessageEvaluation(BaseModel):
    score: int = Field(description="Effectiveness score from 1 to 100")
    reason: str = Field(description="Reason for the score, and feedback if under 90")
    approved: bool = Field(description="True if score is 90 or above")