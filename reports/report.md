# Attack Report

- **Server:** `targets/weak_server/server.py`
- **Generated:** 2026-11-13T12:15:58

**3 of 4 checks found a vulnerability** (1 safe, 0 inconclusive)

| Case | Category | Verdict | Time | Evidence |
|---|---|---|---|---|
| traversal-1 | path_traversal | VULNERABLE | 0.1s | secret returned in output: FAKE_SECRET=this-should-never-be-readable |
| calc-injection-control | code_injection | SAFE | 0.1s | rejected: ToolError: Error calling tool 'calculate': unsupported expression |
| calc-exhaustion-1 | resource_exhaustion | VULNERABLE | 1.7s | took 1.7s (normal calls take ~0s) |
| fetch-hang-1 | hang | VULNERABLE | 7.6s | no answer after 7.6s: tool has no timeout |
