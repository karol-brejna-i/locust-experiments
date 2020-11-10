from locust import HttpUser, TaskSet, task


class UserTasks(TaskSet):

    @task
    def index(self):
        self.client.get("/")

    @task
    def stats(self):
        self.client.get("/stats/requests")


class WebsiteUser(HttpUser):
    task_set = UserTasks
