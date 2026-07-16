FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Vite bakes import.meta.env.VITE_* in at BUILD time, not read at runtime -
# this ARG must be set (Railway forwards service variables as build args
# automatically when an ARG of the same name is declared) before the
# build runs. ARGs don't carry across stages, so if a later stage ever
# needs this too it must be redeclared there.
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM caddy:2-alpine
COPY --from=build /app/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
