# ranger

`ranger` is a scoped reconnaissance and vulnerability-detection orchestrator tailored for Kali Linux and Bugcrowd-style web bounty programs. It focuses on deterministic collection, scope-aware filtering, and structured reporting while remaining lightweight and dependency-free beyond the system tools it coordinates.

## Features

- Argparse-based CLI with dry-run and self-test helpers
- Scope modelling for include/exclude domains, URLs, regexes, and CIDRs
- Structured filesystem layout with atomic writes and quarantining of out-of-scope artifacts
- Optional integration with common reconnaissance tooling when available at runtime
- Streaming-friendly utilities and resilient parsers for common tool outputs

## Getting Started

### Requirements

- Python 3.11+
- Kali Linux or a compatible Unix-like environment
- Optional third-party tools detected automatically at runtime: `subfinder`, `amass`, `assetfinder`, `dnsx`, `massdns`, `httpx`, `ffuf`, `waybackurls`, `gau`, `katana`, `nmap`, `nuclei`, `gf`, `subzy`, `subjack`, `trufflehog`

### Installation

Clone the repository and install the Python package in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Usage

Run the orchestrator against a target:

```bash
python -m ranger.main \
  --target example.com \
  --program-name "example" \
  --out results/ \
  --modules all
```

Use `--dry-run` to print the execution plan without running external tooling. The `--self-test` flag runs quick sanity checks for filesystem and scope helpers.

### Development Workflow

The project enforces formatting and quality gates via Ruff, mypy, and pytest:

```bash
ruff check .
mypy --strict .
pytest -q
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
