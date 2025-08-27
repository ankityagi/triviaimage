# TriviaImage

A single-player movie poster trivia game web application.

## Features
- Google OAuth authentication (frontend only)
- Movie poster questions with hidden titles
- 4 radio button options for movie name
- Score tracking, next/quit buttons
- Final score page with wrong guesses and total time
- User stats via `/stats` backend endpoint
- SQLite database for persistence

## Tech Stack
- Frontend: HTML, CSS, vanilla JavaScript
- Backend: PHP
- Database: SQLite

## Setup
1. Copy `.env.example` to `.env` and fill in your secrets/URLs.
2. Ensure PHP and SQLite are installed.
3. Start a local PHP server in the backend directory:
	```
	php -S localhost:8000
	```
4. Open `frontend/index.html` in your browser.
	```
	http://localhost:8000/frontend/index.html
	```

5. Docker commands
	```
	docker build -f backend/Dockerfile -t triviaimage:latest .

	docker run -d -p 8080:80 --name triviaImageC triviaimage:latest
	```
6. Test backend 
	```
	http://localhost:8080/api.php?endpoint=health
	```
7. Run the frontend locally and connect to backend in container
	```
	python3 -m http.server 3000

	http://localhost:3000/frontend/index.html
	```

## Deployment on Render.com

### Backend (PHP + SQLite)
1. **Create a new Web Service on Render.com**
	- Go to your Render dashboard and click 'New Web Service'.
	- Connect your GitHub repo or upload your code.
	- Set the root directory to `/backend`.
	- Set the build and start command to:
	  ```
	  php -S 0.0.0.0:10000
	  ```
	- Set the environment to 'PHP'.
	- Add a persistent disk if you want to keep the SQLite database between deploys.
	- Make sure your SQLite database file is in the correct location and accessible by the PHP code.
	- Add any required environment variables in the Render dashboard.

2. **Database Setup**
	- If your app needs to initialize the database, add a script or instructions in your repo for first-time setup.
	- For persistent data, use Render's 'Add Disk' feature and point your SQLite file to the disk mount path.

3. **Accessing the Backend**
	- After deploy, note the public URL Render provides (e.g., `https://your-app.onrender.com`).
	- Your API endpoints (e.g., `/stats`) will be available at this URL.

### Frontend (Static Site)
1. **Create a new Static Site on Render.com**
	- Go to your Render dashboard and click 'New Static Site'.
	- Connect your GitHub repo or upload your code.
	- Set the root directory to `/frontend`.
	- No build command is needed if you use pre-built CSS (e.g., Tailwind output.css).
	- Render will automatically serve `index.html` and static assets.

2. **Configure API URLs**
	- Update your frontend code to use the backend's public URL for API requests (e.g., `fetch('https://your-app.onrender.com/stats')`).

3. **Accessing the Frontend**
	- After deploy, note the public URL Render provides for your static site.
	- Share this link with users to play the game.

### Notes
- If you use environment variables, set them in the Render dashboard for both services.
- For Tailwind CSS, build your CSS locally and commit `output.css` to the repo before deploying.
- For persistent scores, use Render's disk feature for SQLite.
- Make sure CORS is handled if your frontend and backend are on different URLs.

## API
- `/stats`: Returns user stats (name, total rounds played, total score, best score for any round).

## Database
- `users` table: id, name
- `scores` table: id, datetime, user_id, rounds, score, total_time

## Notes
- Replace placeholder images and movie names with real data.
- Add Google OAuth client ID and redirect URI in `.env` for authentication.