# stage 1: build
FROM node:20-bullseye-slim AS bilder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# stage 2: dev
FROM node:20-bullseye-slim AS dev
WORKDIR /app
COPY ./frontend/package*.json ./

RUN npm ci 
COPY ./frontend ./ 
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]