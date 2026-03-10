# Frontend Workspace

This directory is reserved for the Scivly web app.

- framework: Next.js App Router
- primary concerns: landing pages, public library, user workspace, and admin console
- expected subdirectories: `app/`, `components/`, `lib/`
- local commands: `npm install`, `npm run dev`, `npm run build`, `npm run preview`
- current routes: `/`, `/docs`, `/docs/api`, `/admin`
- Vercel: set the project Root Directory to `frontend`
- Vercel config: `frontend/vercel.json`

`npm run start` serves the existing static export from `dist/`.
`npm run preview` rebuilds the static export and serves it locally.

Do not move backend business logic here. The frontend should consume backend APIs instead of becoming a second application core.
