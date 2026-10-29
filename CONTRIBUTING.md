# Contributing to RepoLens

Thank you for considering contributing to **RepoLens**! We welcome bug reports, feature proposals, documentation improvements, and pull requests.

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+ and npm 10+
- Git
- (Optional) Docker & Docker Compose

### 1. Clone the Repository
```bash
git clone https://github.com/yashwantraj147-eng/repolens.git
cd repolens
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements-dev.txt
cp .env.example .env
```

Start the development backend:
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger docs will be available at `http://localhost:8000/api/docs`.

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Testing & Quality Assurance

### Running Backend Tests
Ensure the scoring engine maintains >= 80% test coverage:
```bash
cd backend
pytest tests/ --cov=app.services.scoring_engine --cov-report=term-missing
```

### Running Frontend Tests
```bash
cd frontend
npm run test
```

### Production Build
```bash
cd frontend
npm run build
```

---

## Pull Request Workflow

1. Fork the repo and create your branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Write clean, readable code with type hints and docstrings.
3. Add unit tests covering new features or bug fixes.
4. Ensure all backend and frontend tests pass.
5. Commit using **Conventional Commits**:
   - `feat: add export to PDF option`
   - `fix: resolve division by zero in commit activity`
   - `docs: update API documentation`
   - `chore: update dependencies`
6. Push to your fork and submit a Pull Request.

