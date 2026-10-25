from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict
from uuid import UUID
from datetime import date, time

class ClientBase(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_names: List[str] = Field(..., min_length=1)
    birth_date: date
    birth_place: str = Field(..., min_length=1)
    birth_time: Optional[time] = None
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    main_symptom: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
    geolocation: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    first_name: Optional[str] = None
    last_names: Optional[List[str]] = None
    birth_date: Optional[date] = None
    birth_place: Optional[str] = None

class ClientInDB(ClientBase):
    id: UUID
    created_at: str

    model_config = ConfigDict(from_attributes=True)
