import os

BASE_URL = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com").rstrip("/")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
