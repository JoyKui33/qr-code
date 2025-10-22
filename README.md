# devops-qr-code

This is the sample application for the DevOps Capstone Project.
It generates QR Codes for the provided URL, the front-end is in NextJS and the API is written in Python using FastAPI.

## Application

**Front-End** - A web application where users can submit URLs.

**API**: API that receives URLs and generates QR codes. The API stores the QR codes in cloud storage(AWS S3 Bucket).

## Running locally

### API

The API code exists in the `api` directory. You can run the API server locally:

- Clone this repo
- Make sure you are in the `api` directory
- Create a virtualenv by typing in the following command: `python -m venv .venv`
- Install the required packages: `pip install -r requirements.txt`
- Create a `.env` file in the `api` directory with your AWS access key, secret key, bucket name, and optional region (`AWS_REGION`)
- Run the API server: `uvicorn main:app --reload`
- Your API Server should be running on port `http://localhost:8000`

#### Run the API with Docker (optional)

- Make sure you are in the `api` directory
- Build the image: `docker build -t qr-api .`
- Run the container (mount your environment variables file if needed): `docker run --env-file .env -p 8000:8000 qr-api`
- The API will be available at `http://localhost:8000`

### Front-end

The front-end code exits in the `front-end-nextjs` directory. You can run the front-end server locally:

- Clone this repo
- Make sure you are in the `front-end-nextjs` directory
- Install the dependencies: `npm install`
- Run the NextJS Server: `npm run dev`
- Your Front-end Server should be running on `http://localhost:3000`

#### Run the Front-end with Docker (optional)

- Make sure you are in the `front-end-nextjs` directory
- Build the image: `docker build -t qr-frontend .`
- Run the container: `docker run -p 3000:3000 qr-frontend`
- Open `http://localhost:3000`


## Goal

The goal is to get hands-on with DevOps practices like Containerization, CICD and monitoring.

Look at the capstone project for more detials.

## Author

[Rishab Kumar](https://github.com/rishabkumar7)

## License

[MIT](./LICENSE)
