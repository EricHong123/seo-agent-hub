FROM python:3.12-slim
WORKDIR /app
COPY server.py index.html ./
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1
CMD ["python3", "server.py"]
