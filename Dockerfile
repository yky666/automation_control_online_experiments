FROM node:24-bookworm-slim AS dependencies
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci

FROM python:3.12-slim-bookworm AS course
WORKDIR /build
COPY requirements-cloud.txt ./
RUN apt-get update && apt-get install -y --no-install-recommends fonts-noto-cjk && rm -rf /var/lib/apt/lists/* && pip install --no-cache-dir -r requirements-cloud.txt
COPY backend ./backend
COPY sources ./sources
COPY tools ./tools
COPY --from=dependencies /build/node_modules/katex/dist ./node_modules/katex/dist
RUN python tools/export_online.py

FROM dependencies AS frontend
COPY index.html vite.config.js ./
COPY frontend ./frontend
COPY --from=course /build/public ./public
RUN npm run build
RUN mkdir -p /report-math && cp -r node_modules/katex/dist/* /report-math/

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/matplotlib CONTROL_LAB_ENABLE_LOCAL_MATLAB=0 CONTROL_LAB_SESSION_ISOLATION=1
WORKDIR /app
COPY requirements-cloud.txt ./
RUN apt-get update && apt-get install -y --no-install-recommends fonts-noto-cjk && rm -rf /var/lib/apt/lists/* && pip install --no-cache-dir -r requirements-cloud.txt && useradd --uid 1000 --create-home lab
COPY backend ./backend
COPY sources ./sources
COPY --from=frontend /build/dist ./dist
COPY --from=frontend /report-math ./node_modules/katex/dist
RUN mkdir runtime && chown -R lab:lab /app
USER lab
EXPOSE 8765
CMD ["python","-m","uvicorn","backend.main:app","--host","0.0.0.0","--port","8765"]
