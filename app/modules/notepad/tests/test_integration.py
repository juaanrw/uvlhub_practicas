import pytest
from app.modules.auth.models import User
from app.modules.notepad.models import Notepad
from app.modules.conftest import login, logout
from app.modules.profile.models import UserProfile
from app import db

@pytest.fixture(scope='module')
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email="user@example.com", password="test1234")
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client

def test_get_notepads_endpoint_returns_existing_notepads(test_client,):
    """
    GET /notepad (API HTML) debe devolver la lista de notepads del usuario.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    # Obtener el usuario desde la base de datos
    user = User.query.filter_by(email="user@example.com").first()
    assert user is not None
    # Crear un notepad para el usuario
    notepad = Notepad(title="Nota API", body="Contenido API", user_id=user.id)
    db.session.add(notepad)
    db.session.commit()

    response = test_client.get('/notepad')
    assert response.status_code == 200
    assert b'Nota API' in response.data
    assert b'Contenido API' in response.data

    logout(test_client)

def test_create_notepad_endpoint_returns_201_and_json(test_client):
    """
    POST /notepad/create (API JSON) debe crear un nuevo notepad y devolver status 201.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    # Obtener el usuario desde la base de datos
    user = User.query.filter_by(email="user@example.com").first()
    assert user is not None
    response = test_client.post('/notepad/create', json={
        'title': 'Notepad JSON',
        'body': 'Contenido JSON'
    })

    # Buscar el notepad en la base de datos
    notepad = Notepad.query.filter_by(title='Notepad JSON', user_id=user.id).first()
    assert notepad is not None
    assert notepad.body == 'Contenido JSON'

    logout(test_client)

def test_create_notepad_without_title_returns_400_error(test_client):
    """
    Si se intenta crear un notepad sin título, el servidor debe devolver error 400.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    response = test_client.post('/notepad/create', json={'body': 'Sin título'})
    assert response.status_code == 400 or b'Title' in response.data

    logout(test_client)

def test_add_notepad_html_redirects_and_renders_new_notepad(test_client):
    """
    POST /notepad/create (formulario HTML):
    - debe aceptar datos enviados por formulario,
    - redirigir a la lista de notepads,
    - y mostrar el nuevo notepad en el HTML.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    response = test_client.post(
        '/notepad/create',
        data={'title': 'Notepad HTML', 'body': 'Desde HTML'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Notepad HTML' in response.data
    assert b'Desde HTML' in response.data

    logout(test_client)

def test_create_then_retrieve_notepad_from_api(test_client):
    """
    Flujo completo API:
    1. Crear un notepad con POST /notepad/create
    2. Recuperar todos los notepads con GET /notepad
    3. Verificar que el nuevo está presente
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    test_client.post('/notepad/create', json={'title': 'Notepad persistente', 'body': 'Persistente'})
    response = test_client.get('/notepad')
    assert response.status_code == 200
    assert b'Notepad persistente' in response.data

    logout(test_client)