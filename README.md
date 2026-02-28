# ☁️ Cloud User Management System – Backend API

A scalable and secure cloud-based user management system developed using Flask.
This project implements JWT authentication, role-based access control (RBAC), and CRUD operations for managing users, following best practices in backend API design and security.

# 📌 Project Overview

The Cloud User Management System provides a RESTful backend service that allows users to register, authenticate, and be managed based on roles (Admin/User).
It is designed for deployment in a cloud environment with secure configuration using environment variables.

## Features
- Secure user registration and login
- JWT-based authentication and authorization
- Role-Based Access Control (RBAC)
- CRUD operations on users (Admin only)
- Password hashing for data security
- RESTful API architecture
- Cloud-ready deployment configuration
- Environment variable management using .env

## API Endpoints
- GET /healthz
- POST /predict

## Technology Stack
Backend: Python, Flask
Authentication: Flask-JWT-Extended (JWT Tokens)
Database: SQLite (development), PostgreSQL (cloud-ready)
ORM: SQLAlchemy
Security: Werkzeug Password Hashing
Testing: Postman
Version Control: Git & GitHub
