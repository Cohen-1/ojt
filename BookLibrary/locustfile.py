from locust import HttpUser, task, between, SequentialTaskSet
import random
import string

def rand_text(prefix, n=6):
    return prefix + "_" + "".join(random.choices(string.ascii_letters + string.digits, k=n))

class BookFlow(SequentialTaskSet):
    def on_start(self):
        payload = {"title": rand_text("Title"), "author": rand_text("Author")}
        with self.client.post("/books", json=payload, catch_response=True) as r:
            if r.status_code == 201:
                self.book = r.json()
            else:
                r.failure(f"Create failed {r.status_code}")
                self.book = None

    @task
    def list_books(self):
        self.client.get("/books")

    @task
    def update_book(self):
        if self.book:
            payload = {"title": rand_text("UpdTitle"), "author": rand_text("UpdAuthor")}
            self.client.put(f"/books/{self.book['id']}", json=payload)

    @task
    def delete_book(self):
        if self.book:
            self.client.delete(f"/books/{self.book['id']}")
        # create a new one again to keep the flow going
        payload = {"title": rand_text("Title"), "author": rand_text("Author")}
        r = self.client.post("/books", json=payload)
        if r.status_code == 201:
            self.book = r.json()

class WebsiteUser(HttpUser):        # 👈 this is what Locust looks for
    tasks = [BookFlow]
    wait_time = between(0.5, 2.0)
