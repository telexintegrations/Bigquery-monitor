from google.cloud import bigquery
from google.oauth2 import service_account, credentials
import asyncio
import json

async def get_daily_slot_utilization(client:bigquery.Client) -> dict:
    """
    Get daily slot utilization
    """
    query = f"""
    SELECT
        FORMAT_DATE('%A', DATE_TRUNC(end_time, DAY)) as day_of_week,
        SUM(TIMESTAMP_DIFF(end_time, start_time, SECOND)) as total_daily_slot_ms
    FROM
        `region-us`.INFORMATION_SCHEMA.JOBS
    WHERE
        state = "DONE"
        AND DATE_TRUNC(end_time, DAY) BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY) AND CURRENT_TIMESTAMP()
        AND (statement_type != "SCRIPT" OR statement_type IS NULL)
    GROUP BY
        day_of_week
    ORDER BY
        day_of_week DESC
    LIMIT 2
    """
    query_job = client.query(query)
    results = query_job.result()
    daily_utilization = {}
    if not results:
        return daily_utilization
    listed_results = []
    for row in results:
        daily_utilization[row[0]] = row[1]
        listed_results.append(int(row[1
        ]))
    daily_utilization["percentage change"] = int(((listed_results[1] - listed_results[0]) / listed_results[0]) * 100)     
    return daily_utilization

# async def get_performance_insights(client: bigquery.Client) -> dict:
#     """
#     Get performance insights for completed jobs
#     """
#     query = f"""
#     SELECT
#         job_id,
#         job_type,
#         total_bytes_processed,
#         statement_type,
#         TIMESTAMP_DIFF(end_time, start_time, SECOND) as job_duration_seconds,
#         COALESCE(query_info.resource_warning, "N/A") as resource_warning,
#         query_info.performance_insights
#     FROM
#         `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
#     WHERE
#         end_time BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY) AND CURRENT_TIMESTAMP()
#         AND error_result IS NULL
#     ORDER BY
#         creation_time DESC
#     """
#     query_job = client.query(query)
#     results = query_job.result()
#     performance_insights = {}
#     if not results:
#         return performance_insights
#     performance_insights = {}
#     for row in results:
#         performance_insights[row[0]] = {
#             "job_type": row[1],
#             "total_bytes_processed": row[2],
#             "statement_type": row[3],
#             "job_duration_seconds": row[4],
#             "resource_warning": row[5],
#             "performance_insights": row[6]
#         }   
#     return performance_insights

async def get_run_errors(client: bigquery.Client) -> dict:
    """
    Get daily job run errors
    """
    query = f"""
    SELECT
        job_id,
        job_type,
        error_result,
        state,
        end_time,
        priority,
        total_bytes_processed,
        TIMESTAMP_DIFF(end_time, start_time, SECOND) as duration_seconds,
        user_email,
        query_info.resource_warning
    FROM
        `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
    WHERE
        end_time BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY) AND CURRENT_TIMESTAMP()
        AND error_result IS NOT NULL
    ORDER BY
        creation_time DESC
    """
    query_job = client.query(query)
    results = query_job.result()
    error_reports = {}
    if not results:
        return error_reports
    for row in results:
        error_reports[row[0]] = {
            "job_type": row[1],
            "error_result": row[2],
            "state": row[3],
            "end_time": row[4],
            "priority": row[5],
            "total_bytes_processed": row[6],
            "duration_seconds": row[7],
            "user_email": row[8],
            "resource_warning": row[9]
        }
    return error_reports

async def main():
    reports = {}
    reports["Daily slots usage in seconds"], reports["Error report by JobID"] = await asyncio.gather(get_daily_slot_utilization(client), get_run_errors(client))
    
    print(json.dumps(reports, indent=2, default=str))

if __name__ == "__main__":
    with open("./sa_key.json") as json_file:
        json_service_key = json.load(json_file)

    creds = service_account.Credentials.from_service_account_info(json_service_key)
    scoped_credentials = creds.with_scopes(['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/bigquery'])
    project_id = "hng13-backend-projects"

    client = bigquery.Client(credentials=scoped_credentials, project=project_id)
    asyncio.run(main())
    
