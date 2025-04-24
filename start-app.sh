#!/usr/bin/env bash
prisma generate --schema=prisma/schema.prisma
python src/main.py
