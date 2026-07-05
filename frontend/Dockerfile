# Frontend de MediWatch (React + Vite, servido como estático).
# Las variables VITE_* son de TIEMPO DE BUILD: en Railway se declaran como
# variables del servicio y llegan aquí como build args.

FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ENV VITE_API_URL=$VITE_API_URL \
    VITE_SUPABASE_URL=$VITE_SUPABASE_URL \
    VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY

RUN npm run build

FROM node:20-alpine
RUN npm install -g serve
COPY --from=build /app/dist /app
EXPOSE 3000
# -s: modo SPA (todas las rutas caen en index.html)
CMD serve -s /app -l ${PORT:-3000}
