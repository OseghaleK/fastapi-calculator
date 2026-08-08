"""Integration tests that call the API endpoints through FastAPI."""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_the_home_page_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "Calculator" in response.text


@pytest.mark.parametrize(
    "endpoint, a, b, expected",
    [
        ("add", 23, 34, 57),
        ("add", -23, 23, 0),
        ("add", 2.5, 2.5, 5.0),
        ("subtract", 34, 23, 11),
        ("subtract", 23, 34, -11),
        ("subtract", 0, 23, -23),
        ("multiply", 23, 2, 46),
        ("multiply", 34, 0, 0),
        ("multiply", -2, 23, -46),
        ("divide", 34, 2, 17),
        ("divide", 23, 2, 11.5),
        ("divide", 46, 23, 2),
    ],
)
def test_each_endpoint_returns_the_right_answer(endpoint, a, b, expected):
    response = client.post(f"/{endpoint}", json={"a": a, "b": b})
    assert response.status_code == 200
    assert response.json()["result"] == expected


@pytest.mark.parametrize("a", [23, 0, -34])
def test_dividing_by_zero_returns_a_400(a):
    response = client.post("/divide", json={"a": a, "b": 0})
    assert response.status_code == 400
    # The custom HTTPException handler reshapes the body into an "error"
    # key rather than FastAPI's usual "detail".
    assert response.json()["error"] == "Cannot divide by zero!"


@pytest.mark.parametrize(
    "payload",
    [
        {"a": 23},
        {"b": 34},
        {},
        {"a": "twenty three", "b": 34},
        {"a": 23, "b": "lebron"},
        {"a": None, "b": None},
    ],
)
@pytest.mark.parametrize("endpoint", ["add", "subtract", "multiply", "divide"])
def test_bad_payloads_are_rejected(endpoint, payload):
    # The RequestValidationError handler turns FastAPI's default 422 into
    # a 400, which is why these do not assert 422.
    response = client.post(f"/{endpoint}", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()


def test_an_unknown_endpoint_is_a_404():
    response = client.post("/modulo", json={"a": 23, "b": 34})
    assert response.status_code == 404


@pytest.mark.parametrize("endpoint", ["add", "subtract", "multiply", "divide"])
def test_get_is_not_allowed_on_the_operation_routes(endpoint):
    assert client.get(f"/{endpoint}").status_code == 405
