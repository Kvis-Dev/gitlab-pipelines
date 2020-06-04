import os

from dotenv import load_dotenv

load_dotenv()

QUERY_TIME = int(os.getenv("QUERY_TIME"))  # every 2 min
GITLAB_URL = os.getenv("GITLAB_URL")
GITLAB_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")
USERNAME = list(os.getenv("USERNAME").split(','))  # use __all__ to track all events
API_KEY = os.getenv("API_KEY")
PIPE_LIMIT = 5
COLORS = {
    "canceled": "#2e2e2e",
    "created": "#a7a7a7",
    "failed": "#db3b21",
    "pending": "#fc9403",
    "preparing": "#a7a7a7",
    "running": "#418cd8",
    "scheduled": "#2e2e2e",
    "success": "#1aaa55",
    "skipped": "#2e2e2e",
}
ICON_SIZE = 20
PIPELINE_ICON_SIZE = 15
BAD_STATUSES = ("failed",)
RUNNING_STATUSES = ("running",)
GOOD_STATUSES = ("success",)
