from fastapi.testclient import TestClient
from bq_functions.bigquery_funcs import get_daily_slot_utilization, get_run_errors
from google.cloud import bigquery
from models.models import ReportPayload, Setting, ServiceAccountKey, level_dict
from main import app
from unittest.mock import Mock, AsyncMock, patch
import asyncio
import json
import pytest

# Create my fixtures for the tests
@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_service_account_key():
    return {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "test-key-id",
        "private_key": "test-private-key",
        "client_email": "test@test.com",
        "client_id": "test-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test"
    }

@pytest.fixture
def mock_payload():
    return ReportPayload(
        channel_id="test-channel",
        return_url="http://test.com/webhook",
        settings=[
            Setting(label="Setting1", type="string", required=True, default="value1"),
            Setting(label="Service Account Key", type="string", required=True, 
                   default=json.dumps(ServiceAccountKey(
                       type="service_account",
                       project_id="test-project",
                       private_key_id="test-key-id",
                       private_key="test-private-key",
                       client_email="test@test.com",
                       client_id="test-client-id",
                       auth_uri="https://accounts.google.com/o/oauth2/auth",
                       token_uri="https://oauth2.googleapis.com/token",
                       auth_provider_x509_cert_url="https://www.googleapis.com/oauth2/v1/certs",
                       client_x509_cert_url="https://www.googleapis.com/robot/v1/metadata/x509/test"
                   ).dict())),
            Setting(label="Setting3", type="string", required=True, default="value3"),
            Setting(label="Project ID", type="string", required=True, default="test-project"),
            Setting(label="Region", type="string", required=True, default="us")
        ]
    )

@pytest.fixture
def mock_bigquery_results():
    class MockRow:
        def __init__(self, values):
            self._values = values
        def __getitem__(self, index):
            return self._values[index]
    
    return [
        MockRow(["Monday", 1000]),
        MockRow(["Tuesday", 2000])
    ]

# Define tests

def test_level_dict():
    test_report = {
        "Category1": {
            "SubKey1": "Value1",
            "SubKey2": "Value2"
        },
        "Category2": "Value3"
    }

    result = level_dict(test_report)

    assert isinstance(result, str)
    assert "Category1" in result
    assert "SubKey1" in result
    assert "Value3" in result
    

def test_get_integration_json(test_client):
    reponse = test_client.get("/integration.json")
    assert reponse.status_code == 200
    data = reponse.json()
    assert "data" in data
    assert data["data"]["descriptions"]["app_url"] == "http://testserver"
    assert data["data"]["tick_url"] == "http://testserver/tick" 
    assert data["data"]["is_active"] == True
    assert data["data"]["integration_category"] == "Monitoring & Logging"
    assert data["data"]["integration_type"] == "interval"
    assert data["data"]["author"] == "Sulaimon Salako"

# def test_send_reports():
#     response = client.post("/tick")

# Test BigQuery utility functions
@pytest.mark.asyncio
async def test_get_daily_slot_utilization():
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result = Mock(return_value=[
        Mock(spec=list, __getitem__=lambda self, index: ["Monday", 1000][index]),
        Mock(spec=list, __getitem__=lambda self, index: ["Tuesday", 2000][index])
    ])

    mock_client.query = Mock(return_value=mock_query_job)

    result = await get_daily_slot_utilization(mock_client, region="us")

    assert isinstance(result, dict)
    assert "percentage change" in result

@pytest.mark.asyncio
async def test_get_run_errors():
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result = Mock(return_value=[
        Mock(spec=list, __getitem__=lambda self, index: ["job_id", "job_type", "error_result", "state", "end_time", "priority", "total_bytes_processed", "duration_seconds", "user_email", "resource_warning"][index])
    ]) 

    mock_client.query = Mock(return_value=mock_query_job)

    result = await get_run_errors(mock_client, region="us")

    assert isinstance(result, dict)
    assert "job_id" in result
    assert "error_result" in result["job_id"]