# Revile Frontend

Next.js App Router frontend for the Revile news publication and editorial desk.

## Local development

From this directory:

```powershell
Copy-Item .env.example .env.local
npm run dev
```

The frontend runs at `http://localhost:3000` and proxies browser API requests through `/api/v1` to the FastAPI backend at `NEXT_PUBLIC_API_URL`.

## Production

```powershell
npm run build
npm run start
```

## Railway

Deploy this directory as its own service inside the same Railway project as the backend. Set `NEXT_PUBLIC_API_URL` to the backend's public domain and, when available, set `INTERNAL_API_URL` to the backend's private Railway address for server components and the frontend proxy. Also set `NEXT_PUBLIC_IMAGEKIT_PUBLIC_KEY` and `NEXT_PUBLIC_IMAGEKIT_URL_ENDPOINT`; do not set the private ImageKit key on this service. Update the backend `FRONTEND_ORIGIN` variable to the frontend service's exact Railway domain.
