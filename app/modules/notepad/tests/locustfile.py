from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing


class NotepadBehavior(TaskSet):
    def on_start(self):
        self.index()

    @task(2)
    def index(self):
        response = self.client.get("/notepad")

        if response.status_code != 200:
            print(f"Notepad index failed: {response.status_code}")
        else:
            print("Notepad accesed successfully.")

    @task(1)
    def create_task(self):
        print("Creating new note...")
        response = self.client.post("/notepad/create", json={"title": "Nota generada por Locust", "body": "Esto es una nota de prueba"})
        if response.status_code == 200:
            print("Nota creada correctamente.")
        else:
            print(f"Error al crear la nota: {response.status_code}")


class NotepadUser(HttpUser):
    tasks = [NotepadBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
