# =========================================================
# imports
# =========================================================

import os
import threading
import time
from datetime import datetime
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv

# =========================================================
# constants
# =========================================================

load_dotenv(Path(__file__).parent / ".env")

CREDENTIALS_PATH = Path(os.environ["CREDENTIALS_PATH"]).expanduser()

API = "https://api2.arduino.cc/iot"
POLL_SECONDS = 0.5

# =========================================================
# source
# =========================================================


class Source:
    """a poller pushing a thing's fresh values"""

    def __init__(self, push, names, thing_id, with_timestamps=True):
        """hold the target thing and the push"""
        self._push = push
        self._names = names
        self._thing_id = thing_id
        self._with_timestamps = with_timestamps
        self._seen = {}

    # =========================================================
    # start
    # =========================================================

    def start(self):
        """poll on a background thread"""
        thread = threading.Thread(
            target=self._poll,
            daemon=True,
        )
        thread.start()

    # =========================================================
    # poll
    # =========================================================

    def _poll(self):
        """push each fresh value forever"""
        headers = self._headers()

        while True:
            # properties
            properties = requests.get(
                f"{API}/v2/things/{self._thing_id}/properties",
                headers=headers,
            ).json()

            # push
            for prop in properties:
                self._handle(prop)

            time.sleep(POLL_SECONDS)

    def _handle(self, prop):
        """push one property when it is fresh"""
        name = prop["name"]
        updated = prop["value_updated_at"]

        # skip
        if name not in self._names:
            return
        if self._seen.get(name) == updated:
            return

        # fresh
        self._seen[name] = updated
        timestamp = None
        if self._with_timestamps:
            timestamp = self._timestamp(updated)
        self._push(
            name,
            prop["last_value"],
            timestamp=timestamp,
        )

    def _timestamp(self, updated):
        """the cloud's sample time, shifted local"""
        timestamp = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        return timestamp.astimezone().replace(tzinfo=None)

    def _headers(self):
        """an authorization header from the cloud credentials"""
        credentials = yaml.safe_load(CREDENTIALS_PATH.read_text())
        response = requests.post(
            f"{API}/v1/clients/token",
            data={
                "grant_type": "client_credentials",
                "client_id": credentials["client"],
                "client_secret": credentials["secret"],
                "audience": API,
            },
        )
        return {"Authorization": f"Bearer {response.json()['access_token']}"}
