# Thursday Cookie Lab Signup

A signup page for the **Learn to Bake Cookies Club**, which meets on Thursdays in the Great Hall.
Students pick a Thursday and one of three baking sessions:

- Chocolate Chip Cookies (3:00 PM)
- Sugar Cookies (4:00 PM)
- Oatmeal Cookies (5:00 PM)

All names used for testing are fictional.

## Features

- **Sign up** with a name, a Thursday (the next four, starting this week) and a session
- **Clear error messages** for a missing name, Thursday or session, with the other choices kept
- **Prevent duplicate signups** (one spot per name per Thursday)
- **Switch activities** by signing up again with a different session on the same Thursday
- **Cancel a signup** by entering your name, Thursday and session, then pressing *Cancel My Signup*
  (only from the browser that made the signup)
- **Limit available spots** to 10 per session, with "spots left" and *Full* shown on each choice
- **Roster** that stays hidden until you search for a name or choose Thursdays
  - **Count by activity** (for example, *3 of 10 spots*)
  - **Names sorted A–Z**
  - **Search past sessions**
- **Mark attendance** on Thursdays that have arrived, for club leaders who enter the leader code
- Keyboard friendly, screen-reader labels, and a layout that works on phones
- Cookie-themed design: cookie session buttons, scattered baking drawings and a rolling-pin cursor

## Run it on your computer

- **Runtime:** Python 3 (Render uses Python 3.12 from `.python-version`; tested locally with Python 3.9)
- **Install:** `pip install -r requirements.txt`
- **Start:** `gunicorn app:app` (Mac/Linux) or `python app.py` (any computer, including Windows)
- **Local address:** http://localhost:10000 with `gunicorn app:app`, or http://localhost:8000 with `python app.py`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Without a `DATABASE_URL` setting, signups are saved in a local SQLite file, `signups.db`
(ignored by git).

**One signup to test:** enter the name `Brock Powell`, keep this week's Thursday,
pick **Chocolate Chip Cookies (3:00 PM)** and press **Sign Up**. Expect
`✓ Thanks, Brock Powell! You're signed up for Chocolate Chip Cookies (3:00 PM) on Thursday, …`.
Then type `Brock` in **Search names** to find him on the roster.

## How it's built

| File | What it is |
|---|---|
| `app.py` | The Flask server: serves the page and the `/api/...` routes, and saves signups |
| `index.html` | The whole page: layout, styles, drawings and browser code in one file |
| `requirements.txt` | Python packages: Flask, gunicorn, psycopg2-binary |
| `gunicorn.conf.py` | Makes gunicorn listen on `0.0.0.0` at the `PORT` setting |
| `.python-version` | Tells Render which Python to use |
| `design.md` | The original design written for the class assignment, before the extra features |

- One server serves the page and the API from one address. The page calls relative paths such as
  `/api/signups`, never `http://localhost`.
- **Storage:** when the `DATABASE_URL` setting is present, signups are saved in **PostgreSQL**.
  The table is created if it's missing and existing signups are never deleted on restart.
  All queries are parameterized.
- **Settings (names only, never put the values in this repository):**
  - `DATABASE_URL`: the Render PostgreSQL **Internal** Database URL (required on Render)
  - `LEADER_KEY`: a code you make up for club leaders to mark attendance (optional;
    without it, attendance marking is turned off)

## Render settings (deploy card)

| Field | Value |
|---|---|
| Repository | `MichelleSanchezMU/Cookie-lab-signup` |
| Branch | `main` |
| Language | **Python 3** |
| Root Directory | *(blank)* |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Instance type | **Free** ($0 / month) |
| Setting names | `DATABASE_URL`, `LEADER_KEY` (optional) |
| Database tested locally | SQLite |

Render picks the language from the form, so make sure **Language** says **Python 3**, not Docker.
