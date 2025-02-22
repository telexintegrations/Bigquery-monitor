integration_json = {
  "data": {
    "date": {
      "created_at": "2025-02-18",
      "updated_at": "2025-02-18"
    },
    "descriptions": {
      "app_name": "BigQuery Performance and Health Monitor",
      "app_description": "Monitor and report spikes in day-on-day execution stats of BigQuery jobs.",
      "app_logo": "https://imgur.com/a/BsoJdfa",
      "app_url": "",
      "background_color": "#065a96"
    },
    "integration_category": "Monitoring & Logging",
    "integration_type": "interval",
    "is_active": True,
    "author": "Sulaimon Salako",
    "key_features": [
      "Report spike in job (qurey) execution stats",
      "Report spike in resource utilization."
    ],
    "settings": [
      {
        "label": "Interval",
        "type": "text",
        "required": True,
        "default": "*/2 * * * *"
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
    "tick_url": "",
    "target_url": ""
  }
}