# 部署
docker compose -f docker-compose-dev.yaml build
docker compose -f docker-compose-dev.yaml up -d

# 启动dev
activate DocsGPT
flask --app application/app.py run --host=0.0.0.0 --port=7091
celery -A application.app.celery worker --pool=eventlet -l info