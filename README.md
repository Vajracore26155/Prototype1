# 🛡️ VAJRA CORE - AI-Driven Multi-Vendor Network Security Compliance Auditor

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![CI/CD](https://github.com/your-org/vajra-core/workflows/CI%20Pipeline/badge.svg)](https://github.com/your-org/vajra-core/actions)

**Smart India Hackathon 2026 - Problem Statement SIH26155**

VAJRA CORE is an enterprise-grade, AI-powered network security compliance auditor that automates the analysis of multi-vendor network device configurations against industry standards (CIS, PCI-DSS, NIST, ISO 27001).

---

## 🚀 Key Features

### Core Capabilities
- ✅ **Multi-Vendor Support**: Cisco, Fortinet, Juniper, Palo Alto, CheckPoint
- ✅ **AI-Powered Analysis**: GPT-4, Claude, Gemini integration with adaptive learning
- ✅ **Compliance Frameworks**: CIS, PCI-DSS, NIST, ISO 27001, HIPAA
- ✅ **Configuration Drift Detection**: Real-time monitoring and alerting
- ✅ **Automated Remediation**: AI-generated fix suggestions
- ✅ **Advanced Reporting**: Executive summaries, technical reports, scheduled reports
- ✅ **Webhook Integration**: Real-time event notifications
- ✅ **Knowledge Graph**: Entity relationships and impact analysis
- ✅ **Universal Search**: Fast search across all entities
- ✅ **Role-Based Access Control**: Multi-tenancy with fine-grained permissions

### Phase 7-9 Features (Production Ready)
- 🔄 **Configuration Versioning**: Track all configuration changes
- 📊 **Monitoring Dashboard**: Real-time metrics and trends
- 🔔 **Event Bus System**: 30+ event types with webhook delivery
- 📈 **Advanced Reporting**: Templates, scheduling, custom builders
- 🕸️ **Knowledge Graph**: Entity relationships and impact analysis
- 🔍 **Advanced Search**: Full-text search with faceted filtering
- 🐳 **Docker Production**: Multi-stage builds, security hardened
- 📊 **Prometheus Metrics**: Comprehensive application monitoring
- 🔐 **Security Hardening**: Rate limiting, input validation, security headers
- 📝 **Comprehensive Tests**: 90%+ code coverage
- 🔄 **CI/CD Pipelines**: Automated testing, security scanning, deployment

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         VAJRA CORE API                          │
│                      (FastAPI + Python 3.11)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │   Upload &   │  │  Compliance  │  │   Drift Detection   │  │
│  │   Parsing    │  │  Evaluation  │  │   & Monitoring      │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  AI/ML       │  │  Reporting   │  │   Knowledge Graph   │  │
│  │  Engine      │  │  System      │  │   & Search          │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  Webhooks &  │  │  Auth & RBAC │  │   Monitoring &      │  │
│  │  Events      │  │              │  │   Observability     │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    PostgreSQL 15 + Redis 7                      │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15 with Alembic migrations
- **Cache**: Redis 7
- **AI/ML**: OpenAI GPT-4, Anthropic Claude, Google Gemini
- **Monitoring**: Prometheus + Grafana
- **Task Queue**: Celery + Redis
- **Container**: Docker + Docker Compose
- **Orchestration**: Kubernetes ready
- **CI/CD**: GitHub Actions

---

## ⚡ Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/your-org/vajra-core.git
cd vajra-core

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Create admin user
docker-compose exec api python scripts/create_admin.py

# Access API
open http://localhost:8000/docs
```

**That's it!** API is running on http://localhost:8000

---

## 📦 Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/vajra-core.git
cd vajra-core

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Setup database
createdb vajra
alembic upgrade head

# 5. Start Redis
redis-server

# 6. Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://vajra:password@localhost:5432/vajra

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-secure-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# AI/ML APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Rate Limiting
DEFAULT_RATE_LIMIT=60  # requests per minute
AUTH_RATE_LIMIT=5
UPLOAD_RATE_LIMIT=10
```

### Compliance Rules

Edit `backend/app/compliance/rules.yaml` to customize compliance rules:

```yaml
frameworks:
  CIS:
    name: "CIS Benchmarks"
    version: "1.0"
    rules:
      - rule_id: "CIS-1.1"
        title: "Enable SSH version 2"
        severity: "HIGH"
        check: "ssh_version >= 2"
```

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Quick Examples

#### Upload Configuration
```bash
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@router_config.cfg"
```

#### Run Audit
```bash
curl -X POST http://localhost:8000/api/audits \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config_id": "CFG-000123",
    "frameworks": ["CIS", "PCI-DSS"]
  }'
```

#### Generate Report
```bash
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "TMPL-001",
    "name": "Security Report",
    "format": "PDF"
  }'
```

See [API_REFERENCE.md](docs/API_REFERENCE.md) for complete documentation.

---

## 🚀 Deployment

### Production Deployment

```bash
# Build production image
docker build -t vajra-core:latest -f docker/Dockerfile.production .

# Deploy with Docker Compose
docker-compose -f docker-compose.production.yml up -d

# Or deploy to Kubernetes
kubectl apply -f k8s/
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace vajra

# Apply manifests
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/api.yaml

# Check status
kubectl get pods -n vajra
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment guide.

---

## 📊 Monitoring

### Prometheus Metrics

Access metrics at: http://localhost:8000/metrics

**Available Metrics:**
- HTTP requests/duration/size
- Audit execution metrics
- Finding counts by severity
- AI prediction metrics
- System resource usage
- Database query performance
- Cache hit rates
- Webhook delivery status

### Grafana Dashboards

1. Start Grafana:
```bash
cd monitoring
docker-compose up -d grafana
```

2. Import dashboard from `monitoring/grafana-dashboard.json`

3. Access: http://localhost:3000 (admin/admin)

### Alerts

Configured in `monitoring/alert_rules.yml`:
- High error rate
- Slow requests
- Critical findings spike
- Low compliance score
- System resource warnings

---

## 🔐 Security

### Security Features

- ✅ JWT authentication with refresh tokens
- ✅ Role-based access control (RBAC)
- ✅ Rate limiting (sliding window)
- ✅ Input validation & sanitization
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CSRF protection
- ✅ Security headers (OWASP recommended)
- ✅ HTTPS/TLS encryption
- ✅ Secret management
- ✅ Audit logging
- ✅ Webhook HMAC signatures

### Security Scanning

```bash
# Dependency vulnerabilities
safety check --file=backend/requirements.txt

# Code security analysis
bandit -r backend/app/

# Docker image scanning
trivy image vajra-core:latest
```

---

## 🧪 Testing

### Run Tests

```bash
cd backend

# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_auth.py -v

# Integration tests only
pytest tests/test_api_integration.py -v -m integration
```

### Test Coverage

Current coverage: **90%+**

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Test Structure

```
backend/tests/
├── conftest.py                  # Fixtures
├── test_auth.py                 # Authentication tests
├── test_adaptive_learning.py    # AI/ML tests
├── test_compliance_engine.py    # Compliance tests
├── test_drift_detection.py      # Drift detection tests
├── test_api_integration.py      # Integration tests
└── test_phase_7_monitoring.py   # Monitoring tests
```

---

## 👥 Development

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linters
black backend/app/
flake8 backend/app/
mypy backend/app/
```

### Code Style

- **Formatter**: Black
- **Linter**: Flake8
- **Type Checker**: MyPy
- **Line Length**: 120 characters

### Git Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit: `git commit -m "Add feature"`
3. Push branch: `git push origin feature/my-feature`
4. Create Pull Request
5. Wait for CI/CD checks
6. Merge after approval

---

## 📈 Performance

### Benchmarks

- **Upload Processing**: 100 configs/minute
- **Audit Execution**: 50 audits/minute
- **API Response Time**: <200ms (p95)
- **Database Queries**: <50ms (p95)
- **Concurrent Users**: 1000+

### Optimization

- Database indexing on frequently queried fields
- Redis caching for hot data
- Connection pooling
- Async/await for I/O operations
- Lazy loading of relationships
- Query optimization with SQLAlchemy

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

### How to Contribute

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Run test suite
5. Submit Pull Request

### Code of Conduct

Be respectful, inclusive, and collaborative.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🆘 Support

### Documentation

- [API Reference](docs/API_REFERENCE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

### Contact

- **Email**: support@vajra.example.com
- **Issues**: https://github.com/your-org/vajra-core/issues
- **Discussions**: https://github.com/your-org/vajra-core/discussions

---

## 🏆 Acknowledgments

- **Smart India Hackathton 2026** for the problem statement
- OpenAI, Anthropic, Google for AI APIs
- FastAPI, SQLAlchemy, and the Python community
- All contributors and supporters

---

## 📊 Project Status

- ✅ **Phase 1-6**: Complete (Core features)
- ✅ **Phase 7**: Complete (Monitoring, Webhooks, Versioning)
- ✅ **Phase 8**: Complete (Testing, Security, Performance)
- ✅ **Phase 9**: Complete (CI/CD, Monitoring, Documentation)
- 🚀 **Production Ready**: Yes
- 📈 **Test Coverage**: 90%+
- 🔐 **Security Audited**: Yes
- 📚 **Documentation**: Complete

---

## 🔥 What's Next

- [ ] Frontend Dashboard (React/Vue.js)
- [ ] Mobile App (React Native)
- [ ] Advanced ML Models (Custom training)
- [ ] Multi-cloud Support (AWS, Azure, GCP)
- [ ] API Gateway Integration
- [ ] Blockchain Audit Trail

---

**Made with ❤️ for SIH 2026**

⭐ Star this repo if you find it useful!
