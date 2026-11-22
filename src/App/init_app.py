from dotenv import load_dotenv

from src.Service.JWTService import JwtService

load_dotenv()
jwt_service = JwtService()
