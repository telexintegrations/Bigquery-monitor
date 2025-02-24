from bq_functions.bigquery_funcs import get_daily_slot_utilization, get_run_errors
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.cloud import bigquery
from pydantic import BaseModel
from typing import List, Union
import asyncio
import json
import os

load_dotenv()

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

async def get_reports(payload: ReportPayload) -> dict:
    """
    Return resource utilization and error reports as dictionary
    """
    # Obtain service account key
    sa_key = (dict(payload.settings[1])["default"])

    # If service account key is a string
    if not sa_key:
        sa_key = os.getenv('SERVICE_ACCOUNT_KEY')
        sa_key_json = json.loads(sa_key)
    elif isinstance(sa_key, str):
        sa_key_json = json.loads(sa_key)
    else:

        sa_key_json = sa_key.model_dump_json()
        sa_key_json = json.loads(sa_key_json)
    
    credentials = service_account.Credentials.from_service_account_info(sa_key_json)
    scoped_credentials = credentials.with_scopes([
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/bigquery'
        ]
        )
    
    project_id = dict(payload.settings[3])["default"]
    region = dict(payload.settings[4])["default"]

    bigquery_client = bigquery.Client(credentials=scoped_credentials, project=project_id)
    
    reports = {}

    reports["📋Daily Resource Utilization Report (in slot milliseconds)"], reports["🔴Error Reports"] = await asyncio.gather(
        get_daily_slot_utilization(bigquery_client, region=region),
        get_run_errors(bigquery_client, region=region)
        )

    if not reports["🔴Error Reports"]:
        reports["🔴Error Reports"] = "No error reports"

    return reports

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