from typing import Optional, List
from langchain.pydantic_v1 import BaseModel, Field

class Identifiers(BaseModel):
    """
    Structure to hold identifiers found in text
    """
    first_name: Optional[List[str]] = Field(description="List of first names identified in the text")
    last_name: Optional[List[str]] = Field(description="List of last names identified in the text")
    middle_name: Optional[List[str]] = Field(description="List of middle names identified in the text")
    phone: Optional[List[str]] = Field(description="List of phone or fax numbers identified in the text") 
    email: Optional[List[str]] = Field(description="List of email addresses identified in the text")
    address_line_1: Optional[List[str]] = Field(description="List of street address line 1s identified in the text")
    address_line_2: Optional[List[str]] = Field(description="List of street address line 2s identified in the text")
    city: Optional[List[str]] = Field(description="List of city, town or county names identified in the text")
    zipcode: Optional[List[str]] = Field(description="List of zip codes identified in the text")
    state: Optional[List[str]] = Field(description="List of state names or codes identified in the text")
    country: Optional[List[str]] = Field(description="List of country names identified in the text") 
    company: Optional[List[str]] = Field(description="List of company names identified in the text")


class TransformedData(BaseModel):
    """
    Structure to hold transformed data
    """
    identifiers: Optional[Identifiers] = Field(description="Structure holding the identified PII elements")
    tagged_text: Optional[str] = Field(description="The input text with PII elements tagged")
    
    
class ReflectionOuput(BaseModel):
    review: str = Field(default="n/a", description="Review of the TransformedData as to how well it aligns with the expected format")
    recommendations: str = Field(default="n/a", description="Actionable recommendations formatted as a multiline string containing bulleted list of necessary changes to align with original formatting instructions and improvement if needed for any attribute. Use examples as needed. If the TransformedData matches all requirements say so.")
    feedback: str = Field(default="n/a", description="'perfect' if no changes are required, or 'needs work' otherwise")