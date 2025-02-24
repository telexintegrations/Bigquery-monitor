from ast import literal_eval
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.cloud import bigquery
from integration_json.telex_json import integration_json
from models.models import ReportPayload, level_dict, get_reports
import asyncio
import httpx
import time

app = FastAPI()

origins = [
    "https://telex.im",
    "https://*.telex.im",
    "http://telextest.im",
    "http://staging.telextest.im"
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
async def send_reports(payload: ReportPayload):

    report_date = "\033[1mDate:" + str(time.strftime("%Y-%m-%d")) + "\033[0m" + "\n"

    reports = await get_reports(payload)

    string_reports = report_date + level_dict(reports)

    data = {
        "message": string_reports,
        "username": "BigQuery Monitor",
        "event_name": "BigQuery Resources Check-In",
        "status": "success"
    }

    for attempt in range(3):
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=None)) as client:
            try:
                response = await client.post(payload.return_url, json=data)
                response.raise_for_status()
                print(response.status_code)
                return JSONResponse(content={"status": "success"})
            except(httpx.HTTPStatusError, httpx.RequestError) as exc:
                if attempt == 2:
                    print(f"Failed to send report: {str(exc)}")
                    return JSONResponse(content={"status": "failed", "error": str(exc)})
                await asyncio.sleep(2)
