# 🕌 ROM PeerBot - Rose of Madinah Islamic Companion Bot

[![CI/CD Pipeline](https://github.com/MuhammedIrshath49/EternalGivingProject/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/MuhammedIrshath49/EternalGivingProject/actions/workflows/ci-cd.yml)

A comprehensive Islamic companion Telegram bot providing accurate prayer times, adkar reminders, Friday khutbah notifications, and nearby mosque finder for Muslims worldwide.

## ✨ Features

### 🕌 Prayer Times
- **Accurate Singapore Prayer Times** from official MUIS CSV data
- Support for international cities via Aladhan API
- Dual time display (12-hour AM/PM + 24-hour format)
- Automatic daily updates

### ⏰ Smart Reminders
- Prayer reminders (10 minutes before + exact time)
- Morning Adkar (15 minutes after Fajr)
- Evening Adkar (30 minutes after Asr)
- Sleep Adkar (1 hour after Isha)
- Customizable Allahu Allah dhikr intervals

### 📖 Islamic Resources
- Friday Khutbah updates from MUIS
- Wirdu Amm daily routines
- Adkar and dhikr guidance
- Quranic references

### 📍 Mosque Finder
- Find nearby mosques and musollahs
- Singapore mosque database integration
- International mosque search via OpenStreetMap
- Interactive map locations

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/MuhammedIrshath49/EternalGivingProject.git
cd EternalGivingProject

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API_TOKEN and database settings

# Set up database
python -m database.migrate

# Run the bot
python main.py
```

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use Docker Compose)
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

## ⚙️ Configuration

Create a `.env` file (see `.env.example`):

```env
# Required
API_TOKEN=your_telegram_bot_token

# Database (Railway auto-provides, or configure manually)
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db

# Optional
LOG_LEVEL=INFO
DEFAULT_CITY=Singapore
DEFAULT_COUNTRY=Singapore
```

## 🐳 Docker & CI/CD

### Docker Image
Multi-platform Docker images are automatically built and published to GitHub Container Registry:
```bash
docker pull ghcr.io/muhammedirshath49/eternalgivingproject:latest
```

### GitHub Actions Pipeline
Automated CI/CD workflow includes:
- ✅ Code linting and syntax validation
- 🐳 Multi-platform Docker builds (amd64, arm64)
- 📦 Push to GitHub Container Registry
- 🔒 Security vulnerability scanning with Trivy
- 🚀 Deployment readiness checks

See [DOCKER.md](DOCKER.md) for detailed Docker documentation.

## � CI/CD

### GitHub Actions Pipeline
Automated CI/CD workflow includes:
- ✅ Code linting and syntax validation (Black, isort, Flake8)
- 🔒 Security vulnerability scanning (Safety)
- 🚀 Deployment readiness checks
- 📊 Automated testing on push and pull requests
│   ├── handlers/          # Command handlers
│   │   ├── start.py       # Start & help commands
│   │   ├── prayer.py      # Prayer times & location
│   │   ├── adkar.py       # Adkar settings
│   │   └── misc.py        # Miscellaneous handlers
│   ├── schedulers/        # Automated tasks
│   │   ├── prayer_scheduler.py
│   │   ├── adkar_scheduler.py
│   │   └── khutbah_scheduler.py
│   └── utils/             # Helper modules
│       ├── prayer_api.py  # Prayer times API
│       ├── muis_prayer_csv.py  # MUIS data parser
│       ├── mosque_finder.py    # Mosque search
│       └── khutbah_fetcher.py  # Khutbah scraper
├── database/              # Database models & migrations
├── assets/                # Static assets
├── Dockerfile             # Container definition
├── docker-compose.yml     # Local development setup
├── requirements.txt       # Python dependencies
├── main.py                # Application entry point
└── config.py              # Configuration management
```

## 🔧 Development

### Running Tests
```bash
# Lint code
black --check .
isort --check-only .
flake8 .

# Format code
black .
isort .
```

### Database Migrations
```bash
python -m database.migrate
```

## 🚀 Deployment

### Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Set environment variable `API_TOKEN`
3. Railway auto-detects `Dockerfile` and deploys

### Manual Deployment
```bash
# Pull latest image
docker pull ghcr.io/muhammedirshath49/eternalgivingproject:latest

# Run with your environment
docRailway automatically detects `Procfile` and `requirements.txt`
3. Add PostgreSQL database addon
4. Set environment variable `API_TOKEN` in Railway dashboard
5. Deploy! Railway handles everything automatically

### Environment Variables in Railway
```
API_TOKEN=your_telegram_bot_token
DATABASE_URL=automatically_provided_by_railway
- [x] Friday Khutbah notifications
- [x] Docker containerization
- [x] CI/CD pipeline
- [ ] Multi-language support
- [ ] Qibla direction finder
- [ ] Islamic calendar events
- [ ] Hadith of the day

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. PusCI/CD pipeline with automated testingst

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Prayer times data from [MUIS](https://www.muis.gov.sg/) (Singapore)
- International prayer times from [Aladhan API](https://aladhan.com/prayer-times-api)
- Mosque data from [OpenStreetMap](https://www.openstreetmap.org/)
- Built with [aiogram](https://github.com/aiogram/aiogram) framework

## 📞 Support

For support, please open an issue in the GitHub repository.

---

**May Allah accept our efforts and make this beneficial for the Ummah. 🤲**

*In sha Allah*
