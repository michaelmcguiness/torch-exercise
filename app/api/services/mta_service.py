import xml.etree.ElementTree as ET
import requests
import datetime
import threading

MTA_STATUS_ENDPOINT = "http://web.mta.info/status/serviceStatus.txt"


class MTAService:
    """
    Data Model for statuses of MTA services
    -----------------------------------------
    It stores, updates and retrieves data from a map ('line_map') of each service line (i.e. '123, 'BDFM', etc.)
    The value for each line is a dict with 4 properties: 1. is_delayed, 2. uptime, 3. downtime, and 4. last_update
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.line_map = {}
        self.update()

    def update(self) -> None:
        """fetch line statuses and update internal 'line_map'"""
        line_statuses = self._get_latest_line_statuses()
        with self.lock:
            # update line_info map with fetched service statuses
            for name, status in line_statuses.items():
                self._update_line(name.lower(), status)

    def get_is_delayed(self, line: str) -> bool:
        """Returns delay status of a line (true if delayed, else false)"""
        with self.lock:
            return self.line_map[line.lower()]["is_delayed"]

    def get_uptime(self, line: str) -> float:
        """
        Returns the 'uptime' for a given service since inception
        'uptime' defined as '1 - (total_time_delayed/total_time)'
        """
        with self.lock:
            name = line.lower()
            uptime = self.line_map[name]["uptime"]
            downtime = self.line_map[name]["downtime"]
            time_since_update = (datetime.datetime.now() - self.line_map[name]["last_update"]).total_seconds()

            # if delayed, add time since last update to downtime (else add to uptime)
            if self.line_map[name]["is_delayed"]:
                downtime = downtime + time_since_update
            else:
                uptime = uptime + time_since_update

            return uptime / (downtime + uptime)

    def line_exists(self, line: str) -> bool:
        """Helper method used by controller to verify line in line_map"""
        if line.lower() in self.line_map:
            return True
        else:
            return False

    @classmethod
    def _get_latest_line_statuses(cls) -> dict:
        """Helper method to fetch and parse service statuses from MTA Website and returns service_statuses dict"""
        response = requests.get(MTA_STATUS_ENDPOINT, allow_redirects=True)
        root = ET.fromstring(response.text)
        line_statuses = {}
        for child in root[2]:
            name = ""
            status = ""
            for line in child:
                if line.tag == "name":
                    name = line.text
                if line.tag == "status":
                    status = line.text
            line_statuses[name] = status

        return line_statuses

    def _update_line(self, name: str, line: str) -> None:
        """Helper method that takes name and ser"""
        line_is_delayed = line.lower() not in ["weekday service", "weekend service"]

        if name in self.line_map:
            now = datetime.datetime.now()
            time_since_update = (now - self.line_map[name]["last_update"]).total_seconds()
            if self.line_map[name]["is_delayed"] is True:
                new_downtime = self.line_map[name]["downtime"] + time_since_update
                self.line_map[name]["downtime"] = new_downtime
                self.line_map[name]["last_update"] = now
            else:
                new_uptime = self.line_map[name]["uptime"] + time_since_update
                self.line_map[name]["uptime"] = new_uptime
                self.line_map[name]["last_update"] = now

            # print status messages if delayed -> not delayed or not delayed -> delayed
            if self.line_map[name]["is_delayed"] and (not line_is_delayed):
                print(f"Line {name} is now recovered")
            if (not self.line_map[name]["is_delayed"]) and line_is_delayed:
                print(f"Line {name} is experiencing delays")

            # update is_delayed status
            self.line_map[name]["is_delayed"] = line_is_delayed
        else:
            self.line_map[name] = {
                "is_delayed": line_is_delayed,
                "uptime": 0,
                "downtime": 0,
                "last_update": datetime.datetime.now()
            }