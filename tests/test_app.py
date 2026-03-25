
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Utility to reset activities for each test (since in-memory DB is shared)
def reset_activities():
    for activity in activities.values():
        if "participants" in activity:
            activity["participants"] = []
    # Add initial participants for known activities
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
    activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]
    activities["Basketball Team"]["participants"] = ["alex@mergington.edu"]
    activities["Tennis Club"]["participants"] = ["lucas@mergington.edu"]
    activities["Drama Club"]["participants"] = ["grace@mergington.edu", "james@mergington.edu"]
    activities["Art Studio"]["participants"] = ["isabella@mergington.edu"]
    activities["Debate Team"]["participants"] = ["noah@mergington.edu", "ava@mergington.edu"]
    activities["Science Club"]["participants"] = ["mia@mergington.edu"]

@pytest.fixture(autouse=True)
def setup():
    reset_activities()


def test_list_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_success():
    resp = client.post("/activities/Chess Club/signup?email=tester@mergington.edu")
    assert resp.status_code == 200
    assert "Signed up tester@mergington.edu for Chess Club" in resp.json()["message"]
    # Confirm participant added
    resp2 = client.get("/activities")
    assert "tester@mergington.edu" in resp2.json()["Chess Club"]["participants"]


def test_signup_duplicate():
    resp = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"]


def test_signup_activity_not_found():
    resp = client.post("/activities/Unknown/signup?email=someone@mergington.edu")
    assert resp.status_code == 404
    assert "Activity not found" in resp.json()["detail"]


def test_unregister_success():
    # Remove existing participant
    resp = client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
    assert resp.status_code == 200
    assert "Removed michael@mergington.edu from Chess Club" in resp.json()["message"]
    # Confirm participant removed
    resp2 = client.get("/activities")
    assert "michael@mergington.edu" not in resp2.json()["Chess Club"]["participants"]


def test_unregister_not_found():
    resp = client.post("/activities/Chess Club/unregister?email=notfound@mergington.edu")
    assert resp.status_code == 404
    assert "Participant not found" in resp.json()["detail"]


def test_unregister_activity_not_found():
    resp = client.post("/activities/Unknown/unregister?email=someone@mergington.edu")
    assert resp.status_code == 404
    assert "Activity not found" in resp.json()["detail"]


def test_signup_case_insensitive():
    resp = client.post("/activities/Chess Club/signup?email=MICHAEL@mergington.edu")
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"]


def test_unregister_case_insensitive():
    # Should remove even if case differs
    resp = client.post("/activities/Chess Club/unregister?email=MICHAEL@mergington.edu")
    assert resp.status_code == 200
    assert "Removed MICHAEL@mergington.edu from Chess Club" in resp.json()["message"]
    resp2 = client.get("/activities")
    assert "michael@mergington.edu" not in resp2.json()["Chess Club"]["participants"]
