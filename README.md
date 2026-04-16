# SportZone

Dynamic sports ecommerce website built with Python, Flask, and MongoDB.

## Features

- Multiple sports sections with sport-specific equipment
- Shopping cart and checkout flow
- Customer and order details stored in MongoDB
- Admin panel for reviewing customers and orders
- Sporty responsive UI

## Run

1. Install packages:
   `pip install -r requirements.txt`
2. Copy `.env.example` to `.env`
3. Start MongoDB
4. Run:
   `python app.py`

Open `http://127.0.0.1:5000`

## Free Deploy

Recommended free stack:

- Render free web service
- MongoDB Atlas free cluster

Render settings:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

Required environment variables:

- `SECRET_KEY`
- `MONGO_URI`
- `MONGO_DB_NAME`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

This repo includes a `render.yaml` file to make Render setup easier.
