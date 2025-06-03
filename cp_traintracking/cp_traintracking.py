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

    """Consulta o NodeID da estação via Infraestruturas de Portugal."""
    
    url = f"https://www.infraestruturasdeportugal.pt/negocios-e-servicos/estacao-nome/{station_name}"

    async with httpx.AsyncClient() as client:
        try:            
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            
            # Verify if the response is a valid JSON
            try:
                data = response.json()
            except ValueError as e:
                print(f"Error decoding JSON: {str(e)}")
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
                print(f"Checking station: {station}")
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

    """Consulta os comboios que passam por uma estação CP."""
    
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
async def consultar_comboios(estacao: str) -> str:
    
    """Consulta os comboios que passam por uma estação em Portugal.

    Args:
        estacao: Nome da estação (ex: Porto-Campanhã, Lisboa Oriente)
    """
    
    try:
        station_id = await get_station_id(estacao)
        station_id = str(station_id)
        station_id = f"{station_id[:2]}-{station_id[2:].lstrip('0')}"
        data = await get_train_schedule(station_id)

        if not data:
            return f"No information available for {estacao}."

        comboios = []
        for train in data:
            origem = train.get("trainOrigin", {}).get("designation", "Origem desconhecida")
            destino = train.get("trainDestination", {}).get("designation", "Destino desconhecido")
            partida = train.get("departureTime", "??:??")
            chegada = train.get("arrivalTime", "??:??")
            numero = train.get("trainNumber", "N/A")
            tipo = train.get("trainService", {}).get("designation", "Tipo desconhecido")
            plataforma = train.get("platform", "—")

            info = (
                f"Comboio {numero} ({tipo})\n"
                f"De: {origem} → Para: {destino}\n"
                f"Partida: {partida} — Chegada: {chegada} | Plataforma: {plataforma}"
            )
            comboios.append(info)

        return f"Comboios em {estacao}:\n\n" + "\n\n---\n\n".join(comboios)

    except Exception as e:
        return f"Error getting data: {str(e)}"



if __name__ == "__main__":
    mcp.run(transport="stdio")

