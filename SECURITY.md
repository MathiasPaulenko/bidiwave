# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.8.x   | :white_check_mark: |
| < 1.8   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in bidiwave, please report it
responsibly:

1. **Do not** open a public GitHub issue.
2. Email **mathias.paulenko@outlook.com** with a description of the
   vulnerability, reproduction steps, and potential impact.
3. You will receive an acknowledgment within 48 hours.
4. A fix will be developed and released as soon as possible, and you will be
   credited in the release notes (unless you prefer to remain anonymous).

## Security Considerations

bidiwave communicates with browsers via WebSocket. Keep in mind:

- **WebSocket URLs** may contain session tokens. Do not log or share connection
  URLs.
- **Remote code execution**: `script.evaluate()` and `script.call_function()`
  execute arbitrary JavaScript in the browser. Only run trusted code.
- **Network interception**: intercepted request/response bodies may contain
  sensitive data. Handle with care.
- **CDP bridge**: the CDP module provides direct access to browser internals.
  Treat it with the same caution as DevTools.
