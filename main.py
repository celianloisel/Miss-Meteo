from fastapi import FastAPI, Query, HTTPException
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


@app.get("/weather-by-date")
async def get_weather_by_date(
        start_date: str = Query(..., description="Date de début"),
        end_date: str = Query(..., description="Date de fin")
) -> List[dict]:
    """
    Récupère les données météorologiques pour une plage de dates spécifiée.

    Args:
        start_date (str): Date de début.
        end_date (str): Date de fin.

    Returns:
        List[dict]: Liste des données météorologiques dans la plage de dates spécifiée.
    """
    request_counter["get_weather_by_date"] += 1
    filtered_data = []

    for data in weather_data:
        if start_date <= data["date"] <= end_date:
            filtered_data.append(data)

    if not filtered_data:
        raise HTTPException(
            status_code=404, detail=f"Aucune donnée météorologique trouvée pour la plage de dates spécifiée.")
    return filtered_data


@app.get("/weather-by-precipitation")
async def filter_by_precipitation(
    min_precipitation: float = Query(...,
                                     description="Précipitation minimale"),
    max_precipitation: float = Query(..., description="Précipitation maximale")
) -> List[dict]:
    """
    Filtre les données météorologiques par plage de précipitations.

    Args:
        min_precipitation (float): Précipitation minimale.
        max_precipitation (float): Précipitation maximale.

    Returns:
        List[dict]: Liste des données météorologiques dans la plage de précipitations spécifiée.
    """
    request_counter["filter_by_precipitation"] += 1
    filtered_data = []

    for data in weather_data:
        if min_precipitation <= data["prcp"] <= max_precipitation:
            filtered_data.append(data)

    if not filtered_data:
        raise HTTPException(
            status_code=404, detail=f"Aucune donnée météorologique trouvée pour la plage de précipitations spécifiée.")

    return filtered_data


@app.get("/weather-by-temperature")
async def filter_by_temperature(
    min_temperature: float = Query(..., description="Température minimale"),
    max_temperature: float = Query(..., description="Température maximale")
) -> List[dict]:
    """
    Filtre les données météorologiques par plage de températures.

    Args:
        min_temperature (float): Température minimale.
        max_temperature (float): Température maximale.

    Returns:
        List[dict]: Liste des données météorologiques dans la plage de températures spécifiée.
    """
    request_counter["filter_by_temperature"] += 1
    filtered_data = []

    for data in weather_data:
        if min_temperature <= data["tmin"] <= max_temperature:
            filtered_data.append(data)

    if not filtered_data:
        raise HTTPException(
            status_code=404, detail=f"Aucune donnée météorologique trouvée pour la plage de températures spécifiée.")

    return filtered_data


@app.post("/add-date")
async def add_date(date: str, tmin: float, tmax: float, prcp: float, snow: float, snwd: float, awnd: float):
    """
    Ajoute de nouvelles données météorologiques pour une date spécifiée.

    Args:
        date (str): Date.
        tmin (float): Température minimale.
        tmax (float): Température maximale.
        prcp (float): Précipitation.
        snow (float): Neige.
        snwd (float): Accumulation de neige.
        awnd (float): Vitesse du vent moyen.

    Returns:
        dict: Message de confirmation ou d'erreur.
    """
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

    try:
        # Ajouter la nouvelle entrée aux données météorologiques
        weather_data.append(new_entry)

        # Sauvegarder les données mises à jour dans le fichier JSON
        with open("rdu-weather-history.json", "w") as file:
            json.dump(weather_data, file, indent=4)

        return {"message": "Données ajoutées avec succès"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de l'ajout des données : {str(e)}")


@app.delete("/delete-date")
async def delete_date(date: str):
    """
    Supprime les données météorologiques pour une date spécifiée.

    Args:
        date (str): Date.

    Returns:
        dict: Message de confirmation ou erreur si la date n'est pas trouvée.
    """
    request_counter["delete_date"] += 1
    for entry in weather_data:
        if entry["date"] == date:
            weather_data.remove(entry)
            with open("rdu-weather-history.json", "w") as file:
                json.dump(weather_data, file, indent=4)
            return {"message": f"Données pour la date {date} supprimées avec succès"}
    raise HTTPException(
        status_code=404, detail=f"Données pour la date {date} non trouvées")


@app.put("/update-date")
async def update_date(
        date: str,
        tmin: Optional[float] = None,
        tmax: Optional[float] = None,
        prcp: Optional[float] = None,
        snow: Optional[float] = None,
        snwd: Optional[float] = None,
        awnd: Optional[float] = None
):
    """
    Met à jour les données météorologiques pour une date spécifiée.

    Args:
        date (str): Date.
        tmin (float): Nouvelle température minimale (optionnelle).
        tmax (float): Nouvelle température maximale (optionnelle).
        prcp (float): Nouvelle précipitation (optionnelle).
        snow (float): Nouvelle quantité de neige (optionnelle).
        snwd (float): Nouvelle accumulation de neige (optionnelle).
        awnd (float): Nouvelle vitesse du vent moyen (optionnelle).

    Returns:
        dict: Message de confirmation ou erreur si la date n'est pas trouvée.
    """
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
        raise HTTPException(
            status_code=404, detail=f"Données pour la date {date} non trouvées")


@app.get("/request-count")
async def get_request_count():
    """
    Récupère le compteur de requêtes pour chaque endpoint.

    Returns:
        dict: Compteur de requêtes pour chaque endpoint.
    """
    try:
        return request_counter
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la récupération du compteur de requêtes : {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
