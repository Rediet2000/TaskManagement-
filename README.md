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
- **📱 Responsive Design**: Glassmorphism UI optimized for desktop and mobile.
- **🔑 Secure Auth**: Integrated SMTP for password recovery and LDAP support (Experimental).

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL.
- **Frontend**: Angular 18, SCSS, Bootstrap Icons.
- **Infrastructure**: Docker, Docker Compose, Nginx.

## 📦 Quick Start

### Prerequisites
- Docker & Docker Desktop

### Deployment
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/task-management.git
   cd task-management
   ```

2. **Setup environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Launch with Docker**:
   ```bash
   docker-compose up -d --build
   ```

4. **Access the app**:
   - Frontend: `http://localhost:4200`
   - API Docs: `http://localhost:8000/docs`

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
Contributions are welcome! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.