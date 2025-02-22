from pydantic import BaseModel
from typing import List, Union
from fastapi import BackgroundTasks

class ServiceAccountKey(BaseModel):
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str

class Setting(BaseModel):
    label: str
    type:str
    required: bool
    default: Union[str, ServiceAccountKey]

class ReportPayload(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]

