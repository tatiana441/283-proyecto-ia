# Guía de despliegue — GitHub + Railway

Pasos exactos para publicar MediWatch. Los pasos 1-2 los hace una persona del equipo (necesitan cuentas propias); todo lo demás ya está preparado en el repo.

## 1. Subir el repo a GitHub (~5 min)

```bash
# desde la carpeta mediwatch/
git remote add origin https://github.com/TU_USUARIO/IdEquipo-proyecto-abierto-ia.git
git push -u origin main
```

Luego en GitHub → Settings → Secrets and variables → Actions → **New repository secret**:

| Secret | Valor |
|--------|-------|
| `DATABASE_URL` | la misma del `.env.local` (pooler de Supabase) |

Con eso quedan activos los dos workflows: **CI** (tests en cada push) y **Actualización semanal de datos** (lunes 3 a.m., también ejecutable a mano desde la pestaña Actions → Run workflow).

## 2. Railway (~15 min)

Crear cuenta en railway.app (login con GitHub) → **New Project → Deploy from GitHub repo** → seleccionar el repo. Crear **dos servicios** desde el mismo repo:

### Servicio 1: API

- Settings → **Root Directory**: `/` · **Dockerfile Path**: `deployments/docker/Dockerfile.api`
- Variables:
  - `DATABASE_URL` = (pooler de Supabase)
  - `OPENROUTER_API_KEY` = (la del .env.local)
  - `CORS_ORIGINS` = `https://<dominio-del-frontend>.up.railway.app` (se agrega después de crear el servicio 2)
- Settings → Networking → **Generate Domain** → anotar la URL (p. ej. `mediwatch-api.up.railway.app`)

### Servicio 2: Frontend

- Settings → **Root Directory**: `/frontend` (usa el `Dockerfile` de esa carpeta)
- Variables (Railway las pasa como build args):
  - `VITE_API_URL` = `https://<dominio-de-la-api>.up.railway.app`
  - `VITE_SUPABASE_URL` = `https://yryxtnguteodrnzybisa.supabase.co`
  - `VITE_SUPABASE_ANON_KEY` = (la publishable del .env.local)
- Generate Domain → esta es la **URL pública de la demo** para el README.

### Ajuste final

1. Volver al servicio API y poner en `CORS_ORIGINS` el dominio real del frontend (sin barra final). Redeploy.
2. En Supabase → Authentication → URL Configuration → **Site URL** = dominio del frontend (para los correos de confirmación).

## 3. Verificación post-deploy

- `https://<api>/health` → `{"status": "ok"}`
- `https://<api>/docs` → Swagger (este es el enlace "Documentación de la API" del README)
- Abrir el frontend → registrarse → buscar "TACROLIMUS" → ver score + precios → preguntar al asistente y verificar que cita fuentes.

## 4. Actualizar el README

Reemplazar los placeholders de "Solución en Producción (Demo en Vivo)" con las dos URLs y hacer push.

## Notas

- El parquet SISMED (230 MB) no viaja al repo ni a Railway: la app lee el agregado desde Supabase y el cron semanal conserva esa tabla intacta.
- Costo: plan gratuito de Railway (US$5 de crédito/mes) alcanza para la demo del concurso.
