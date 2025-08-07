FROM golang:1.21-alpine AS go-builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY *.go ./
RUN go build -o main .

FROM python:3.11-alpine