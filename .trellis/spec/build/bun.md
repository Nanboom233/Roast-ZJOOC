# Bun

These rules apply to Bun projects.
Use Bun, `bunx`, and the project's package-manager scripts.

Do not use these dependencies or APIs:

- `express`
- `better-sqlite3`
- `ioredis`
- `pg`
- `postgres.js`
- `ws`
- `dotenv`
- `execa`
- `node:fs` file read and write APIs

Serve all Bun Web HTML imports through `Bun.serve`.
Do not use Vite for these applications.
