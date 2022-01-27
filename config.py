import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

tok = os.getenv('token')
id = os.getenv('id')
user = os.getenv('user')
host = os.getenv('host')
sword = os.getenv('password')

I18N_DOMAIN = 'mybot'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'
