# =========================================================
# imports
# =========================================================

import logging
from pathlib import Path

from dashboard import Dashboard
from dotenv import load_dotenv

# =========================================================
# constants
# =========================================================

load_dotenv(Path(__file__).parent / ".env")

# =========================================================
# execution
# =========================================================

if __name__ == "__main__":
    # logging
    log = logging.getLogger("memory")
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler())

    # quiet
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    # dashboard
    dashboard = Dashboard(
        source={
            "name": "arduino",
            "thing_id": "b993d89a-b12c-40ca-8abf-aadb771d6cb1",
            "names": ["accelerometer_x", "accelerometer_y", "accelerometer_z"],
        },
        methods={
            "reduce": "minmax",
            "timestamps": True,
            "leading": "now",
        },
        settings={
            "title": "Smartphone Accelerometer",
        },
    )

    # run
    dashboard.run()
