# React Vite Starter with FastAPI Backend

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-16.x-green.svg)

## 📖 Description

Welcome to the **React Vite Starter with FastAPI Backend** project! This repository serves as a boilerplate for building full-stack applications using ``FastAPI`` for the backend and ``React`` with ``Vite`` and ``Tailwind CSS`` for the frontend. It provides a seamless development environment with efficient tooling, enabling you to focus on building robust features without worrying about initial setup complexities.

## Table of Contents

- [✨ Features](#-features)
- [🛠️ Tech Stack](#-tech-stack)
- [📋 Prerequisites](#-prerequisites)
- [🚀 Installation](#-installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [🏃 Running the Application](#-running-the-application)
  - [Running the Backend](#backend)
  - [Running the Frontend](#frontend)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## ✨ Features

- **FastAPI Backend:**
  - High-performance API endpoints
  - Automatic interactive API documentation
  - Easy integration with databases and third-party services

- **React Frontend:**
  - Modern UI with ``Tailwind CSS``
  - Fast development with ``Vite``
  - State management and component-based architecture

- **Development Tools:**
  - Virtual environment management with ``venv``
  - Auto-reloading for both frontend and backend
  - Environment variable configuration

## 🛠️ Tech Stack

- **Frontend**
  - [React](https://reactjs.org/)
  - [Vite](https://vitejs.dev/)
  - [Tailwind CSS](https://tailwindcss.com/)
- **Backend**
  - [FastAPI](https://fastapi.tiangolo.com/)
  - [Uvicorn](https://www.uvicorn.org/)
- **Others**
  - [Python 3.9](https://www.python.org/)
  - [Node.js 16.x](https://nodejs.org/)
  - [Virtualenv](https://virtualenv.pypa.io/en/latest/)

## 📋 Prerequisites

Before you begin, ensure you have met the following requirements:

- ``Python`` 3.9 or higher installed on your machine
- ``Node.js`` and ``npm`` installed for frontend development
- [Git](https://git-scm.com/) for version control

## 🚀 Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/IW714/react-vite-starter.git
   cd react-vite-starter/backend
   ```

### Backend Setup
1. **Navigate to the Backend Directory:**
    ```bash
    cd backend
    ```
2. **Create a Virtual Environment:**
    ```bash
    python3 -m venv .venv
    ```
3. **Activate the Virtual Environment:**
    - On macOS/Linux: 
    ```bash
    source .venv/bin/activate
    ```
    - On Windows: 
    ```bash
    .venv/Scripts/activate
    ```
4. **Install Dependencies:**
    ```bash
    pip install --upgrade pip
    pip install fastapi uvicorn
    pip freeze > requirements.txt
    ```
### Frontend Setup
1. **Navigate to the Frontend Directory:**
    ```bash
    cd frontend
    ```
4. **Install Dependencies:**
    ```bash
    npm install
    ```
3. **Configure Tailwind CSS:**

    If Tailwind CSS is not already set up, follow these steps:

    ```bash
    npm install -D tailwindcss postcss autoprefixer
    npx tailwindcss init -p
    ```

    Update `tailwind.config.js`:
    ```bash
    // tailwind.config.js

    module.exports = {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {},
    },
    plugins: [],
    }
    ```
    Include Tailwind in your CSS:
    ```bash
    /* src/index.css */

    @tailwind base;
    @tailwind components;
    @tailwind utilities;
    ```

## 🏃 Running the Application

### Backend
1. **Activate the Virtual Environment:**

    Ensure your're in the `backend/` directory and the virtual environment is activated.

    ```bash
    cd backend
    source .venv/bin/activate  # macOS/Linux
    # or
    .venv\Scripts\activate     # Windows
    ```

2. **Run the FastAPI Server:**
    ```bash
    uvicorn app.main:app --reload
    ```

    **Access the Backend:**

    - Root Endpoint: http://127.0.0.1:8000/
    - API Documentation: http://127.0.0.1:8000/docs

### Frontend
1. **Navigate to the Frontend Directory:**
    ```bash
    cd frontend
    ```

2. **Start the React Development Server:**
    ```bash
    npm run dev
    ```
    **Access the Frontend:**
    - React App: http://localhost:5173/ (this may be different depening on what ports are available)


## 🤝 Contributing
Contributions are welcome! Please follow these steps: 

1. **Fork the Repository**
2. **Create a New Branch**
    ```bash
    git checkout -b feature/YourFeatureName
    ```
3. **Make Your Changes**
4. **Commit Your Changes**
    ```bash
    git commit -m "Add some feature"
    ```
5. **Push to the Branch**
    ```bash
    git push origin feature/YourFeatureName
    ```
6. **Open a Pull Request**

## 📄 License
This project is licensed under the [MIT License](../LICENSE)