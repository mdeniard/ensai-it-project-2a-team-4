import datetime
import os
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from jwt import ExpiredSignatureError

from src.Service.JWTService import JwtService

jwt_service = JwtService("mysecret")


@freeze_time("2024-08-26 12:00:00")
def test_encode_jwt():
    user_id = "myUser"
    jwtResponse = jwt_service.encode_jwt(user_id=user_id)
    assert (
        jwtResponse.access_token
        == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoibXlVc2VyIiwiZXhwaXJ5X3RpbWVzdGFtcCI6MTcyNDY3NDIwMC4wfQ.eUjNbpMCDNuPESsMHF2dpeRlDl6fMJmjUWsHSZT_n1Q"  # noqa: E501
    )


@freeze_time("2024-08-26 12:00:00")
def test_decode_jwt():
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoibXlVc2VyIiwiZXhwaXJ5X3RpbWVzdGFtcCI6MTcyNDY3NDIwMC4wfQ.eUjNbpMCDNuPESsMHF2dpeRlDl6fMJmjUWsHSZT_n1Q"  # noqa: E501
    decoded_jwt = jwt_service.decode_jwt(jwt)
    assert decoded_jwt.get("user_id") == "myUser"
    assert datetime.datetime.fromtimestamp(decoded_jwt.get("expiry_timestamp")) == datetime.datetime.fromisoformat(
        "2024-08-26 12:10:00"
    )


@freeze_time("2024-08-26 12:00:00")
def test_init_reads_secret_from_environment():
    # GIVEN no secret is passed to the constructor
    with patch.dict(os.environ, {"JWT_SECRET": "mysecret"}):
        service = JwtService()

    # THEN the secret is read from the environment variable
    assert service.secret == "mysecret"


@freeze_time("2024-08-26 12:00:00")
def test_validate_user_jwt_ok():
    # GIVEN a valid (not expired) token for user "myUser"
    token = jwt_service.encode_jwt(user_id="myUser").access_token

    # WHEN we validate it
    user_id = jwt_service.validate_user_jwt(token)

    # THEN we get the user id
    assert user_id == "myUser"


@freeze_time("2024-08-26 12:20:00")
def test_validate_user_jwt_expired():
    # GIVEN a token created 20 minutes ago (it expired 10 minutes after creation)
    with freeze_time("2024-08-26 12:00:00"):
        token = jwt_service.encode_jwt(user_id="myUser").access_token

    # WHEN we validate it / THEN ExpiredSignatureError
    with pytest.raises(ExpiredSignatureError):
        jwt_service.validate_user_jwt(token)
