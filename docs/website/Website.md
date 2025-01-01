# Hosting locally
Website allows you to easily try out all models. To get it running locally:
## Prerequisites
* If you're going to run backend service locally without Docker, you'll have to install requirements for the main project by running `pip3 install requirements.txt` in root directory.
*
TODO npm version, create requirements.txt also for backend
## Backend
1. Navigate to `/website/backend`
2. Install dependencies with `pip3 install requirements.txt`
3. Execute `uvicorn main:app --reload`
## Frontend
1. Navigate to `/website/frontend`
2. Build by running `npm run build`
3. Execute `npm run dev`

## Docker
If instead, you want to use docker, just run `docker-compose up` in the `website` directory.
