from pydantic import BaseModel


class User(BaseModel):
  id: int
  age: int
  gender: str
  hiv_status: str
  tb_status: str
  hepatitis_status: str
