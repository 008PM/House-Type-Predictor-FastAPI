# 1️⃣ Create a virtual environment
python3 -m venv .venv

# 2️⃣ Activate it
source .venv/bin/activate        # Mac/Linux
# OR on Windows:
# .venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt
# -----------------------------------------------------------



For running just run : uvicorn app.main:app --reload
and swagger endpoint at : http://127.0.0.1:8000/docs