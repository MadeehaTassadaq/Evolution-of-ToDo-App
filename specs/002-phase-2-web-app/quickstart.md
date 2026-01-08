# Quickstart: Phase II - Todo Full-Stack Web Application

This guide provides instructions on how to set up and run the application locally.

## Prerequisites

- Node.js (v18+) and npm
- Python (v3.11+) and `uv`

## Environment Variables

Create a `.env.local` file in both the `frontend` and `backend` directories with the following content:

```
# frontend/.env.local and backend/.env.local
BETTER_AUTH_SECRET="your-super-secret-key"
DATABASE_URL="postgresql://user:password@host:port/database"
```

- `BETTER_AUTH_SECRET`: A shared secret for signing and verifying JWTs.
- `DATABASE_URL`: The connection string for your Neon Serverless PostgreSQL database.

## Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install dependencies using `uv`:
    ```bash
    uv pip install -r requirements.txt
    ```
3.  Run the database migrations (details to be added in the `tasks` phase).
4.  Start the FastAPI server:
    ```bash
    uvicorn main:app --reload
    ```
    The backend will be running at `http://localhost:8000`.

## Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies using `npm`:
    ```bash
    npm install
    ```
3.  Start the Next.js development server:
    ```bash
    npm run dev
    ```
    The frontend will be running at `http://localhost:3000`.

## Running the Application

Once both the backend and frontend servers are running, you can access the application by navigating to `http://localhost:3000` in your web browser.
