# Spike notes — bidiwave

## Objetivo

Documentar los findings del spike de validación BiDi con Chrome y Edge.

## Resumen

BiDi funciona correctamente para Chrome y Edge usando ChromeDriver/EdgeDriver
como proxy. No es posible conectar BiDi directamente al navegador; se necesita
el driver como intermediario.

## Chrome

- **Versión del navegador**: 149.0.7827.201
- **ChromeDriver**: 149.0.7827.155 (win64)
- **Driver path**: `bin/chromedriver-win64/chromedriver.exe`
- **Driver port**: 9515
- **Flujo**:
  1. Lanzar `chromedriver --port=9515`
  2. POST `http://localhost:9515/session` con `{"capabilities":{"alwaysMatch":{"webSocketUrl":true}}}`
  3. Response incluye `value.capabilities.webSocketUrl` → `ws://localhost:9515/session/{sessionId}`
  4. Conectar a esa URL via WebSocket
  5. Enviar `session.status` → respuesta `{"type":"success","result":{"ready":false,"message":"already connected"}}`
- **¿Funciona?**: Sí

## Edge

- **Versión del navegador**: 149.0.4022.98
- **EdgeDriver**: 149.0.4022.98 (win64)
- **Driver path**: `bin/edgedriver/msedgedriver.exe`
- **Driver port**: 9516
- **Flujo**: idéntico a Chrome, usando `msedgedriver --port=9516`
- **¿Funciona?**: Sí

## Diferencias encontradas

- Chrome y Edge usan el mismo flujo (ambos son Chromium).
- El `build.version` difiere: Chrome reporta `149.0.7827.155`, Edge reporta `149.0.4022.98`.
- `session.status` responde `ready: false` y `message: "already connected"` en ambos casos,
  lo que confirma que la sesión BiDi ya está activa al conectar via `webSocketUrl`.

## Notas adicionales

- El `--remote-debugging-port` del navegador expone CDP, no BiDi. No sirve para BiDi directo.
- La URL de descarga de ChromeDriver viene de
  `https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json`
  (milestone 149 → versión 149.0.7827.155).
- La URL de descarga de EdgeDriver es `https://msedgedriver.microsoft.com/{version}/edgedriver_win64.zip`
  (el viejo `msedgedriver.azureedge.net` está deprecado).
- Firefox expone BiDi nativamente en `ws://127.0.0.1:{port}/session` sin necesidad de driver,
  pero no se probó en este spike por no estar instalado.
