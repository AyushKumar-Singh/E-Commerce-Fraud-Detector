# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is currently not compatible with SWC. See [this issue](https://github.com/vitejs/vite-plugin-react/issues/428) for tracking the progress.

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

# E-Commerce Fraud Detector

A full‑stack project (React + TypeScript frontend, Node backend) for detecting potential fraud in e‑commerce transactions.

This README provides concise setup, run and test instructions for both frontend and backend on Windows.

---

## Prerequisites

- Node.js 18+ (or the version your project expects)
- npm (comes with Node) — or yarn / pnpm if used by the repo
- Git
- (Optional) Docker & Docker Compose if the repo includes Docker configs
- (Optional) Database client (Postgres / MySQL) if a database is required

Verify Node/npm:
- PowerShell / CMD:
  - node -v
  - npm -v

---

## Repository layout (typical)
Adjust paths below if your repo differs.

- /frontend — React + Vite app
- /backend — Node (Express / Nest / Fastify) API
- .env.example — example environment file
- .gitignore — secrets and generated files ignored

---

## Initial setup (one-time)

1. Clone:
   - git clone <repo-url>
   - cd "E-Commerce Fraud Detector"

2. Copy env examples:
   - PowerShell:
     - cp .env.example .env
   - CMD:
     - copy .env.example .env
   - Fill required values in `.env`.


3. Install root dependencies (if monorepo scripts exist) or install per side below.

---

## Frontend

From repo root:

- Enter frontend:
  - cd frontend

- Install:
  - npm install
  - Or: yarn / pnpm install

- Run dev server (Vite):
  - npm run dev
  - The terminal will show the local URL (usually http://localhost:5173)

- Build for production:
  - npm run build
  - Preview production build:
    - npm run preview

- Tests & lint (if configured):
  - npm test
  - npm run lint
  - npm run format

Notes:
- If using a specific Node version, consider using nvm or .nvmrc.

---

## Backend

From repo root:

- Enter backend:
  - cd backend

- Install:
  - npm install

- Environment:
  - Ensure `.env` contains API_PORT, DATABASE_URL, and other keys required by backend.

- Run in development:
  - npm run dev
    - (typically uses nodemon / ts-node-dev to reload on changes)

- Run production:
  - npm run build
  - npm start

- Database migrations (if using Prisma / TypeORM / Sequelize):
  - Prisma example:
    - npx prisma generate
    - npx prisma migrate dev --name init
  - TypeORM / Sequelize: run the project-specific migration command.

- Tests & lint:
  - npm test
  - npm run lint

---

## Running frontend + backend together

Option A — manually:
- Open two terminals:
  - Terminal 1 (frontend):
    - cd frontend
    - npm run dev
  - Terminal 2 (backend):
    - cd backend
    - npm run dev

Option B — docker / docker-compose:
- If docker-compose.yml exists:
  - docker compose up --build
  - (Stop with docker compose down)

---

## Environment files

Add private keys & secrets only to `.env` (do not commit). Your .gitignore already ignores `.env*` while allowing `.env.example`. Example `.env.example`:

NODE_ENV=development
PORT=4000
API_URL=http://localhost:4000
FRONTEND_PORT=5173
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
JWT_SECRET=replace_me
# Add any other required variables here

Copy `.env.example` -> `.env` and fill values.

---

## Security / Secrets

- Do not commit `.env` or any secret files.
- .gitignore is configured to hide common secret files (keys, creds, service accounts).
- If sensitive data was accidentally committed, rotate the secret and remove it from git history (use git filter-repo or BFG).

---

## Common troubleshooting

- "Port already in use": change port in `.env` or kill the process.
- Missing scripts: check package.json in frontend/backend for available scripts.
- DB connection errors: ensure database is running and DATABASE_URL is correct.
- If packages fail to install: remove node_modules and lock files, then reinstall:
  - rm -rf node_modules
  - npm install

(Windows CMD / PowerShell: use rd /s /q node_modules)

---

## Tests, linting & formatting

- Run tests:
  - cd frontend || cd backend
  - npm test

- Lint:
  - npm run lint

- Auto-format:
  - npm run format

Adjust commands to match scripts in each package.json.

---

## Contributing

1. Create a feature branch
2. Run lint & tests locally
3. Open a pull request with a clear description

---

## If you want, I can:
- Inspect specific package.json scripts and update this README with exact commands.
- Add a sample .env.example based on backend/frontend config.
- Add docker-compose example if you use containers.
