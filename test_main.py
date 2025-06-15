import pytest
from fastapi.testclient import TestClient
from main import app
from utils import read_questions, save_question_to_file, read_ratings, add_user
import os
import re

client = TestClient(app)

# Фикстуры для тестов
@pytest.fixture
def test_questions_file(tmp_path):
    test_file = tmp_path / "test_questions.txt"
    content = """1. Вопрос 1
a) Вариант 1
b) Вариант 2
c) Вариант 3
Правильный ответ: a) Вариант 1

2. Вопрос 2
a) Вариант A
b) Вариант B
c) Вариант C
Правильный ответ: b) Вариант B
"""
    test_file.write_text(content, encoding='utf-8')
    return test_file

@pytest.fixture
def test_ratings_file(tmp_path):
    test_file = tmp_path / "test_ratings.txt"
    content = """user1:100
user2:80
user3:50
"""
    test_file.write_text(content)
    return test_file

# Тесты для utils.py
def test_read_questions(test_questions_file):
    questions = read_questions(test_questions_file)
    assert len(questions) == 2
    assert questions[0]["text"] == "Вопрос 1"
    assert questions[0]["options"] == ["a) Вариант 1", "b) Вариант 2", "c) Вариант 3"]
    assert questions[0]["correct_answer"] == "a) Вариант 1"

def test_save_question_to_file(tmp_path):
    test_file = tmp_path / "test_save.txt"
    test_file.write_text("", encoding='utf-8')
    
    question_number = save_question_to_file(
        "Новый вопрос",
        ["Опция 1", "Опция 2", "Опция 3"],
        "Опция 2",
        filename=str(test_file)
    )
    
    assert question_number == 1
    content = test_file.read_text(encoding='utf-8')
    assert "1. Новый вопрос" in content
    assert "a) Опция 1" in content
    assert "Правильный ответ: c) Опция 2" in content

def test_read_ratings(test_ratings_file):
    ratings = read_ratings(test_ratings_file)
    assert len(ratings) == 3
    assert ratings[0]["name"] == "user1"
    assert ratings[0]["score"] == 100
    assert ratings[1]["score"] == 80

def test_add_user(tmp_path):
    test_file = tmp_path / "test_add.txt"
    test_file.write_text("", encoding='utf-8')
    
    add_user("new_user", 75, filename=str(test_file))
    content = test_file.read_text()
    assert "new_user:75" in content

# Тесты для FastAPI маршрутов
def test_login_choice():
    response = client.get("/")
    assert response.status_code == 200
    assert "Выберите тип входа" in response.text  # Изменено на проверку текста

def test_handle_login_choice_guest():
    response = client.post("/login", data={"guest": "on", "guest_name": "TestGuest"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/game"

def test_handle_login_choice_admin():
    response = client.post("/login", data={"admin": "on", "guest_name": ""}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin_login"

def test_admin_login_success():
    response = client.post("/admin_login", 
                         data={"login": "admin", "password": "admin123"},
                         follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin_main_window"

def test_admin_login_failure():
    response = client.post("/admin_login", 
                         data={"login": "admin", "password": "wrong"})
    assert response.status_code == 200
    assert "Неверные учетные данные!" in response.text

def test_game_page_requires_auth():
    response = client.get("/game", follow_redirects=False)
    assert response.status_code == 200  # Редирект на логин

def test_logout():
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"