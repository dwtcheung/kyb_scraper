from typing import Optional, List
from pydantic import BaseModel
'''
Data model for Taiwan business entity extraction from Taiwan Ministry of Economic Affairs 
Not all attributes extracted, you will need to add definition for the following if needed:
* Managerial Personnel
* Branch Offices
* Factory
* Cross Domain Information
* History
* Self Publish
* Network
'''
class Director(BaseModel):
    no: int
    occupation: str
    name: str
    statutory_representative: Optional[str]
    number_shares: Optional[int]

class BusinessScope(BaseModel):
    code: str
    description: str

class TWBusiness(BaseModel):
    unified_business_no: int
    registration_status: str
    company_name: str
    foreign_company_name_specified_charter: Optional[str]
    amount_capital: Optional[int]
    total_paid_in_capital: Optional[int]
    share_value: Optional[float]
    equity_amount: Optional[int]
    name_of_representative: Optional[str]
    location_company: str
    registration_authority: str
    date_registration: str
    last_modification_date: str
    business_scope: List[BusinessScope]

