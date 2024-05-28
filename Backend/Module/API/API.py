# Module/API/API.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
from pathlib import Path
from Module.ResourceManager import *

app = FastAPI()

# Pfade zu den Logdateien
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BLOCK_LOG_FILE = BASE_DIR / 'Logs/block_log.json'
ACTIVE_MEASURES_FILE = BASE_DIR / 'Logs/active_measures.json'
NETWORK_TRAFFIC_LOG_FILE = BASE_DIR / 'Logs/network_traffic_logs.json'
RESOURCE_USAGE_LOG_FILE = BASE_DIR / 'Logs/resource_usage.json'
ACTIVE_CONNECTIONS_FILE = BASE_DIR / 'Logs/active_connections.json'

def read_json_file(file_path: Path):
    print(f"Reading data from {file_path}")  # Debugging-Ausgabe
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                print(f"Data read from {file_path}: {data}")  # Debugging-Ausgabe
                return data
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError encountered while reading {file_path}: {e}")  # Debugging-Ausgabe
            # Versuchen Sie, die beschädigte Datei zu reparieren
            with open(file_path, 'w') as f:
                json.dump([], f)
            return []
    print(f"File {file_path} does not exist")  # Debugging-Ausgabe
    return []

@app.get("/logs/blocks")
async def get_block_logs():
    data = read_json_file(BLOCK_LOG_FILE)
    return JSONResponse(content=data)

@app.get("/logs/active")
async def get_active_measures():
    data = read_json_file(ACTIVE_MEASURES_FILE)
    return JSONResponse(content=data)

@app.get("/logs/traffic")
async def get_network_traffic_logs():
    data = read_json_file(NETWORK_TRAFFIC_LOG_FILE)
    return JSONResponse(content=data)

@app.get("/logs/resource_usage")
async def get_resource_usage_logs():
    data = read_json_file(RESOURCE_USAGE_LOG_FILE)
    return JSONResponse(content=data)

@app.get("/logs/connections")
async def get_active_connections():
    data = read_json_file(ACTIVE_CONNECTIONS_FILE)
    return JSONResponse(content=data)

@app.get("/resource/usage")
async def get_current_resource_usage():
    data = {
        "cpu_usage": ResourceManager.get_cpu_usage(),
        "ram_usage": ResourceManager.get_ram_usage(),
        "network_traffic": ResourceManager.get_network_traffic()
    }
    return JSONResponse(content=data)

@app.get("/resource/network")
async def get_current_network_usage():
    data = ResourceManager.get_network_traffic()
    return JSONResponse(content=data)
