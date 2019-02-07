FROM node:lts-alpine

RUN apk add --no-cache git
RUN npm install -g http-server

WORKDIR /crud

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

EXPOSE 8080
CMD [ "http-server", "." ]
