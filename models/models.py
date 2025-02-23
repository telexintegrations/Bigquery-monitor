from pydantic import BaseModel
from typing import List, Union


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

# Convert report from dict format into a formated string as Telex channel msg

def level_dict(reports: dict) -> str:
    """
    Convert report from dict format into a formated string as Telex channel msg
    """
    placeholder = ""
    for key, value in reports.items():
        if isinstance(value, dict) and ((len(value.keys()) > 1) or (isinstance(value[list(value.keys())[0]], dict))):
            placeholder += ("\n" + "\033[1m" + key + "\033[0m" + "\n" + level_dict(value))
        elif isinstance(value, list) and (len(value) > 1) and (isinstance(value[0], dict)):
            for i in value:
                placeholder += ("\n" + "\033[1m" + key + "\033[0m" + "\n" + level_dict(i))
        else:
            placeholder += (key + " : " + str(value) + "\n") 
    return placeholder