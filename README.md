# TaskMaster Pro: Enterprise Task Management System

![Project Status](https://img.shields.io/badge/Status-Beta-orange)
![License](https://img.shields.io/badge/License-MIT-blue)
![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Angular%20%7C%20PostgreSQL-green)

A high-performance, enterprise-grade task management system with organizational hierarchy, advanced RBAC, and real-time analytics. Built for scale and designed for high-fidelity user experiences.

## 🚀 Key Features

- **🏢 Organizational Hierarchy**: Manage multi-level structures (Organization -> Branch -> Department -> Team).
- **🛡️ Advanced RBAC**: Permission-based access control with hierarchical roles.
- **📊 Performance Hub**: Real-time dashboard with analog clock, organizational map, and productivity stats.
- **🎨 Dynamic Branding**: Auto-theme injection and white-labeling support.
- **📋 Agile Integration**: Kanban and Scrum support with dynamic columns and WIP limits.
- **🔍 Global Search Engine**: Tactics-wide task discovery via organizational search.
- **📜 Strategy Audit**: Automated security logging and action tracking.

## 🛠️ Tech Stack
...

## 📦 Quick Start

### Prerequisites
- Docker & Docker Desktop

### Development
1. **Clone & Setup**:
   ```bash
   git clone -b Dev https://github.com/Rediet2000/TaskManagement-.git
   cd TaskManagement-
   cp .env.example .env
   ```
2. **Launch**:
   ```bash
   docker-compose up -d --build
   ```

### Production Deployment
For stable environments:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## 🔗 Port Mapping
- **Frontend (Prod)**: `http://localhost:80`
- **Frontend (Dev)**: `http://localhost:4200`
- **API (Prod)**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
Contributions are welcome! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.