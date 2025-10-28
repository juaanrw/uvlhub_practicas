import pytest

from app import db
from app.modules.auth.models import User
from app.modules.conftest import login, logout
from app.modules.profile.models import UserProfile
from app.modules.notepad.models import Notepad

@pytest.fixture(scope='module')
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        user_test = User(email="user@example.com", password="test1234")
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


def test_sample_assertion(test_client):
    """
    Sample test to verify that the test framework and environment are working correctly.
    It does not communicate with the Flask application; it only performs a simple assertion to
    confirm that the tests in this module can be executed.
    """
    greeting = "Hello, World!"
    assert greeting == "Hello, World!", "The greeting does not coincide with 'Hello, World!'"

def test_list_empty_notepad_get(test_client):
    """
    Tests access to the empty notepad list via GET request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/notepad")
    assert response.status_code == 200, "The notepad page could not be accessed."
    assert b"You have no notepads." in response.data, "The expected content is not present on the page"

    logout(test_client)

def test_create_notepad(test_client):
    """
    Tests creating a new notepad via POST request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    data = {
        "title": "Test Notepad",
        "body": "This is a test notepad."
    }
    response = test_client.post("/notepad/create", data=data, follow_redirects=True)
    assert response.status_code == 200, "Failed to create notepad."

    # Confirm notepad exists in DB
    user = User.query.filter_by(email="user@example.com").first()
    notepad = Notepad.query.filter_by(user_id=user.id, title="Test Notepad").first()
    assert notepad is not None, "Notepad was not created in the database."

    logout(test_client)

def test_edit_notepad(test_client):
    """
    Tests editing an existing notepad via POST request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    user = User.query.filter_by(email="user@example.com").first()
    notepad = Notepad.query.filter_by(user_id=user.id, title="Test Notepad").first()
    assert notepad is not None, "Notepad to edit does not exist."

    edit_data = {
        "title": "Edited Notepad",
        "body": "This notepad has been edited."
    }
    response = test_client.post(f"/notepad/edit/{notepad.id}", data=edit_data, follow_redirects=True)
    assert response.status_code == 200, "Failed to edit notepad."

    # Confirm changes in DB
    edited_notepad = Notepad.query.get(notepad.id)
    assert edited_notepad.title == "Edited Notepad", "Notepad title was not updated."
    assert edited_notepad.body == "This notepad has been edited.", "Notepad body was not updated."

    logout(test_client)

def test_show_notepad(test_client):
    """
    Tests viewing the details of a notepad via GET request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    user = User.query.filter_by(email="user@example.com").first()
    notepad = Notepad.query.filter_by(user_id=user.id).first()
    assert notepad is not None, "No notepad found to show."

    response = test_client.get(f"/notepad/{notepad.id}")
    assert response.status_code == 200, "Failed to access notepad details page."
    assert bytes(notepad.title, "utf-8") in response.data, "Notepad title not found in response."
    assert bytes(notepad.body, "utf-8") in response.data, "Notepad body not found in response."

    logout(test_client)

def test_delete_notepad(test_client):
    """
    Tests deleting an existing notepad via POST request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    user = User.query.filter_by(email="user@example.com").first()
    notepad = Notepad.query.filter_by(user_id=user.id).first()
    assert notepad is not None, "No notepad found to delete."

    response = test_client.post(f"/notepad/delete/{notepad.id}", follow_redirects=True)
    assert response.status_code == 200, "Failed to delete notepad."

    # Confirm notepad is deleted from DB
    deleted_notepad = Notepad.query.get(notepad.id)
    assert deleted_notepad is None, "Notepad was not deleted from the database."

    logout(test_client)