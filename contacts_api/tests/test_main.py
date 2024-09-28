import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine
from app import models, schemas

@pytest.fixture
def db_session():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    models.Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_create_contact(client, db_session):
    contact_data = {
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice.johnson@example.com",
        "phone": "0987654321",
        "birthday": "1995-05-15"
    }
    response = client.post("/contacts/", json=contact_data)
    assert response.status_code == 200
    assert response.json()["email"] == contact_data["email"]

def test_get_contact(client, db_session):
    contact_data = {
        "first_name": "Bob",
        "last_name": "Brown",
        "email": "bob.brown@example.com",
        "phone": "1234567890",
        "birthday": "1992-02-02"
    }
    response = client.post("/contacts/", json=contact_data)
    contact_id = response.json()["id"]
    
    response = client.get(f"/contacts/{contact_id}")
    assert response.status_code == 200
    assert response.json()["email"] == contact_data["email"]

def test_update_contact(client, db_session):
    contact_data = {
        "first_name": "Charlie",
        "last_name": "Green",
        "email": "charlie.green@example.com",
        "phone": "1234567890",
        "birthday": "1993-03-03"
    }
    response = client.post("/contacts/", json=contact_data)
    contact_id = response.json()["id"]
    
    update_data = {"first_name": "Charles"}
    response = client.put(f"/contacts/{contact_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Charles"

def test_delete_contact(client, db_session):
    contact_data = {
        "first_name": "Diana",
        "last_name": "Blue",
        "email": "diana.blue@example.com",
        "phone": "1234567890",
        "birthday": "1991-01-01"
    }
    response = client.post("/contacts/", json=contact_data)
    contact_id = response.json()["id"]

    response = client.delete(f"/contacts/{contact_id}")
    assert response.status_code == 200
    assert response.json()["id"] == contact_id
