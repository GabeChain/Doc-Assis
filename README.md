# Doc Assistant

## Project structure

- Application - Flask app (main api)

<!-- - Extensions - Chrome extension -->

- Frontend - Frontend uses Vite and Vue3
  - chat - Chat sdk plugin

## QuickStart

Note: Make sure you have docker installed

1. Dowload and open this repository
2. Create an .env file in your root directory and set the env variable OPENAI_API_KEY with your openai api key and  VITE_API_STREAMING to true or false, depending on if you want streaming or not
3. Run `bash ./run-with-docker-compose.sh` or run

   ```bash
   docker-compose -f docker-compose.yaml up -d
   ```

To stop just run Ctrl + C

## Development environments

### Spin up mongo and redis and qdrant

For development only 3 containers are used from docker-compose.yaml (by deleting all services except for redis, mongo, qdrant).
See file [docker-compose-dev.yaml](./docker-compose-dev.yaml).

Run

```bash
docker-compose -f docker-compose-dev.yaml up -d
```

### Run the backend

Make sure you have Python 3.10 or 3.11 installed.

1. If you use annaconda, create a new environment and activate it

   ```bash
   conda create --name DocsAssis python=3.10
   conda activate DocsAssis
   ```

2. Prepare .env file
3. Change to `api/` subdir and install dependencies for the backend

   ```commandline
   cd api/
   pip install -r requirements.txt
   ```

4. Run the app `python app.py`
5. Start worker with `celery -A app.celery worker -l INFO`
windows: (`celery -A app.celery worker --pool=eventlet -l info`)

### Start frontend

Make sure you have Node version 16 or higher.

1. Navigate to `/frontend` folder
2. run `npm run dev`

Built with [🦜️🔗 LangChain](https://github.com/hwchase17/langchain)
