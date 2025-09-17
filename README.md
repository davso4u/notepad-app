# Note Pad Project

A simple **Flask-based note-taking app** where users can register, log in, and manage notes.  
The app uses **SQL Server** for data storage and fetches random news headlines from an external API on the homepage.

## Features

-  User registration and login with password hashing.  
-  Add, view, update, and delete notes.  
-  Mark notes as completed with a toggle option.  
-  SQL Server database integration using SQLAlchemy.  
-  Random news headline displayed from an external API.  

## How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/note_pad.git
   cd note_pad
   
2. **Create and activate a virtual environment**:
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

3. **Install dependencies**
   pip install -r requirements.txt

4. **Set up environment variables**:
Create a .env file in the project root and add:
FLASK_SECRET_KEY=your_secret_key
SQL_SERVER=your_sql_server
SQL_DATABASE=db_notes
SQL_DRIVER=ODBC Driver 17 for SQL Server
NEWS_API_KEY=your_news_api_key

5. **Run the App**
   flask run

6. **Open your browser at:**
👉 http://127.0.0.1:5000

**Notes**
Replace environment variables with your own credentials.
Requires SQL Server installed and running.
NEWS API key can be obtained from NewsAPI.org
