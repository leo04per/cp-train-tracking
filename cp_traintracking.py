from typing import Any
import httpx
import json
from rapidfuzz import process
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

with open("list_ids.json", "r") as f:
    STATION_LIST = json.load(f)

def get_station_id(station_name: str):
    
    best_match = process.extractOne(
        station_name, STATION_LIST.keys(), score_cutoff=70 
    if best_match:
        matched_name, score, _ = best_match
        return STATION_LIST[matched_name], matched_name
    return None, None

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
async def Query(station: str) -> str:
    
    """Query the trains that pass through a station in Portugal.

    Args:
        station: Station name (ex: Porto-Campanhã, Lisboa Oriente)
    """
    station_id = None

    try:
        if not station_id:
            station_id, corrected_name = get_station_id(station)
            if not station_id:
                return f"Station '{station}' not found."
            station = corrected_name 
        
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
                f"Train {number} ({type})\n"
                f"From: {origin} → To: {destination}\n"
                f"Departure: {departure} — arrival: {arrival} | platform: {platform} | delay: {delay}"
            )
            trains.append(info)

        return f"Trains in {station}:\n\n" + "\n\n---\n\n".join(trains) + "\n\n"

    except Exception as e:
        return f"Error getting data: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

