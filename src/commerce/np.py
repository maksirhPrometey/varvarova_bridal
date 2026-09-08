import json
from functools import lru_cache
from pathlib import Path


FIXTURE = Path(__file__).resolve().parent / 'data' / 'np_stub.json'


@lru_cache(maxsize=1)
def load_np_stub() -> dict:
    return json.loads(FIXTURE.read_text(encoding='utf-8'))


def np_cities(query: str = '') -> list[dict]:
    needle = query.strip().lower()
    cities = load_np_stub().get('cities', [])
    if not needle:
        return cities[:8]
    return [city for city in cities if needle in city['name'].lower()][:8]


def np_warehouses(city_ref: str) -> list[dict]:
    if not city_ref:
        return []
    return list(load_np_stub().get('warehouses', {}).get(city_ref, []))


def resolve_city(ref: str, name: str) -> dict | None:
    ref = (ref or '').strip()
    name = (name or '').strip()
    for city in load_np_stub().get('cities', []):
        if ref and city['ref'] == ref:
            return city
        if name and city['name'].lower() == name.lower():
            return city
    return None


def resolve_warehouse(city_ref: str, ref: str, name: str) -> dict | None:
    ref = (ref or '').strip()
    name = (name or '').strip()
    for warehouse in np_warehouses(city_ref):
        if ref and warehouse['ref'] == ref:
            return warehouse
        if name and warehouse['name'] == name:
            return warehouse
    return None
