from fastapi import FastAPI, Query, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from typing import List, Optional
import json

app = FastAPI()

with open("rdu-weather-history.json", "r") as file:
    weather_data = json.load(file)

# Compteur de requêtes
request_counter = {
    "get_weather_by_date": 0,
    "filter_by_precipitation": 0,
    "filter_by_temperature": 0,
    "add_date": 0,
    "delete_date": 0,
    "update_date": 0,
}


@app.get("/weather")
async def get_weather_by_date(
    start_date: str = Query(..., description="Date de début"),
    end_date: str = Query(..., description="Date de fin")
) -> List[dict]:
    request_counter["get_weather_by_date"] += 1
    filtered_data = [data for data in weather_data if start_date <= data["date"] <= end_date]
    return filtered_data


@app.get("/filter/precipitation")
async def filter_by_precipitation(
    min_precipitation: float = Query(..., description="Précipitation minimale"),
    max_precipitation: float = Query(..., description="Précipitation maximale")
) -> List[dict]:
    request_counter["filter_by_precipitation"] += 1
    filtered_data = [data for data in weather_data if min_precipitation <= data["prcp"] <= max_precipitation]
    return filtered_data


@app.get("/filter/temperature")
async def filter_by_temperature(
    min_temperature: float = Query(..., description="Température minimale"),
    max_temperature: float = Query(..., description="Température maximale")
) -> List[dict]:
    request_counter["filter_by_temperature"] += 1
    filtered_data = [data for data in weather_data if min_temperature <= data["tmin"] <= max_temperature]
    return filtered_data


@app.post("/add_date")
async def add_date(date: str, tmin: float, tmax: float, prcp: float, snow: float, snwd: float, awnd: float):
    request_counter["add_date"] += 1
    new_entry = {
        "date": date,
        "tmin": tmin,
        "tmax": tmax,
        "prcp": prcp,
        "snow": snow,
        "snwd": snwd,
        "awnd": awnd
    }
    weather_data.append(new_entry)
    with open("rdu-weather-history.json", "w") as file:
        json.dump(weather_data, file, indent=4)
    return {"message": "Données ajoutées avec succès"}


@app.delete("/delete_date")
async def delete_date(date: str):
    request_counter["delete_date"] += 1
    for entry in weather_data:
        if entry["date"] == date:
            weather_data.remove(entry)
            with open("rdu-weather-history.json", "w") as file:
                json.dump(weather_data, file, indent=4)
            return {"message": f"Données pour la date {date} supprimées avec succès"}
    raise HTTPException(status_code=404, detail=f"Données pour la date {date} non trouvées")


@app.put("/update_date")
async def update_date(
    date: str,
    tmin: Optional[float] = None,
    tmax: Optional[float] = None,
    prcp: Optional[float] = None,
    snow: Optional[float] = None,
    snwd: Optional[float] = None,
    awnd: Optional[float] = None
):
    request_counter["update_date"] += 1
    updated = False
    for entry in weather_data:
        if entry["date"] == date:
            if tmin is not None:
                entry["tmin"] = tmin
            if tmax is not None:
                entry["tmax"] = tmax
            if prcp is not None:
                entry["prcp"] = prcp
            if snow is not None:
                entry["snow"] = snow
            if snwd is not None:
                entry["snwd"] = snwd
            if awnd is not None:
                entry["awnd"] = awnd
            updated = True
            with open("rdu-weather-history.json", "w") as file:
                json.dump(weather_data, file, indent=4)
            break

    if updated:
        return {"message": f"Données pour la date {date} mises à jour avec succès"}
    else:
        raise HTTPException(status_code=404, detail=f"Données pour la date {date} non trouvées")


@app.get("/request_count")
async def get_request_count():
    return request_counter

@app.get("/docs")
async def get_swagger():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Documentation")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)