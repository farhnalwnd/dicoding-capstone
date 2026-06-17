import requests
import json

base_url = "http://localhost:8000/api/v1"

# 1. Register
reg_data = {
    "name": "Test User",
    "email": "test_metrics@example.com",
    "password": "password123",
    "role": "hr"
}
r = requests.post(f"{base_url}/auth/register", json=reg_data)
token = ""
if r.status_code == 201:
    token = r.json()["access_token"]
else:
    # login
    l_data = {"email": "test_metrics@example.com", "password": "password123"}
    r = requests.post(f"{base_url}/auth/login", json=l_data)
    token = r.json()["access_token"]

# 2. Hit match-detailed
headers = {"Authorization": f"Bearer {token}"}

# We need to send form data and a file for match-detailed
data = {
    "job_description": "Looking for a Python Backend Developer with Docker and cloud experience.",
    "domain": "it"
}

print("Running API requests to populate metrics...")
for i in range(3):
    # Important: files must be re-opened or re-created in requests for each loop
    files = {
        "cv": ("cv.txt", "I am a skilled software engineer with 5 years of Python, Docker, and Kubernetes experience.", "text/plain")
    }
    res = requests.post(f"{base_url}/match-detailed", headers=headers, files=files, data=data)
    print(f"Request {i+1}: {res.status_code}")

print("Done generating metrics via HTTP!")
