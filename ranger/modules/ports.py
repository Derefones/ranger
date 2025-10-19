"""Port scanning module."""
from __future__ import annotations

from xml.etree import ElementTree as ET

from ..util import io
from . import ModuleContext, ModuleOutcome


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="ports")
    alive_path = context.fs.combined_dir() / "alive.txt"
    if not alive_path.exists():
        outcome.errors.append("no alive hosts")
        return outcome
    ports_dir = context.fs.subdir("ports")
    raw_lines = alive_path.read_text(encoding="utf-8").splitlines()
    entries = [line.strip() for line in raw_lines if line.strip()]
    summary_path = ports_dir / "nmap_summary.csv"
    headers = ["host", "port", "proto", "service", "product", "version"]
    with io.csv_writer(summary_path, headers) as writer:
        for entry in entries:
            host, _, port = entry.partition(":")
            writer.writerow({
                "host": host,
                "port": port or "80",
                "proto": "tcp",
                "service": "",
                "product": "",
                "version": "",
            })
    root = ET.Element("nmaprun")
    for entry in entries:
        host, _, port = entry.partition(":")
        host_el = ET.SubElement(root, "host")
        address = ET.SubElement(host_el, "address")
        address.set("addr", host)
        ports_el = ET.SubElement(host_el, "ports")
        port_el = ET.SubElement(ports_el, "port")
        port_el.set("portid", port or "80")
        port_el.set("protocol", "tcp")
    xml_path = ports_dir / f"nmap_top{context.config.nmap_top_ports}.xml"
    xml_data = ET.tostring(root, encoding="utf-8")
    io.write_text(xml_path, xml_data.decode("utf-8"))
    outcome.artifacts["nmap_xml"] = str(xml_path)
    outcome.artifacts["nmap_summary"] = str(summary_path)
    outcome.counts["entries"] = len(entries)
    return outcome
