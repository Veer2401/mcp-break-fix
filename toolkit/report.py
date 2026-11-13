import json
from collections import Counter
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from toolkit.models import Finding


def _cell(text: str) -> str:
    # Clean text for a Markdown table cell: a "|" or a line break would break the table.
    return text.replace("|", "\\|").replace("\n", " ")


def build_summary(findings: list[Finding]) -> dict:
    # Count results by verdict. The words must match exactly (uppercase).
    counts = Counter(f.verdict for f in findings)
    return {
        "total": len(findings),
        "vulnerable": counts["VULNERABLE"],
        "safe": counts["SAFE"],
        "inconclusive": counts["INCONCLUSIVE"],
    }


def write_reports(findings: list[Finding], out_dir: Path, server_path: Path) -> None:
    # Writes two files: report.json (for programs) and report.md (for people).
    out_dir.mkdir(exist_ok=True)  # make the folder if it doesn't exist yet
    generated_at = datetime.now().isoformat(timespec="seconds")
    summary = build_summary(findings)

    # JSON report: the agent reads this in Phase 4, and the verifier compares
    # two of these (before and after a fix) in Phase 5. Keep the shape stable.
    data = {
        "server": str(server_path),
        "generated_at": generated_at,
        "summary": summary,
        "findings": [asdict(f) for f in findings],  # asdict turns each Finding into a dict
    }
    (out_dir / "report.json").write_text(json.dumps(data, indent=2))

    # Markdown report: build a list of text lines, then join them into one file.
    lines = [
        "# Attack Report",
        "",
        f"- **Server:** `{server_path}`",
        f"- **Generated:** {generated_at}",
        "",
        f"**{summary['vulnerable']} of {summary['total']} checks found a vulnerability** "
        f"({summary['safe']} safe, {summary['inconclusive']} inconclusive)",
        "",
        "| Case | Category | Verdict | Time | Evidence |",
        "|---|---|---|---|---|",
    ]
    for f in findings:  # one table row per result
        lines.append(
            f"| {f.case_id} | {f.category} | {f.verdict} | {f.elapsed:.1f}s | {_cell(f.evidence)} |"
        )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n")