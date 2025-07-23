# Frontend Dockerfile for Baobab AI
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user for security
RUN addgroup -g 1001 -S baobab && \
    adduser -S baobab -u 1001

# Set ownership
RUN chown -R baobab:baobab /usr/share/nginx/html
RUN chown -R baobab:baobab /var/cache/nginx
RUN chown -R baobab:baobab /var/log/nginx
RUN chown -R baobab:baobab /etc/nginx/conf.d
RUN touch /var/run/nginx.pid
RUN chown -R baobab:baobab /var/run/nginx.pid

# Switch to non-root user
USER baobab

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Expose port
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]