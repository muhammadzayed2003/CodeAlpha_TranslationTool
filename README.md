# CodeAlpha Translation Tool

A full-stack AI-powered translation application developed as part of the CodeAlpha Internship Program.

The project provides a modern web-based translation interface, user authentication, translation history, and a separate desktop translation application powered by Google's Gemini AI.

## Features

### Web Application

* AI-powered text translation
* Gemini 3.1 Flash-Lite integration
* User registration and login
* Secure session-based authentication
* Translation history
* Delete translation history
* Source and target language selection
* Custom language support
* Swap source and target languages
* Copy translated text
* Text-to-speech support
* Responsive modern interface
* Translation input limit of 5000 characters

### Desktop Application

* Standalone Tkinter translation application
* Gemini AI translation
* Source and target language selection
* Language swapping
* Copy translated result
* Clear input/output
* Keyboard shortcut for translation
* Background API processing
* Error handling

## Technologies Used

### Frontend

* React 19
* Vite
* JavaScript
* CSS

### Backend

* Python
* Flask
* Flask-CORS
* SQLite
* Requests
* Werkzeug

### AI

* Google Gemini 3.1 Flash-Lite

### Desktop Application

* Python Tkinter

## Project Structure

```text
CodeAlpha_TranslationTool/
│
├── backend/
│   ├── backend.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
└── Video Project demo.mp4
```

## Requirements

* Python 3.10+
* Node.js
* npm
* Google Gemini API key

## Backend Setup

Open PowerShell in the project directory.

Create and activate the virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Set the Gemini API key as an environment variable:

```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Start the Flask backend:

```powershell
python .\backend\backend.py
```

The backend runs on:

```text
http://127.0.0.1:5000
```

## Frontend Setup

Open another PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Then open the local Vite URL shown in the terminal.

## Desktop Application

From the project root:

```powershell
python app.py
```

Make sure `GEMINI_API_KEY` is configured before launching the application.

## API Endpoints

### Authentication

```text
POST /api/signup
POST /api/login
POST /api/logout
GET  /api/me
```

### Translation

```text
POST /api/translate
```

### History

```text
GET    /api/history
DELETE /api/history/<translation_id>
```

### Health Check

```text
GET /api/health
```

## Security

API keys and environment files should never be committed to GitHub.

The project's `.gitignore` excludes:

* Virtual environments
* Environment files
* Node modules
* Build files
* Local SQLite database
* Logs
* IDE configuration files

## CodeAlpha Internship

This project was developed as part of the **CodeAlpha Internship Program**.

**Project:** Translation Tool

**Repository:** `CodeAlpha_TranslationTool`

**Developer:** Muhammad Zayed Bin Gul Nawaz
