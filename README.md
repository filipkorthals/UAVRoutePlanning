# UAVRoutePlanning

Application designed for interactive route planning of UAVs. Using outline detection algorithms based on satelite images the program designates areas to be covered by the flight. It also takes into account waypoints chosen by the user, speed, and opitmal flight time.

## Setup

After cloning the repo go to the root directory to setup the project. 

### Frontend 

1. Open the frontend directory
```bash
cd frontend
```

2. Install required modules (this can take a while)
```bash
npm install
```

3. Create your own `.env` file
- **MacOS/Linux**
  ```bash
  cp .env.local.example .env.local
  ```
- **Windows**
  ```bash
  copy .env.local.example .env.local
  ```

4. Go to the [Google Cloud Console](https://console.cloud.google.com/google/maps-apis/credentials) and copy `Maps Platform API Key`. You need to paste it into the `.env.local` file.

5. Run your development server!
```bash
npm run dev
```

### API

To setup API for this project you need to open a new terminal because both frontend and backend have to work simultaneously.\
Go to the root directory again.

1. Open the API directory
```bash
cd api
```

2. Create a virtual environment
- **MacOS/Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```
- **Windows**
```bash
python -m venv .venv
.venv/Scripts/activate
```

From now on, every command must be run with the virtual environment active.

3. Install required modules
```bash
pip install —upgrade pip    # This is not necessary, but it can help avoid potential errors
pip install -r requirements.txt
```

4. Run the backend server!
```bash
flask run -p 5001
```
