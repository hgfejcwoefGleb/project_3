from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import random
from typing import Optional
from starlette.middleware.sessions import SessionMiddleware
import secrets
from utils import read_questions, generate_question_html

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_hex(32),
    session_cookie="session_cookie"
)

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")

# Модели данных
class LoginData(BaseModel):
    username: str
    password: str

# "База данных" пользователей (в реальном приложении используйте настоящую БД)
USERS = {
    "admin": {"password": "admin123", "role": "admin"}
}

# Функция для проверки аутентификации
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

# Главная страница с выбором типа входа
@app.get("/", response_class=HTMLResponse)
async def login_choice(request: Request):
    return templates.TemplateResponse("sign_in.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_choice(request: Request):
    return templates.TemplateResponse("sign_in.html", {"request": request})

# Обработка выбора типа входа
@app.post("/login")
async def handle_login_choice(request: Request, guest: Optional[str] = Form(None), admin: Optional[str] = Form(None)):
    if guest:
        request.session["user"] = {"role": "guest"}
        return RedirectResponse(url="/game", status_code=303)
    elif admin:
        return RedirectResponse(url="/admin_login", status_code=303)
    return RedirectResponse(url="/", status_code=303)

#тут
# Страница входа для админа
@app.get("/admin_login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

# Обработка входа админа
@app.post("/admin_login")
async def handle_admin_login(request: Request, login: str = Form(...), password: str = Form(...)):
    user = USERS.get(login)
    if not user or user["password"] != password:
        return templates.TemplateResponse("admin_login.html", 
                                        {"request": request, "error": "Неверные учетные данные!"})
    
    request.session["user"] = {"login": login, "role": user["role"]}
    return RedirectResponse(url="/admin_main_window", status_code=303)

#Страница главного окна админа
@app.get("/admin_main_window", response_class=HTMLResponse)
async def admin_main_window_page(request: Request):
    return templates.TemplateResponse("admin_main_window.html", {"request": request})

#Страница вопросов
@app.get("/questions", response_class=HTMLResponse)
async def questions_page(request: Request):
    questions = read_questions('questions.txt')
    questions_html = generate_question_html(questions)

    with open('templates/questions.html', 'r', encoding='utf-8') as file:
        template = file.read()

    final_html = template.replace("{{questions}}", questions_html)

    with open('templates/questions.html', 'w', encoding='utf-8') as file:
        file.write(final_html)
    return templates.TemplateResponse("questions.html", {"request": request})

#Страница рейтинга
@app.get("/progress", response_class=HTMLResponse)
async def progress_page(request: Request):
    return templates.TemplateResponse("progress.html", {"request": request})

#Страница с правилами
@app.get("/rules", response_class=HTMLResponse)
async def rules_page(request: Request):
    return templates.TemplateResponse("rules.html", {"request": request})

#Показываем страницу с вопросом
@app.get("/game", response_class=HTMLResponse)
def show_game(request: Request):
    user = get_current_user(request)
    questions = read_questions("questions.txt")

    if "game_index" not in request.session:
        request.session["game_index"] = 0
        request.session["score"] = 0

    idx = request.session["game_index"]
    if idx >= len(questions):
        return RedirectResponse("/result", status_code=303)

    current = questions[idx]

    return templates.TemplateResponse("game.html", {
        "request": request,
        "question_text": current,
        "answers": ["a", "b", "c"],
        "hint_text": "Подсказка: Внимательно читай формулировку вопроса"
    })

#Обработка ответа
@app.post("/submit")
async def submit_answer(request: Request, selected_answer: str = Form(...)):
    questions = read_questions("questions.txt")
    idx = request.session["game_index"]
    current = questions[idx]

    correct_raw = current.split("Правильный ответ:")[-1].strip().lower()
    correct_letter = correct_raw[0]  # "a" из "a) НОБЧ"

    if selected_answer.lower() == correct_letter:
        request.session["score"] += 1

    request.session["game_index"] += 1
    return RedirectResponse("/game", status_code=303)

#Завершение игры
@app.post("/end_game")
def end_game(request: Request):
    return RedirectResponse("/result", status_code=303)

#Страница результата
@app.get("/result", response_class=HTMLResponse)
def show_result(request: Request):
    score = request.session.get("score", 0)
    total = len(read_questions("questions.txt"))
    return templates.TemplateResponse("result_offline.html", {
        "request": request,
        "score": score,
        "total": total
    })

# Выход из системы
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)