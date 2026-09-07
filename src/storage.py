import abc
import json
from pathlib import Path
from typing import List, Dict, Any
from .models import Aeroplane

class StorageConnector(abc.ABC):
    @abc.abstractmethod
    def add_aeroplane(self, plane: Aeroplane) -> None:
        pass

    @abc.abstractmethod
    def delete_aeroplane_by_callsign(self, callsign: str) -> bool:
        pass

    @abc.abstractmethod
    def get_all(self) -> List[Aeroplane]:
        pass

    @abc.abstractmethod
    def filter_by_country(self, country: str) -> List[Aeroplane]:
        pass

    @abc.abstractmethod
    def clear(self) -> None:
        pass


class JSONSaver(StorageConnector):
    def __init__(self, path: str = "data/planes.json"):
        self.path = Path(path)
        self._ensure_file()

    def _ensure_file(self) -> None:
        # Создаём папку, если её нет
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load_data(self) -> List[Dict[str, Any]]:
        try:
            text = self.path.read_text(encoding="utf-8")
            data = json.loads(text)
            if not isinstance(data, list):
                return []
            return data
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_aeroplane(self, plane: Aeroplane) -> None:
        data = self._load_data()
        data.append({
            "callsign": plane.callsign,
            "origin_country": plane.origin_country,
            "speed_kmh": plane.speed_kmh,
            "baro_altitude_m": plane.baro_altitude_m,
            "icao24": plane.icao24,
            "last_contact": plane.last_contact,
            "latitude": plane.latitude,
            "longitude": plane.longitude,
        })
        self._save_data(data)

    def delete_aeroplane_by_callsign(self, callsign: str) -> bool:
        data = self._load_data()
        before = len(data)
        data = [d for d in data if d.get("callsign") != callsign]
        if len(data) == before:
            return False
        self._save_data(data)
        return True

    def get_all(self) -> List[Aeroplane]:
        data = self._load_data()
        planes = []
        for d in data:
            p = Aeroplane(
                callsign=d["callsign"],
                origin_country=d["origin_country"],
                speed_kmh=float(d["speed_kmh"]),
                baro_altitude_m=float(d["baro_altitude_m"]),
                icao24=d.get("icao24"),
                last_contact=d.get("last_contact"),
                latitude=d.get("latitude"),
                longitude=d.get("longitude"),
            )
            if p.validate():
                planes.append(p)
        return planes

    def filter_by_country(self, country: str) -> List[Aeroplane]:
        planes = self.get_all()
        country_lower = country.lower()
        return [p for p in planes if p.origin_country.lower() == country_lower]

    def clear(self) -> None:
        self.path.write_text("[]", encoding="utf-8")


class DbStorageStub(StorageConnector):
    """Заглушка для интеграции с БД. Методы реализованы, но ничего не делают."""

    def __init__(self, conn_str: str):
        self.conn_str = conn_str

    def add_aeroplane(self, plane: Aeroplane) -> None:
        # TODO: реализовать вставку в БД
        pass

    def delete_aeroplane_by_callsign(self, callsign: str) -> bool:
        # TODO: реализовать удаление из БД
        return False

    def get_all(self) -> List[Aeroplane]:
        # TODO: вернуть все записи из БД
        return []

    def filter_by_country(self, country: str) -> List[Aeroplane]:
        # TODO: фильтрация по стране в БД
        return []

    def clear(self) -> None:
        # TODO: очистить таблицу
        pass
