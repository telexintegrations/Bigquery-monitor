# BigQuery Monitor (Telex Integration)

## Overview

This project is a Telex "interval integration" for Google's BigQuery (a distributed data querying and processing engine). It allows team to monitor their Big Query performance and resource utilization on a day-to-day basis. Everyday at 11:59pm (this can be changed to suit any other use case), it fetches data on job runs (like a database query) that failed as well as the details of the error. It also collects information on the amount of slot time (resource usage) consumed for the day and calculates the day-on-day percentage change. This helps team detect usage spikes (a potential indicator of a problematic job) and increase provisioning where necessary. 

## Features

- 🔍 Daily report on job run errors
- 📝 Daily updates on BigQuery resource utilization
- 🔒 CORS middleware enabled

## Project Structures

```
Bigquery-monitor/
├── bq_functions/
│   ├── bigquery_funcs.py/ # Wrapper functions for BigQuery DB queries
│   │ 
├── integration_json/
│   └── telex_json.py           # JSON file configuration that Telex needs to configure the app
├── tests/
│   ├── __init__.py
│   └── test_app.py       # API endpoint tests
├── models/
│   │
│   └── models.py           # Pydantic data models
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
└── README.md
```

## Technologies Used

- Python 3.12
- FastAPI
- Pydantic
- Google Cloud SDK
- uvicorn

## Installation

1. Clone the repository:

```bash
git clone https://github.com/telexintegrations/Bigquery-monitor
cd Bigquery-monitor
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application (Testing)

### Authentication with Google Cloud Services

This integration leverages the Google Cloud API to collect data from Google Cloud Services (GCS). Therefore, it needs to authenticate with GCS, using a service account key, via the `gcloud API`. This key can be generated via the Google Cloud Console within the `Service Accounts` interface. Note, however, that the service account must have the `BigQuery/Admin` role permissions enabled. 

Paste this key within the `telex_json.py` file as the value for the `default` key under the `Service Account Key` label. In addition, the integration requires a GCS `project ID` and `region`. Default values can be set within the `telex_json.py` file.

1. Start the server:

```bash
uvicorn main:app 
```

2. Access the API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Books

- `GET /integration.json` - Returns the JSON configuration file that the integration provides to Telex
- `POST /tick` - Triggers the app to fetch data from BigQuery and send to the designated Telex channel. 

## Running Tests

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository.
