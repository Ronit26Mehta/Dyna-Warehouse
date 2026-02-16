# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ Yes     |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public issue
2. Email the maintainers directly with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
3. We will acknowledge receipt within **48 hours**
4. A fix will be prioritized and released as a patch version

## Security Considerations

- **Pickle Caching** — Cache files are stored locally at `~/.warehouse/` and are only loaded by the application owner. Do not share or accept pickle files from untrusted sources.
- **Data Storage** — Settings and simulation history are stored as plain JSON. No sensitive data (passwords, API keys) is stored.
- **No Network Access** — The application is fully offline. It does not make any network requests.
