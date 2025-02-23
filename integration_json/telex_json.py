integration_json = {
  "data": {
    "date": {
      "created_at": "2025-02-18",
      "updated_at": "2025-02-18"
    },
    "descriptions": {
      "app_name": "BigQuery Monitor",
      "app_description": "Monitor and report daily resource utilization and job run errors in BigQuery.",
      "app_logo": "https://imgur.com/YlkPatz",
      "app_url": "https://bigquery-monitor.onrender.com/",
      "background_color": "#065a96"
    },
    "integration_category": "Monitoring & Logging",
    "integration_type": "interval",
    "is_active": True,
    "author": "Sulaimon Salako",
    "key_features": [
      "Report daily slot utilization, in seconds, and with day-on-day percentage change.",
      "Report job run errors for the day."
    ],
    "settings": [
      {
        "label": "interval",
        "type": "text",
        "required": True,
        "default": "59 23 * * *"
      },
      {
        "label": "Service Account Key",
        "type": "text",
        "required": True,
        "default": ""
      },
      {
        "label": "Sensitivity Level",
        "type": "dropdown",
        "required": True,
        "default": "Low",
        "options": ["High", "Low"]
      },
      {
        "label": "Project ID",
        "type": "text",
        "required": True,
        "default": ""
      },
      {
        "label": "Region",
        "type": "text",
        "required": True,
        "default": "us",
      },
      {
        "label": "Alert Admin",
        "type": "multi-checkbox",
        "required": True,
        "default": "Super-Admin",
        "options": ["Super-Admin", "Admin", "Manager", "Developer"]
      }

    ],
    "tick_url": "https://bigquery-monitor.onrender.com/tick",
    "target_url": ""
  }
}
