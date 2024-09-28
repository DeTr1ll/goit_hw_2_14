import pytest
from sqlalchemy.orm import Session
from app import crud, models, schemas

@pytest.fixture
def db_session():
    # Создание тестовой сессии БД
    from app.database import SessionLocal, engine
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    models.Base.metadata.drop_all(bind=engine)

def test_create_contact(db_session):
    contact_data = schemas.ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        birthday="1990-01-01"
    )
    contact = crud.create_contact(db_session, contact_data)
    assert contact.id is not None
    assert contact.email == contact_data.email

def test_get_contact(db_session):
    contact_data = schemas.ContactCreate(
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone="1234567890",
        birthday="1990-01-01"
    )
    created_contact = crud.create_contact(db_session, contact_data)
    fetched_contact = crud.get_contact(db_session, created_contact.id)
    assert fetched_contact.email == created_contact.email

def test_update_contact(db_session):
    contact_data = schemas.ContactCreate(
        first_name="Tom",
        last_name="Smith",
        email="tom.smith@example.com",
        phone="1234567890",
        birthday="1990-01-01"
    )
    created_contact = crud.create_contact(db_session, contact_data)
    update_data = schemas.ContactUpdate(first_name="Thomas")
    updated_contact = crud.update_contact(db_session, created_contact.id, update_data)
    assert updated_contact.first_name == "Thomas"

def test_delete_contact(db_session):
    contact_data = schemas.ContactCreate(
        first_name="Anna",
        last_name="Bell",
        email="anna.bell@example.com",
        phone="1234567890",
        birthday="1990-01-01"
    )
    created_contact = crud.create_contact(db_session, contact_data)
    deleted_contact = crud.delete_contact(db_session, created_contact.id)
    assert deleted_contact.id == created_contact.id

def test_search_contacts(db_session):
    contact_data = schemas.ContactCreate(
        first_name="John",
        last_name="Smith",
        email="john.smith@example.com",
        phone="1234567890",
        birthday="1990-01-01"
    )
    crud.create_contact(db_session, contact_data)
    results = crud.search_contacts(db_session, "Smith")
    assert len(results) == 1