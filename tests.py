from unittest import TestCase
from app import app, User

app.config['WTF_CSRF_ENABLED'] = False


class UserTestCase(TestCase):

    def test_register_user(self):
        ex_user = User.register("exampleuser18", "password123")

        assert ex_user
        assert ex_user.username == "exampleuser18"
        assert ex_user.password != "password123"

    def test_register_user_route(self):
        with app.test_client() as client:
            d = {"username": "newuser89", "password": "password123"}
            r = client.post("/register", data = d, follow_redirects=True) 

            #print(r.data)
            assert r.status_code == 200
            
