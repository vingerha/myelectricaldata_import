import datetime
import json
import traceback
from os import environ, getenv

import __main__ as app

from config import URL
from dependencies import *
from models.config import get_version
from models.log import Log
from models.query import Query


class Status:

    def __init__(self, headers=None):
        self.url = URL
        self.headers = headers

    def ping(self):

        target = f"{self.url}/ping"
        status = {
            "version": get_version(),
            "status": False,
            "information": "MyElectricalData injoignable.",
        }
        try:
            response = Query(endpoint=target, headers=self.headers).get()
            if hasattr(response, "status_code") and response.status_code == 200:
                status = json.loads(response.text)
                for key, value in status.items():
                    app.LOG.log(f"{key}: {value}")
                status["version"] = get_version()
                return status
            else:
                return status
        except LookupError:
            return status

    def status(self, usage_point_id):
        usage_point_id_config = app.DB.get_usage_point(usage_point_id)
        target = f"{self.url}/valid_access/{usage_point_id}"
        if hasattr(usage_point_id_config, "cache") and usage_point_id_config.cache:
            target += "/cache"
        response = Query(endpoint=target, headers=self.headers).get()
        if response:
            status = json.loads(response.text)
            if response.status_code == 200:
                try:
                    for key, value in status.items():
                        app.LOG.log(f"{key}: {value}")
                    app.DB.usage_point_update(
                        usage_point_id,
                        consentement_expiration=datetime.datetime.strptime(status["consent_expiration_date"], "%Y-%m-%dT%H:%M:%S"),
                        # last_call=datetime.datetime.strptime(status["last_call"], "%Y-%m-%dT%H:%M:%S.%f"),
                        call_number=status["call_number"],
                        quota_limit=status["quota_limit"],
                        quota_reached=status["quota_reached"],
                        quota_reset_at=datetime.datetime.strptime(status["quota_reset_at"], "%Y-%m-%dT%H:%M:%S.%f"),
                        ban=status["ban"]
                    )
                    return status
                except Exception as e:
                    if "DEBUG" in environ and getenv("DEBUG"):
                        traceback.print_exc()
                    app.LOG.error(e)
                    return {
                        "error": True,
                        "description": "Erreur lors de la récupération du statut du compte."
                    }
            else:
                if "DEBUG" in environ and getenv("DEBUG"):
                    traceback.print_exc()
                app.LOG.error(status["detail"])
                return {
                    "error": True,
                    "description": status["detail"]
                }
        else:
            if "DEBUG" in environ and getenv("DEBUG"):
                traceback.print_exc()
            return {
                "error": True,
                "description": "MyElectricalData indisponible."
            }
