from pydantic import BaseModel

class UserBase(BaseModel):
    name : str
    mail : str
    sex : str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class Product(BaseModel):
    prd_id: int
    code: str
    name: str
    price: int

class EchoMessage(BaseModel):
    message: str | None = None

class TransactionRequest(BaseModel):
    total_amt: float
    emp_cd: int
    store_cd: int
    pos_no: int

class TransactionDetailRequest(BaseModel):
    trd_id: int
    prd_id: int
    prd_code: str
    prd_name: str
    prd_price: float

class Tax(BaseModel):
    tax_ID: int
    tax_code: str
    tax_name: str
    tax_percent: float
