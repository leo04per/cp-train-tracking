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
            print(f"Fazendo requisição para: {url}")
            print(f"Headers utilizados: {HEADERS}")
            
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            
            print(f"Status code: {response.status_code}")
            print(f"Resposta bruta: {response.text[:500]}...")  # Primeiros 500 caracteres
            
            # Verifica se a resposta é JSON válido
            try:
                data = response.json()
                print(f"Tipo de dados recebido: {type(data)}")
                print(f"Dados recebidos: {data}")
            except ValueError as e:
                print(f"Erro ao decodificar JSON: {str(e)}")
                raise ValueError(f"Resposta inválida da API para a estação {station_name}")

            # Verifica se data é uma lista ou dicionário
            if not isinstance(data, (list, dict)):
                print(f"Formato inesperado: {type(data)}")
                raise ValueError(f"Formato de resposta inválido para a estação {station_name}")

            # Se for um dicionário, procura a chave 'response'
            if isinstance(data, dict):
                stations = data.get("response", [])
                print(f"Estacoes encontradas no dicionário: {stations}")
            else:
                stations = data
                print(f"Estacoes encontradas na lista: {stations}")

            if not stations:
                raise ValueError(f"Nenhuma estação encontrada com o nome {station_name}")

            # Procura a estação
            for station in stations:
                print(f"Verificando estação: {station}")
                if isinstance(station, dict) and station_name.lower() in station.get("Nome", "").lower():
                    node_id = str(station.get("NodeID"))
                    print(f"Estação encontrada! NodeID: {node_id}")
                    return node_id

            raise ValueError(f"Estação {station_name} não encontrada.")

        except httpx.HTTPError as e:
            print(f"Erro HTTP: {str(e)}")
            raise ValueError(f"Erro ao acessar a API: {str(e)}")
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            raise ValueError(f"Erro inesperado: {str(e)}")


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
            raise ValueError(f"Erro ao obter horários: {str(e)}")


@mcp.tool()
async def consultar_comboios(estacao: str) -> str:
    """Consulta os comboios que passam por uma estação em Portugal.

    Args:
        estacao: Nome da estação (ex: Porto-Campanhã, Lisboa Oriente)
    """
    try:
        station_id = await get_station_id(estacao)
        data = await get_train_schedule(station_id)

        if not data:
            return f"Nenhuma informação disponível para {estacao}."

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
        return f"Erro ao obter dados: {str(e)}"



if __name__ == "__main__":
    mcp.run(transport="stdio")

