from bigquery_funcs import get_daily_slot_utilization, get_run_errors
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google.oauth2 import service_account, credentials
from google.cloud import bigquery
from models import ReportPayload
from telex_json import integration_json
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import httpx
import json

app = FastAPI()

origins = [
    "http://localhost",
    "https://telex.im",
    "http://telex.im/",
    "https://staging.telex.im",
    "http://staging.telex.im",
    "http://telextest.im",
    "http://staging.telextest.im",
    "https://staging.telextest.im",
    "https://telextest.im"
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
    channel_id = payload.channel_id
    
    sa_key = (dict(payload.settings[1])["default"])
    sa_key_json = sa_key.model_dump_json()
    project_id = dict(payload.settings[3])["default"]
    # region = dict(payload.settings[4])["default"]

    credentials = service_account.Credentials.from_service_account_info(json.loads(sa_key_json))
    scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/bigquery'])
    
    bigquery_client = bigquery.Client(credentials=scoped_credentials, project=project_id)
    
    reports = {}

    reports["Daily Resource Utilization Report"], reports["Error Reports"] = await asyncio.gather(get_daily_slot_utilization(bigquery_client), get_run_errors(bigquery_client))

    data = {
        "message": reports,
        "username": "BigQuery Monitor",
        "event_name": "BigQuery Resources Checkin",
        "status": "success"
    }

    data = json.dumps(data, indent=2, default=str)

    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=None)) as client:
        try:
            print(payload.return_url)
            response = await client.post(payload.return_url, json=data, headers={"Content-Type": "application/json", "Accept": "application/json"})
            print(response.status_code)
            response.raise_for_status()
            return JSONResponse(content={"status": "success"})
        except httpx.HTTPStatusError as exc:
            return JSONResponse(content={"status": "failed", "error": str(exc)})
        except httpx.RequestError as exc:
            return JSONResponse(content={"status": "failed", "error": str(exc)})
