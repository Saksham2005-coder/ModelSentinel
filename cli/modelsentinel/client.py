import requests
from requests.exceptions import RequestException, Timeout
from .config import config
from .errors import APIError, NotFoundError, RejectedOperationError, GateFailureError

class ModelSentinelClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.API_URL
        self.timeout = config.TIMEOUT
        self.session = requests.Session()
        self._load_auth()

    def _load_auth(self):
        import os
        import json
        from pathlib import Path
        token = os.environ.get("MODELSENTINEL_TOKEN")
        if not token:
            config_path = Path.home() / ".modelsentinel" / "auth.json"
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        data = json.load(f)
                        token = data.get("access_token")
                except Exception:
                    pass
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _handle_response(self, response: requests.Response):
        try:
            data = response.json()
        except ValueError:
            data = response.text

        if response.status_code == 404:
            detail = data.get("detail", "Resource not found") if isinstance(data, dict) else data
            raise NotFoundError(f"{detail}")
            
        if response.status_code == 401:
            detail = data.get("detail", "Unauthenticated") if isinstance(data, dict) else data
            raise APIError(f"Authentication failed (401): {detail}")
            
        if response.status_code == 403:
            detail = data.get("detail", "Forbidden") if isinstance(data, dict) else data
            raise APIError(f"Authorization denied (403): {detail}")
        
        # Determine if it's a specific gate failure or generic bad request
        if response.status_code in (400, 422):
            detail = data.get("detail", str(data)) if isinstance(data, dict) else data
            if "validation failed" in str(detail).lower() or "policy" in str(detail).lower():
                raise GateFailureError(f"Validation/Policy Gate Failure: {detail}")
            raise RejectedOperationError(f"Operation rejected: {detail}")

        if response.status_code >= 500:
            raise APIError(f"Backend error ({response.status_code})")

        response.raise_for_status()
        return data

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            res = self.session.request(method, url, timeout=self.timeout, **kwargs)
            return self._handle_response(res)
        except Timeout:
            raise APIError(f"Request to {url} timed out after {self.timeout}s.")
        except RequestException as e:
            raise APIError(f"Unable to connect to ModelSentinel API at {self.base_url}.\nDetails: {str(e)}")

    def get(self, endpoint: str, params=None):
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, json=None, files=None):
        return self._request("POST", endpoint, json=json, files=files)

client = ModelSentinelClient()
