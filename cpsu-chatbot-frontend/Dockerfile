FROM node:22-slim AS build
WORKDIR /app

ARG VITE_API_DOMAIN
ENV VITE_API_DOMAIN=$VITE_API_DOMAIN

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:stable-alpine

RUN rm -rf /usr/share/nginx/html/*

COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]
