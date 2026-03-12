# Bob Family Tree API

A REST API built with Python (FastAPI) and MariaDB to manage a family tree database.

This project was built as a school exercise to practice API design, database constraints, and Python backend development.

---

## Tech Stack

- Python 3.12
- FastAPI
- MariaDB
- Pydantic v2
- Uvicorn

---

## Folder Structure

```
BDD-FastAPI/
├── main.py                  ← starts the app, plugs in all routers
├── requirements.txt         ← all dependencies
├── CONSTRAINTS.md           ← all business rules
├── database/
│   ├── connection.py        ← database connection
│   └── init.sql             ← run once to create the database and tables
└── routers/
    ├── person.py            ← create, read, update, delete persons
    ├── firstname.py         ← add, rename, delete firstnames
    ├── lastname.py          ← add, rename, delete lastnames
    └── relationship.py      ← add, get, delete parent-child links
```

---

## How to Install

**1 — Clone the project**
```bash
git clone https://github.com/yourname/BDD-FastAPI.git
cd BDD-FastAPI
```

**2 — Create and activate a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3 — Install dependencies**
```bash
pip install -r requirements.txt
```

**4 — Create the database**
```bash
sudo mariadb -u root < database/init.sql
```

**5 — Start the API**
```bash
uvicorn main:app --reload
```

**6 — Open the interactive docs**
```
http://localhost:8000/docs
```

---

## Database Connection

The connection is configured in `database/connection.py`:

```python
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="khris",
        password="cute",
        database="Bob_Family_Tree"
    )
```

Change `user` and `password` to match your MariaDB credentials.
