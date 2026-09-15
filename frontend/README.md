# Revile Frontend

Next.js App Router frontend for the Revile news publication and editorial desk.

## Local development

From this directory:

```powershell
Copy-Item .env.example .env.local
npm run dev
```

The frontend runs at `http://localhost:3000` and calls the FastAPI backend at `NEXT_PUBLIC_API_URL`.

## Production

```powershell
npm run build
npm run start
```

## Railway

Deploy this directory as its own service inside the same Railway project as the backend. Set `NEXT_PUBLIC_API_URL` to the backend's public domain for browser requests. Set `INTERNAL_API_URL` to the backend's private Railway address when server components should use private networking. Update the backend `FRONTEND_ORIGIN` variable to the frontend service's exact Railway domain.
