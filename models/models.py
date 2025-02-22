from pydantic import BaseModel
from typing import List, Union
import time 

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

def convert_reports_to_string(reports: dict) -> str:
    reports_as_string = "Date:" + str(time.strftime("%Y-%m-%d")) + "\n"

    for key, value in reports.items():
        print(key, value)
        reports_as_string += f"{key}\n"
        for k, v in value.items():
            reports_as_string += f"{k} : {v}\n"
    return reports_as_string

