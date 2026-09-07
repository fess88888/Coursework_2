import os
from typing import List
from dotenv import load_dotenv
from src.api import NominatimAPI, OpenSkyAPI, RequestsAPI
from src.models import Aeroplane
from src.storage import JSONSaver


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

MAIL = os.getenv("MAIL")

def fetch_planes_for_country(country: str) -> List[Aeroplane]:
    api_client = RequestsAPI(user_agent=f"Coursework_2/1.0 ({MAIL})")
    nominatim = NominatimAPI(api_client)
    opensky = OpenSkyAPI(api_client)

    bbox = nominatim.get_country_bbox(country)
    if not bbox:
        raise ValueError(f"Страна '{country}' не найдена в Nominatim.")

    states = opensky.get_states_in_bbox(bbox)
    planes = Aeroplane.cast_to_object_list(states)
    return [p for p in planes if p.validate()]


def get_top_n_by_altitude(planes: List[Aeroplane], n: int) -> List[Aeroplane]:
    sorted_planes = Aeroplane.sort_by_altitude_desc(planes)
    return sorted_planes[:n]


def filter_by_countries(planes: List[Aeroplane], countries: List[str]) -> List[Aeroplane]:
    countries_lower = [c.lower() for c in countries]
    return [p for p in planes if p.origin_country.lower() in countries_lower]


def parse_altitude_range(range_str: str):
    parts = range_str.replace(",", " ").replace("-", " ").split()
    if len(parts) < 2:
        raise ValueError("Диапазон высот должен содержать минимум два числа.")
    min_alt = float(parts[0])
    max_alt = float(parts[-1])
    if min_alt > max_alt:
        min_alt, max_alt = max_alt, min_alt
    return min_alt, max_alt


def print_planes(planes: List[Aeroplane]) -> None:
    if not planes:
        print("Самолётов не найдено.")
        return
    print(f"{'Callsign':<12} {'Country':<20} {'Speed (km/h)':<14} {'Alt (m)':<10}")
    for p in planes:
        print(f"{p.callsign:<12} {p.origin_country:<20} {p.speed_kmh:<14.1f} {p.baro_altitude_m:<10.0f}")


def user_interaction():
    saver = JSONSaver("data/planes.json")

    while True:
        print("\n--- Меню ---")
        print("1. Получить самолёты по стране (и сохранить в JSON)")
        print("2. Топ N самолётов по высоте")
        print("3. Фильтр по стране регистрации")
        print("4. Фильтр по диапазону высот")
        print("5. Показать все сохранённые самолёты")
        print("6. Удалить самолёт по позывному")
        print("0. Выход")

        choice = input("Выберите пункт: ").strip()

        try:
            if choice == "1":
                country = input("Введите название страны: ").strip()
                if not country:
                    print("Название страны не может быть пустым.")
                    continue
                print("Загрузка данных...")
                planes = fetch_planes_for_country(country)
                print(f"Найдено самолётов: {len(planes)}")
                for p in planes:
                    saver.add_aeroplane(p)
                print_planes(planes)

            elif choice == "2":
                n_str = input("Сколько самолётов в топе (N): ").strip()
                n = int(n_str)
                if n <= 0:
                    print("N должно быть положительным числом.")
                    continue
                planes = saver.get_all()
                top_n = get_top_n_by_altitude(planes, n)
                print(f"\nТоп {n} самолётов по высоте:")
                print_planes(top_n)

            elif choice == "3":
                countries_input = input("Страны для фильтрации (через пробел): ").strip()
                countries = countries_input.split() if countries_input else []
                if not countries:
                    print("Не указаны страны для фильтрации.")
                    continue
                planes = saver.get_all()
                filtered = filter_by_countries(planes, countries)
                print("\nОтфильтрованные самолёты:")
                print_planes(filtered)

            elif choice == "4":
                range_str = input("Диапазон высот (например, 10000 15000): ").strip()
                min_alt, max_alt = parse_altitude_range(range_str)
                planes = saver.get_all()
                filtered = [p for p in planes if min_alt <= p.baro_altitude_m <= max_alt]
                print(f"\nСамолёты с высотой от {min_alt} до {max_alt} м:")
                print_planes(filtered)

            elif choice == "5":
                planes = saver.get_all()
                print("\nВсе сохранённые самолёты:")
                print_planes(planes)

            elif choice == "6":
                callsign = input("Позывной самолёта для удаления: ").strip()
                if not callsign:
                    print("Позывной не может быть пустым.")
                    continue
                ok = saver.delete_aeroplane_by_callsign(callsign)
                if ok:
                    print(f"Самолёт с позывным {callsign} удалён.")
                else:
                    print(f"Самолёт с позывным {callsign} не найден.")

            elif choice == "0":
                print("Выход.")
                break

            else:
                print("Неверный пункт меню.")

        except ValueError as e:
            print(f"Ошибка ввода: {e}")
        except Exception as e:
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    user_interaction()
