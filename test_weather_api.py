import json
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

with open("test_weather_data.json", "r") as file:
    test_weather_data = json.load(file)

def test_get_weather_by_date():
    response = client.get("/weather?start_date=2017-01-01&end_date=2023-01-05")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_filter_by_precipitation():
    response = client.get("/filter/precipitation?min_precipitation=0.0&max_precipitation=1.0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_filter_by_temperature():
    response = client.get("/filter/temperature?min_temperature=0&max_temperature=30")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_add_date():
    new_date_data = {
        "date": "2023-01-10",
        "tmin": 22.0,
        "tmax": 32.0,
        "prcp": 0.3,
        "snow": 0.0,
        "snwd": 0.0,
        "awnd": 6.0
    }
    response = client.post("/add_date", json=new_date_data)
    assert response.status_code == 200, f"Échec de la requête POST : {response.status_code}"
    print(response.json())

def test_delete_date():
    date_to_delete = "2023-01-10"
    response = client.delete(f"/delete_date?date={date_to_delete}")
    if response.status_code == 200:
        assert response.json() == {"message": f"Données pour la date {date_to_delete} supprimées avec succès"}
    else:
        assert response.status_code == 404

def test_update_date():
    date_to_update = "2023-01-01"
    updated_data = {
        "tmin": 22.0,
        "tmax": 32.0,
        "prcp": 0.3,
        "snow": 0.0,
        "snwd": 0.0,
        "awnd": 6.0
    }
    response = client.put(f"/update_date?date={date_to_update}", json=updated_data)
    if response.status_code == 200:
        assert response.json() == {"message": f"Données pour la date {date_to_update} mises à jour avec succès"}
    else:
        assert response.status_code == 404

def test_request_count():
    response = client.get("/request_count")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


if __name__ == "__main__":
    pytest.main()