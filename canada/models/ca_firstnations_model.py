from typing import Optional
from pydantic import BaseModel

'''
Data model for First Nation entity extraction from Gov of Canada First Nations list website
'''
class FirstNation(BaseModel):
    official_name: str
    number: int
    address: str
    postal_code: str
    phone: Optional[str] = None
    fax: Optional[str] = None
    website: Optional[str] = None