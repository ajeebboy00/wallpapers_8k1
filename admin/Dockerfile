# Stage 1: Build production React/TypeScript bundle
FROM node:20-alpine AS builder

WORKDIR /app

# Cache package manifests
COPY package*.json ./
RUN npm ci

# Build optimized static assets
COPY . .
RUN npm run build

# Stage 2: Serve via Nginx Alpine
FROM nginx:alpine

# Remove default nginx server configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom production server configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD wget -q -O - http://localhost/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
