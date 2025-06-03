from typing import Any
import httpx
import json
from mcp.server.fastmcp import FastMCP

# Inicializa o servidor MCP
mcp = FastMCP("cp-trains")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.infraestruturasdeportugal.pt/",
    "Origin": "https://www.infraestruturasdeportugal.pt",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}


async def get_station_id(station_name: str) -> str:

    """Query the station NodeID via Infraestruturas de Portugal."""
    
    url = f"https://www.infraestruturasdeportugal.pt/negocios-e-servicos/estacao-nome/{station_name}"

    async with httpx.AsyncClient() as client:
        try:            
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            
            # Verify if the response is a valid JSON
            try:
                data = response.json()
            except ValueError as e:
                raise ValueError(f"Invalid response from API for station {station_name}")

            # Verify if data is a list or dictionary
            if not isinstance(data, (list, dict)):
                raise ValueError(f"Invalid response format for station {station_name}")

            # If it's a dictionary, search for the 'response' key
            if isinstance(data, dict):
                stations = data.get("response", [])
            else:
                stations = data

            if not stations:
                raise ValueError(f"No station found with the name {station_name}")

            # Search for the station
            for station in stations:
                if isinstance(station, dict) and station_name.lower() in station.get("Nome", "").lower():
                    node_id = str(station.get("NodeID"))
                    return node_id

            raise ValueError(f"Station {station_name} not found.")

        except httpx.HTTPError as e:
            raise ValueError(f"Error accessing the API: {str(e)}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")


async def get_train_schedule(station_id: str) -> Any:

    """Query the trains that pass through a station in CP."""
    
    url = f"https://www.cp.pt/sites/spring/station/trains?stationId={station_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.cp.pt/",
        "Origin": "https://www.cp.pt",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return []
                
            return data
        except Exception as e:
            raise ValueError(f"Error getting schedules: {str(e)}")


@mcp.tool()
async def train_query(station: str, station_id: str = None) -> str:
    
    """Query the trains that pass through a station in Portugal.

    Args:
        station: Station name (ex: Porto-Campanhã, Lisboa Oriente)
        station_id: Optional station ID from favorites list
    """
    
    try:
        if not station_id:
            station_id = await get_station_id(station)
            
        station_id = str(f"{station_id[:2]}-{station_id[2:].lstrip('0')}")
        
        data = await get_train_schedule(station_id)

        if not data:
            return f"No information available for {station}."

        trains = []
        for train in data:
            delay = train.get("delay")
            origin = train.get("trainOrigin", {}).get("designation", "origin unknown")
            destination = train.get("trainDestination", {}).get("designation", "destination unknown")
            departure = train.get("departureTime", "??:??")
            arrival = train.get("arrivalTime", "??:??")
            number = train.get("trainNumber", "N/A")
            type = train.get("trainService", {}).get("designation", "type unknown")
            platform = train.get("platform", "—")

            if delay is None:
                delay = "0"

            info = (
                f"Comboio {number} ({type})\n"
                f"De: {origin} → Para: {destination}\n"
                f"Partida: {departure} — arrival: {arrival} | platform: {platform} | delay: {delay}"
            )
            trains.append(info)

        return f"trains em {station}:\n\n" + "\n\n---\n\n".join(trains) + "\n\n"

    except Exception as e:
        return f"Error getting data: {str(e)}"

@mcp.tool()
async def add_favorite_station(station: str) -> str:
    """Adds a station to the favorites list.
    
    Args:
        station: Name of the station to add
    """
    try:
        # Check if station exists
        station_id = await get_station_id(station)
        if not station_id:
            return f"Station {station} not found."
            
        # Read current favorites list
        try:
            with open("favorite_stations.json", "r") as f:
                favorites = json.load(f)
        except FileNotFoundError:
            favorites = {"stations": []}
            
        # Check if station is already in favorites
        if station in favorites["stations"]:
            return f"Station {station} is already in favorites."
            
        # Add station to favorites
        favorites["stations"].append({"station_id": station_id, "station_name": station})
        
        # Save updated list
        with open("favorite_stations.json", "w") as f:
            json.dump(favorites, f, indent=4)
            
        return f"Station {station} added to favorites."
        
    except Exception as e:
        return f"Error adding station: {str(e)}"

@mcp.tool()
async def remove_favorite_station(station: str) -> str:
    """Removes a station from the favorites list.
    
    Args:
        station: Name of the station to remove
    """
    
    try:
        # Read current favorites list
        try:
            with open("favorite_stations.json", "r") as f:
                favorites = json.load(f)
        except FileNotFoundError:
            return "No favorite stations found."
            
        # Check if station is in favorites
        station_found = False
        for fav_station in favorites["stations"]:
            if isinstance(fav_station, dict) and fav_station.get("station_name") == station:
                favorites["stations"].remove(fav_station)
                station_found = True
                break
                
        if not station_found:
            return f"Station {station} is not in favorites."
            
        # Save updated list
        with open("favorite_stations.json", "w") as f:
            json.dump(favorites, f, indent=4)
            
        return f"Station {station} removed from favorites."
        
    except Exception as e:
        return f"Error removing station: {str(e)}"

@mcp.tool()
async def get_favorite_stations() -> str:
    """Returns the list of favorite stations."""
    try:
        # Read favorites list
        try:
            with open("favorite_stations.json", "r") as f:
                favorites = json.load(f)
        except FileNotFoundError:
            return "No favorite stations found."
            
        if not favorites["stations"]:
            return "No favorite stations found."
            
        # Format stations list
        stations_list = "\n".join([f"- {station['station_name']} - {station['station_id']}" for station in favorites["stations"]])
        return f"Favorite stations:\n{stations_list}"
        
    except Exception as e:
        return f"Error getting favorite stations: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

