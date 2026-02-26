import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

retry_strategy = Retry(
    total=10,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
    raise_on_status=False,
)

adapter = HTTPAdapter(max_retries=retry_strategy)
http_session = requests.Session()
http_session.mount("http://", adapter)
http_session.mount("https://", adapter)
