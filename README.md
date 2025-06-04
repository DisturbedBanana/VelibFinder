# Velib Station Finder

A desktop and web application to find and monitor Velib bike stations in Paris.

## Features

- Real-time station data
- Search stations by name
- View detailed bike information
- Monitor station status
- Available as both desktop application and web interface

## Desktop Version

### Requirements
- Python 3.7+
- Required packages (install using `pip install -r requirements.txt`):
  - requests
  - python-dotenv

### Running the Desktop App
1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python velib_gui.py
   ```

## Web Version

### Requirements
- Python 3.7+
- Required packages (install using `pip install -r web/requirements.txt`):
  - flask
  - flask-cors
  - requests
  - python-dotenv

### Running Locally
1. Install the requirements:
   ```bash
   pip install -r web/requirements.txt
   ```
2. Run the Flask server:
   ```bash
   cd web
   python api/app.py
   ```
3. Open your browser and navigate to `http://localhost:5000`

### Deploying to Vercel
1. Create a GitHub repository and push your code
2. Go to [Vercel](https://vercel.com)
3. Sign up/Login with your GitHub account
4. Click "New Project"
5. Import your repository
6. Configure the project:
   - Framework Preset: Other
   - Root Directory: web
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
7. Click "Deploy"

## Author
Lucas Guichard 