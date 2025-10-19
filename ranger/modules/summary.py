"""Summary aggregation."""
from __future__ import annotations

from ..util import io
from . import ModuleContext, ModuleOutcome


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="summary")
    summary_dir = context.fs.subdir("summary")
    highlights_path = summary_dir / "highlights.md"
    counts_path = summary_dir / "counts.txt"
    indicators_path = summary_dir / "indicators.csv"
    io.write_text(highlights_path, "# Highlights\n\n- Placeholder summary\n")
    io.write_lines(counts_path, ["module,metric,value", "summary,placeholder,0"])
    with io.csv_writer(indicators_path, ["indicator", "value"]) as writer:
        writer.writerow({"indicator": "alive_hosts", "value": "0"})
    outcome.artifacts["highlights"] = str(highlights_path)
    return outcome
