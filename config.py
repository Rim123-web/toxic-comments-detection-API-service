class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///toxicity.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ['http://127.0.0.1:5500']
