# ECOnomics

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-16.x-green.svg)

## 📖 Description

**ECOnomics** is a web application that simplifies the process of evaluating renewable energy options by providing comprehensive assessments that consider both economic and environmental factors. It integrates a FastAPI backend with a React frontend using Vite and Tailwind CSS, offering users an interactive platform to assess the potential of solar and wind energy based on their location.

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

- **AI-Powered Energy Assessments:**
  - Provides detailed reports on the potential of solar and wind energy in a specific area.
  - Utilizes OpenAI's GPT models for intelligent interactions and assessments.
  - Generates analyses on both economic viability and environmental impact.

- **Custom Calculations:**
  - Developed unique algorithms to calculate solar and wind potential.
  - Integrates data from multiple APIs for accurate assessments.

- **User-Friendly Interface:**
  - Modern UI with Tailwind CSS and ShadCN/UI components.
  - Responsive design suitable for various devices.

- **Backend Integration:**
  - High-performance API endpoints with FastAPI.
  - Integration with multiple external APIs for data gathering:
    - ElectricityMap API
    - NREL API
    - CDSAPI
    - OpenCage Geocoding API

## 🛠️ Tech Stack

- **Frontend**
  - [React](https://reactjs.org/)
  - [Vite](https://vitejs.dev/)
  - [Tailwind CSS](https://tailwindcss.com/)
  - [ShadCN/UI](https://ui.shadcn.com/)
  - [Custom ShadCN Chat](https://github.com/jakobhoeg/shadcn-chat)
  - [Framer Motion](https://www.framer.com/motion/)
- **Backend**
  - [FastAPI](https://fastapi.tiangolo.com/)
  - [Uvicorn](https://www.uvicorn.org/)
  - [LangChain](https://langchain.com/)
  - [OpenAI GPT](https://openai.com/)
- **APIs**
  - [ElectricityMap API](https://www.electricitymap.org/)
  - [NREL API](https://developer.nrel.gov/)
  - [CDSAPI](https://cds.climate.copernicus.eu/api-how-to)
  - [OpenCage Geocoding API](https://opencagedata.com/api)
  - [OpenAI API](https://platform.openai.com/docs/overview)
- **Others**
  - [Python 3.9](https://www.python.org/)
  - [Node.js 16.x](https://nodejs.org/)
  - [Virtualenv](https://virtualenv.pypa.io/en/latest/)

## 📋 Prerequisites

Before you begin, ensure you have met the following requirements:

 **Python** 3.9 or higher installed on your machine
- **Node.js** and **npm** installed for frontend development
- **Git** for version control
- **API Keys** for the external services:
  - OpenAI API Key
  - ElectricityMap API Key
  - NREL API Key
  - CDSAPI Key
  - OpenCage Geocoding API Key

## 🚀 Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/IW714/economics.git
   cd economics
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
    pip install -r requirements.txt
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