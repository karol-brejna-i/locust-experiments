from locust import HttpLocust, TaskSet, task, web, runners, events, InterruptTaskSet
from flask import request, redirect

@web.app.route("/login", methods=['POST'])
def login_action():
    username = request.values.get("username")
    password = request.values.get("password")

    print(f"request payload: username {username}, password {password}")

    return "OK"

@web.app.route("/protected/resource")
def resource():
    print("resource")
    username = request.values.get("username")
    password = request.values.get("password")
    print(f"resource for: username {username}, password {password}")
    return "OK"


class UserBehaviour(TaskSet):
    USER_CREDENTIALS = [
        ("user1", "password"),
        ("user2", "password"),
        ("user3", "password"),
    ]

    def on_start(self):
        if len(self.USER_CREDENTIALS) > 0:
            self.user, self.passw = self.USER_CREDENTIALS.pop()
            self.client.post("/login", {"username": self.user, "password": self.passw})
        else:
            print("Nothing else to do....")
            # raise InterruptTaskSet(True)
            raise Exception("don't want to live anymore")


    @task(1)
    def some_task(self):
        # user should be logged in here (unless the USER_CREDENTIALS ran out)
        result = self.client.get(f"/protected/resource?username={self.user}&password={self.passw}")
        print(f"result: {result.text}")


    def on_stop(self):
        print(f" stopping for {self.user}&password={self.passw}")


class User(HttpLocust):
    task_set = UserBehaviour
    min_wait = 1000
    max_wait = 1000