# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in mcp-injector, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Send a description of the issue to:

**foldwork@proton.me**

Include:
- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof of concept
- The mcp-injector version affected (`mcp-injector --version`)
- Your operating system and architecture

We will acknowledge receipt within 48 hours and aim to provide a fix or mitigation within 14 days for critical issues.

## Scope

The following are in scope:

- The `mcp-injector` binary (daemon and MCP server)
- The `install.sh` installer script
- The `foldwork.dev` website and API endpoints

The following are out of scope:

- Vulnerabilities in third-party dependencies (please report these upstream)
- Issues in the `mcp-benchmark` tool (report in that repository)

## What we consider a vulnerability

- Any mechanism that causes mcp-injector to transmit source code or secrets to a remote server other than the configured AI provider
- Bypass of the secret redaction subsystem
- License key forgery or bypass
- Remote code execution via the MCP protocol
- Path traversal allowing access to files outside `MCP_WORKSPACE`

## Disclosure policy

We follow responsible disclosure. We ask that you give us a reasonable window to investigate and patch before publishing details publicly. In return, we will credit researchers who report valid vulnerabilities (if they wish to be credited).

## Known limitations

The secret redaction subsystem uses pattern matching and Shannon entropy analysis. It is designed as a defense-in-depth measure, not a guarantee. Do not rely solely on mcp-injector to prevent credential exposure; follow secure coding practices and use a secrets manager.
