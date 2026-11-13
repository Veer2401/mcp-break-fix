# Attack Report

- **Server:** `targets/weak_server/server.py`
- **Generated:** 2026-11-13T14:17:46

**6 of 11 checks found a vulnerability** (5 safe, 0 inconclusive)

| Case | Category | Verdict | Time | Evidence |
|---|---|---|---|---|
| traversal-1 | path_traversal | VULNERABLE | 0.1s | secret returned in output: FAKE_SECRET=this-should-never-be-readable |
| traversal-deep | path_traversal | VULNERABLE | 0.1s | secret returned in output: FAKE_SECRET=this-should-never-be-readable |
| traversal-absolute | path_traversal | VULNERABLE | 0.1s | secret returned in output: FAKE_SECRET=this-should-never-be-readable |
| traversal-control | path_traversal | SAFE | 0.1s | worked normally: MCP Break Fix Project |
| calc-control | calculator | SAFE | 0.1s | worked normally: 4 |
| calc-injection-control | code_injection | SAFE | 0.1s | rejected: ToolError: Error calling tool 'calculate': unsupported expression |
| calc-reject-text | code_injection | SAFE | 0.1s | rejected: ToolError: Error calling tool 'calculate': unsupported expression |
| calc-exhaustion-1 | resource_exhaustion | VULNERABLE | 1.7s | took 1.7s (normal calls take ~0s) |
| fetch-hang-1 | hang | VULNERABLE | 7.6s | no answer after 7.6s: tool has no timeout |
| fetch-local-1 | ssrf_local_access | VULNERABLE | 0.1s | fetched a local address and returned: FAST_LOCAL_OK |
| fetch-scheme-control | ssrf_local_access | SAFE | 0.1s | rejected: ToolError: Error calling tool 'fetch_url': Request URL is missing an 'http://' o |
