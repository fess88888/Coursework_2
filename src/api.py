import abc
import requests
from typing import Any, Dict, List, Optional


class BaseAPI(abc.ABC):
    @abc.abstractmethod
    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass


class RequestsAPI(BaseAPI):
    """Реализация API через requests с обязательным User-Agent для Nominatim"""

    def __init__(self, timeout: int = 10, user_agent: str = "Coursework_2/1.0"):
        self.timeout = timeout
        self.user_agent = user_agent

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return {"raw": response.text}

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = {"User-Agent": self.user_agent}
        resp = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        return self._handle_response(resp)

    def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = {"User-Agent": self.user_agent}
        resp = requests.post(url, json=data, headers=headers, timeout=self.timeout)
        return self._handle_response(resp)


class NominatimAPI:
    """API Nominatim для получения boundingbox страны"""

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self, api: BaseAPI):
        self._api = api

    def get_country_bbox(self, country_name: str) -> Optional[List[float]]:
        """
        Возвращает [south, north, west, east] или None, если страна не найдена.
        """
        params = {
            "q": country_name,
            "format": "json",
            "limit": 1,
            "addressdetails": 0,
        }
        data = self._api.get(self.BASE_URL, params=params)
        if not data:
            return None
        item = data[0]
        bbox = item.get("boundingbox")
        if not bbox or len(bbox) != 4:
            return None
        return [float(x) for x in bbox]


class OpenSkyAPI:
    """API OpenSky Network для получения самолётов в прямоугольнике"""

    BASE_URL = "https://opensky-network.org/api/states/all"

    def __init__(self, api: BaseAPI):
        self._api = api

    def get_states_in_bbox(self, bbox: List[float]) -> List[Dict[str, Any]]:
        """
        bbox: [min_lat, max_lat, min_lon, max_lon]
        OpenSky ожидает именно такой порядок.
        Nominatim возвращает [south, north, west, east], т.е. [min_lat, max_lat, min_lon, max_lon].
        """
        min_lat, max_lat, min_lon, max_lon = bbox
        params = {
            "lamin": min_lat,
            "lamax": max_lat,
            "lomin": min_lon,
            "lomax": max_lon,
        }
        data = self._api.get(self.BASE_URL, params=params)
        states = data.get("states", [])
        if not states:
            return []
        result = []
        for s in states:
            if len(s) < 8:
                continue
            result.append({
                "icao24": s[0],
                "callsign": s[1],
                "origin_country": s[2],
                "last_contact": s[4],
                "longitude": s[5],
                "latitude": s[6],
                "baro_altitude": s[7],
                "on_ground": s[8],
                "velocity": s[9],
            })
        return result