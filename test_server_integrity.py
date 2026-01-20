
import requests
import json

SERVER_URL = "http://localhost:8080"

def test_get_request():
    response = requests.get(SERVER_URL)
    assert response.status_code == 200
    assert "Gemini Code Search" in response.text
    print("GET request test passed")


def test_post_request_no_file():
    data = {
        "prompt": "test prompt"
    }
    response = requests.post(SERVER_URL, data=data)
    assert response.status_code == 200
    assert "No code provided" in response.text
    print("POST request test passed")


if __name__ == "__main__":
    test_get_request()
    test_post_request_no_file()
