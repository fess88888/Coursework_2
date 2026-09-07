from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Aeroplane:
    callsign: str
    origin_country: str
    speed_kmh: float
    baro_altitude_m: float

    # Дополнительные атрибуты (всего >=4)
    icao24: Optional[str] = None
    last_contact: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @classmethod
    def from_opensky_state(cls, state: dict) -> "Aeroplane":
        """Создаёт Aeroplane из ответа OpenSky"""
        callsign = (state.get("callsign") or "").strip() or "UNKNOWN"
        origin_country = (state.get("origin_country") or "").strip() or "Unknown"
        speed = state.get("velocity")  # OpenSky отдаёт скорость в м/с
        alt = state.get("baro_altitude")

        speed_kmh = float(speed * 3.6) if speed is not None else 0.0
        alt_m = float(alt) if alt is not None else 0.0

        return cls(
            callsign=callsign,
            origin_country=origin_country,
            speed_kmh=speed_kmh,
            baro_altitude_m=alt_m,
            icao24=state.get("icao24"),
            last_contact=state.get("last_contact"),
            latitude=state.get("latitude"),
            longitude=state.get("longitude"),
        )

    @staticmethod
    def cast_to_object_list(states: List[dict]) -> List["Aeroplane"]:
        return [Aeroplane.from_opensky_state(s) for s in states]

    def validate(self) -> bool:
        """Валидирует атрибуты. Возвращает True, если всё ок."""
        if not self.callsign or not self.callsign.strip():
            return False
        if self.speed_kmh < 0:
            return False
        if self.baro_altitude_m < 0:
            return False
        return True

    # Сравнение по высоте
    def __lt__(self, other: "Aeroplane") -> bool:
        return self.baro_altitude_m < other.baro_altitude_m

    def __le__(self, other: "Aeroplane") -> bool:
        return self.baro_altitude_m <= other.baro_altitude_m

    def __gt__(self, other: "Aeroplane") -> bool:
        return self.baro_altitude_m > other.baro_altitude_m

    def __ge__(self, other: "Aeroplane") -> bool:
        return self.baro_altitude_m >= other.baro_altitude_m

    # Для сравнения по скорости можно сделать отдельный ключ сортировки
    @staticmethod
    def sort_by_speed_desc(planes: List["Aeroplane"]) -> List["Aeroplane"]:
        return sorted(planes, key=lambda p: p.speed_kmh, reverse=True)

    @staticmethod
    def sort_by_altitude_desc(planes: List["Aeroplane"]) -> List["Aeroplane"]:
        return sorted(planes, key=lambda p: p.baro_altitude_m, reverse=True)