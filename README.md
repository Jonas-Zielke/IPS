# IPS

A very small demo of an Intrusion Prevention System (IPS) built with Python and [scapy](https://scapy.net/).

## Structure

- `Backend/main.py` – captures network traffic and applies registered rules.
- `Backend/Module/Block.py` – helper functions for blocking IP addresses and logging measures.
- `Backend/Module/Rules.py` – example packet processing rules.
- `Backend/Config.py` – basic configuration such as forwarding ports and excluded IP ranges.

## Running

Install dependencies (only `scapy` is required) and start the main script:

```bash
pip install scapy
python Backend/main.py
```

All captured traffic will be stored in `Logs/network_traffic_logs.json`.
