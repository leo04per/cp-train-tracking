from typing import Any
import httpx
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
async def train_query(station: str) -> str:
    
    """Query the trains that pass through a station in Portugal.

    Args:
        station: Station name (ex: Porto-Campanhã, Lisboa Oriente)
    """
    
    try:
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
            with open("favorite_stations.txt", "r") as f:
                favorites = f.read().splitlines()
        except FileNotFoundError:
            favorites = []
            
        # Check if station is already in favorites
        if station in favorites:
            return f"Station {station} is already in favorites."
            
        # Add station to favorites
        favorites.append(station)
        
        # Save updated list
        with open("favorite_stations.txt", "w") as f:
            f.write("\n".join(favorites))
            
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
            with open("favorite_stations.txt", "r") as f:
                favorites = f.read().splitlines()
        except FileNotFoundError:
            return "No favorite stations found."
            
        # Check if station is in favorites
        if station not in favorites:
            return f"Station {station} is not in favorites."
            
        # Remove station from favorites
        favorites.remove(station)
        
        # Save updated list
        with open("favorite_stations.txt", "w") as f:
            f.write("\n".join(favorites))
            
        return f"Station {station} removed from favorites."
        
    except Exception as e:
        return f"Error removing station: {str(e)}"

@mcp.tool()
async def get_favorite_stations() -> str:
    """Returns the list of favorite stations."""
    try:
        # Read favorites list
        try:
            with open("favorite_stations.txt", "r") as f:
                favorites = f.read().splitlines()
        except FileNotFoundError:
            return "No favorite stations found."
            
        if not favorites:
            return "No favorite stations found."
            
        # Format stations list
        stations_list = "\n".join([f"- {station}" for station in favorites])
        return f"Favorite stations:\n{stations_list}"
        
    except Exception as e:
        return f"Error getting favorite stations: {str(e)}"


if __name__ == "__main__":
    '''import asyncio
    
    async def test_consulta():
        resultado = await train_query("Porto-Campanhã")
        print("\nTest result:")
        print(resultado)
    
    # Executa o teste
    asyncio.run(test_consulta())'''
    mcp.run(transport="stdio")

