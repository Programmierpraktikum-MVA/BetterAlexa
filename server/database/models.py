from pydantic import BaseModel

class SensitiveDataModel(BaseModel):
    key: str
    value: str

class UserIdMappingModel(BaseModel):
    betteralexa_user_id: str
    tutorai_user_id: str
