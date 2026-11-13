import asyncio
from pathlib import Path

from toolkit.attacks import ATTACKS
from toolkit.report import build_summary, write_reports
from toolkit.runner import run_case

# Which server to attack. Change this one line to test a different server.
SERVER = Path("targets/weak_server/server.py")
REPORTS_DIR = Path("reports")


async def main():
    findings = []  # collects each result as attacks finish

    # Run every attack in the list, one at a time.
    for case in ATTACKS:
        print(f"running {case.id} ...", flush=True)
        finding = await run_case(SERVER, case)  # runner.py does the actual work
        findings.append(finding)
        print(f"  {finding.verdict}: {finding.evidence} ({finding.elapsed:.1f}s)")

    # Short table at the end, so you don't have to scroll through server banners.
    print("\n=== SUMMARY ===")
    for f in findings:
        print(f"{f.case_id:<26} {f.verdict:<13} {f.elapsed:>5.1f}s")
    s = build_summary(findings)
    print(f"\n{s['vulnerable']} vulnerable, {s['safe']} safe, {s['inconclusive']} inconclusive")

    # Hand all results to report.py to write the two report files.
    write_reports(findings, REPORTS_DIR, SERVER)
    print(f"reports written to {REPORTS_DIR}/")


# Starts everything. Without this last line, nothing runs.
asyncio.run(main())