import os

class Config:
    SECRET_KEY = 'pawanyadav211191!@#'
    SQLALCHEMY_DATABASE_URI = 'postgresql://pawan:Pawan211191@localhost:5432/controlflow_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size