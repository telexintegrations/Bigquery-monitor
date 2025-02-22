from ast import literal_eval
from bq_functions.bigquery_funcs import get_daily_slot_utilization, get_run_errors
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.cloud import bigquery
from google.oauth2 import service_account
from integration_json.telex_json import integration_json
from models.models import ReportPayload
import asyncio
import httpx
import json
import time

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/integration.json")
def get_integration_json(request: Request):
    base_url = str(request.base_url).rstrip("/")
    integration_json["data"]["descriptions"]["app_url"] = base_url
    integration_json["data"]["tick_url"] = f"{base_url}/tick"
    return integration_json

@app.post("/tick")
async def get_performance_reports(payload: ReportPayload):
    sa_key = (dict(payload.settings[1])["default"])
    print(type(sa_key))
    if isinstance(sa_key, str):
        sa_key_json = json.loads(sa_key)
    else:
        sa_key_json = sa_key.model_dump_json()
    
    project_id = dict(payload.settings[3])["default"]
    region = dict(payload.settings[4])["default"]

    credentials = service_account.Credentials.from_service_account_info(json.loads(sa_key_json))
    scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/bigquery'])
    
    bigquery_client = bigquery.Client(credentials=scoped_credentials, project=project_id)
    
    reports = {}
    reports["Date"] = time.strftime("%Y-%m-%d")
    reports["\nDaily Resource Utilization Report"], reports["\nError Reports"] = await asyncio.gather(get_daily_slot_utilization(bigquery_client, region=region), get_run_errors(bigquery_client, region=region))

    data = {
        "message": str(reports),
        "username": "BigQuery Monitor",
        "event_name": "BigQuery Resources Check-In",
        "status": "success"
    }

    for attempt in range(3):
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=None)) as client:
            try:
                response = await client.post(payload.return_url, json=data)
                response.raise_for_status()
                return JSONResponse(content={"status": "success"})
            except(httpx.HTTPStatusError, httpx.RequestError) as exc:
                if attempt == 2:
                    return JSONResponse(content={"status": "failed", "error": str(exc)})
                await asyncio.sleep(2)
