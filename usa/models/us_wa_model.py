from typing import Optional, List
from pydantic import BaseModel

'''
Data model for using multiple agents to extract company profile in Washington state, USA
'''

class RegAgent(BaseModel):
    registered_agent_name: str
    street_address: str
    mailing_address: str

class Governor(BaseModel):
    title: str
    governors_type: str
    entity_type: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]

class USWABusiness(BaseModel):
    business_name: str
    ubi_number: str
    business_type: str
    business_status: str
    principal_office_street_address: str
    principal_office_mailing_address: str
    expiration_date: str
    jurisdiction: str
    formation_registration_date: str
    inactive_date: Optional[str]
    period_duration: str
    nature_business: str
    registered_agent_info: RegAgent
    governors: List[Governor]