# Gunicorn reads this file automatically when it starts.
# Render gives the app a port number in the PORT setting; listen on all addresses there.
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 2
