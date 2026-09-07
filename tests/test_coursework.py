import pytest
from src.models import Aeroplane
from src.storage import JSONSaver, StorageConnector
from src.api import RequestsAPI, NominatimAPI


class TestAeroplane:
    def test_validation_ok(self):
        p = Aeroplane(callsign="ABC123", origin_country="Russia", speed_kmh=800, baro_altitude_m=10000)
        assert p.validate() is True

    def test_validation_negative_altitude(self):
        p = Aeroplane(callsign="ABC123", origin_country="Russia", speed_kmh=800, baro_altitude_m=-100)
        assert p.validate() is False

    def test_validation_empty_callsign(self):
        p = Aeroplane(callsign="", origin_country="Russia", speed_kmh=800, baro_altitude_m=10000)
        assert p.validate() is False

    def test_sort_by_altitude_desc(self):
        planes = [
            Aeroplane("A", "RU", 800, 5000),
            Aeroplane("B", "RU", 900, 12000),
            Aeroplane("C", "RU", 700, 8000),
        ]
        sorted_planes = Aeroplane.sort_by_altitude_desc(planes)
        heights = [p.baro_altitude_m for p in sorted_planes]
        assert heights == [12000, 8000, 5000]

    def test_sort_by_speed_desc(self):
        planes = [
            Aeroplane("A", "RU", 800, 5000),
            Aeroplane("B", "RU", 900, 4000),
            Aeroplane("C", "RU", 700, 6000),
        ]
        sorted_planes = Aeroplane.sort_by_speed_desc(planes)
        speeds = [p.speed_kmh for p in sorted_planes]
        assert speeds == [900, 800, 700]


class TestJSONSaver:
    @pytest.fixture
    def saver(self, tmp_path):
        path = tmp_path / "planes.json"
        yield JSONSaver(str(path))

    def test_add_and_get_all(self, saver):
        plane = Aeroplane("TEST1", "RU", 850, 9000)
        saver.add_aeroplane(plane)
        all_planes = saver.get_all()
        assert len(all_planes) == 1
        assert all_planes[0].callsign == "TEST1"

    def test_delete_by_callsign(self, saver):
        plane = Aeroplane("DEL1", "RU", 850, 9000)
        saver.add_aeroplane(plane)
        ok = saver.delete_aeroplane_by_callsign("DEL1")
        assert ok is True
        assert len(saver.get_all()) == 0

    def test_filter_by_country(self, saver):
        saver.add_aeroplane(Aeroplane("RU1", "Russia", 800, 9000))
        saver.add_aeroplane(Aeroplane("US1", "United States", 900, 11000))
        filtered = saver.filter_by_country("Russia")
        assert len(filtered) == 1
        assert filtered[0].origin_country == "Russia"

    def test_empty_file_handling(self, tmp_path):
        path = tmp_path / "empty.json"
        path.write_text("", encoding="utf-8")
        saver = JSONSaver(str(path))
        assert saver.get_all() == []


class TestNominatimAPI:
    @pytest.mark.integration
    def test_get_country_bbox_valid(self):
        api_client = RequestsAPI(timeout=5)
        nominatim = NominatimAPI(api_client)
        bbox = nominatim.get_country_bbox("Spain")
        assert bbox is not None
        assert len(bbox) == 4
        south, north, west, east = bbox
        assert south < north
        assert west < east

    def test_get_country_bbox_not_found(self):
        api_client = RequestsAPI(timeout=5)
        nominatim = NominatimAPI(api_client)
        bbox = nominatim.get_country_bbox("__NONEXISTENT_COUNTRY__")
        assert bbox is None


class TestStorageInterface:
    def test_abstract_methods_defined(self):
        with pytest.raises(TypeError):
            StorageConnector()  # type: ignore
