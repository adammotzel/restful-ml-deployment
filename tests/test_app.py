"""
Test the locally hosted app. Ensure the app is running 
before executing this script.
"""

import os
import requests

from dotenv import load_dotenv


server = os.getenv("SERVER_IP", "127.0.0.1")
port = 8000
BASE_URL = f"http://{server}:{port}"

print("URL:", BASE_URL)
print()

load_dotenv()
un = os.environ["AUTH_UN"]
pw = os.environ["AUTH_PW"]
auth = (un, pw)
bad_auth = ("BAD_USER", "CREDS")


def test_check():
    response = requests.get(f"{BASE_URL}/check", auth=auth)
    if response.status_code == 200:
        print("Health check passed:", response.json())
    else:
        print("Health check failed:", response.status_code)


test_data = {
    "identifier": ["a12", "b12", "c12"],
    "data": {
        "mean_radius": [12.34, 15.67, 10.11],
        "mean_texture": [19.54, 17.33, 18.45],
        "mean_perimeter": [78.12, 85.67, 70.22],
        "mean_area": [523.45, 600.34, 490.12],
        "mean_smoothness": [0.089, 0.112, 0.075],
        "mean_compactness": [0.112, 0.145, 0.110],
        "mean_concavity": [0.132, 0.134, 0.120],
        "mean_concave_points": [0.067, 0.072, 0.060],
        "mean_symmetry": [0.172, 0.160, 0.150],
        "mean_fractal_dimension": [0.059, 0.045, 0.051]
    }
}


def test_inference():
    response = requests.post(f"{BASE_URL}/inference", json=test_data, auth=auth)
    if response.status_code == 200:
        print("Inference result:", response.json())
    else:
        print("Inference failed:", response.status_code, response.text)


def test_unauthorized():
    response = requests.get(f"{BASE_URL}/check", auth=bad_auth)
    if response.status_code == 200:
        print("Auth test failed.")
    else:
        print("Auth test passed:", response.status_code, response.text)


if __name__ == "__main__":
    print("Running health check test...")
    test_check()

    print("\nRunning inference test...")
    test_inference()

    print("\nRunning bad auth test...")
    test_unauthorized()
