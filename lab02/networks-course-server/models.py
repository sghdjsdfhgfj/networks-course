from typing import Optional

from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    description: str
    image: Optional[str] = None

class ProductPost(BaseModel):
    name: str
    description: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None