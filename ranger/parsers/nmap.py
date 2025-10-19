"""Parser for nmap XML output."""
from __future__ import annotations

from xml.etree import ElementTree as ET


def parse_nmap(path: str) -> list[dict[str, str]]:
    tree = ET.parse(path)
    root = tree.getroot()
    rows: list[dict[str, str]] = []
    for host in root.findall("host"):
        address = host.find("address")
        addr = address.get("addr") if address is not None else ""
        if addr is None:
            addr = ""
        for port in host.findall("ports/port"):
            port_id = port.get("portid") or ""
            protocol = port.get("protocol") or ""
            rows.append(
                {
                    "host": addr,
                    "port": port_id,
                    "proto": protocol,
                    "service": "",
                    "product": "",
                    "version": "",
                }
            )
    return rows
