import os
class Config:
        SECRET_KEY = 'MuskanSharda'
        JWT_SECRET_KEY = 'MakeMyTripApp'
        GOOGLE_CLIENT_ID = '793208375537-ph8dbkidb76bgr5pqbgu35n3934443pe.apps.googleusercontent.com'
        GOOGLE_CLIENT_SECRET = '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'
        GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

        MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')  # So it can read 'db' inside Docker
        MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '123456')
        MYSQL_DB = os.environ.get('MYSQL_DB', 'makemytripfinal')