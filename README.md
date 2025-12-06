<p align="center">
  <img src="https://raw.githubusercontent.com/Yonas-Berhe/pac-man-charm/main/frontend/public/pacman-logo.png" alt="Pac-Man Logo" width="200"/>
</p>

<h1 align="center">🎮 Pac-Man Charm</h1>

<p align="center">
  <strong>A modern, full-stack Pac-Man game with leaderboards, user authentication, and cloud deployment</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=white" alt="React"/>
  <img src="https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/FastAPI-0.123-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
</p>

<p align="center">
  <a href="#-play-now">Play Now</a> •
  <a href="#-features">Features</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-deployment">Deployment</a> •
  <a href="#-api-documentation">API Docs</a>
</p>

---

## 🕹️ Play Now

**Live Demo:** [https://pacman-app.onrender.com](https://pacman-app.onrender.com)

| Demo Account | |
|---|---|
| Email | `demo@example.com` |
| Password | `demo1234` |

---

## ✨ Features

### 🎮 Game Features
- **Classic Pac-Man gameplay** with smooth animations
- **Arrow key controls** for intuitive movement
- **Multiple levels** with increasing difficulty
- **Power pellets** to eat ghosts
- **Lives system** with 3 lives per game

### 👤 User Features
- **User registration & login** with JWT authentication
- **Personal game history** tracking all your games
- **High score tracking** with new record celebrations
- **User statistics** (games played, win rate, total dots eaten)

### 🏆 Leaderboard
- **Global rankings** - compete with all players
- **Time-based filters** - All-time, Monthly, Weekly, Daily
- **Personal rank** - see where you stand
- **Percentile ranking** - know your standing

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI Framework |
| **TypeScript** | Type Safety |
| **Vite** | Build Tool |
| **shadcn/ui** | UI Components |
| **Tailwind CSS** | Styling |

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | API Framework |
| **SQLAlchemy** | ORM |
| **PostgreSQL** | Production Database |
| **SQLite** | Development Database |
| **JWT** | Authentication |
| **uv** | Dependency Management |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Nginx** | Reverse Proxy |
| **Render** | Cloud Hosting |

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** 20+
- **Python** 3.12+
- **Docker** (optional, for containerized setup)

### Local Development

#### Option 1: Run Separately

```bash
# Clone the repository
git clone https://github.com/Yonas-Berhe/pac-man-charm.git
cd pac-man-charm

# Start backend (Terminal 1)
cd backend
uv sync
uv run uvicorn main:app --reload --port 3000

# Start frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:3000/docs

#### Option 2: Run with npm (concurrent)

```bash
# From project root
npm install
npm run dev    # Runs both frontend and backend
```

#### Option 3: Run with Docker

```bash
# Development (separate containers)
docker compose up --build

# Production (combined container)
docker compose -f deploy/docker-compose.yml up --build
```

**Access:** http://localhost

---

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Unit tests
make test

# Integration tests
make test-integration

# All tests
make test-all
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 📦 Deployment

### Render (Recommended)

The app is configured for one-click deployment to **Render**.

1. **Fork this repository** to your GitHub account

2. **Create Render Account** at [render.com](https://render.com)

3. **Deploy via Blueprint:**
   - Go to [Render Dashboard](https://dashboard.render.com/blueprints)
   - Click **"New Blueprint Instance"**
   - Connect your GitHub repo
   - Render auto-detects `render.yaml`
   - Click **"Apply"**

4. **Wait for deployment** (~5-10 minutes)

**What gets created:**
- ✅ PostgreSQL database (free tier)
- ✅ Web service with Docker image
- ✅ Auto-configured `DATABASE_URL`
- ✅ Auto-generated `JWT_SECRET_KEY`

### Manual Docker Deployment

```bash
# Build the image
docker build -t pacman-app .

# Run with PostgreSQL
docker run -p 80:80 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e JWT_SECRET_KEY=your-secret-key \
  pacman-app
```

---

## 📡 API Documentation

### Interactive Docs
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Create account |
| `POST` | `/api/v1/auth/login` | Login |
| `GET` | `/api/v1/users/me` | Get profile |
| `POST` | `/api/v1/games` | Start game |
| `POST` | `/api/v1/games/{id}/end` | Submit score |
| `GET` | `/api/v1/leaderboard` | Get rankings |

### Example: Start a Game

```bash
curl -X POST "https://your-app.onrender.com/api/v1/games" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

## 📁 Project Structure

```
pac-man-charm/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/       # UI components
│   │   │   ├── game/         # Game logic & rendering
│   │   │   ├── auth/         # Auth modal & user menu
│   │   │   └── ui/           # shadcn components
│   │   ├── contexts/         # React contexts
│   │   └── lib/              # API client
│   └── Dockerfile
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── db/               # SQLAlchemy models & repos
│   │   └── routes/           # API endpoints
│   ├── tests/                # Unit tests
│   ├── tests_integration/    # Integration tests
│   └── Dockerfile
│
├── deploy/                   # Production configs
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── supervisord.conf
│
├── Dockerfile                # Combined production build
├── docker-compose.yml        # Development setup
└── render.yaml               # Render Blueprint
```

---

## 🎯 Game Controls

| Key | Action |
|-----|--------|
| ⬆️ `↑` | Move Up |
| ⬇️ `↓` | Move Down |
| ⬅️ `←` | Move Left |
| ➡️ `→` | Move Right |
| `Space` | Pause/Resume |

---

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | SQLite (dev) |
| `JWT_SECRET_KEY` | Secret for JWT tokens | `dev-secret` |
| `VITE_API_URL` | Backend API URL (frontend) | `/api/v1` |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ and 🎮
</p>

<p align="center">
  <img src="https://media.giphy.com/media/l46CkATpdyLwLI7vi/giphy.gif" width="100" alt="Pac-Man animation"/>
</p>
