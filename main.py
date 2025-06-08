from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import random
from typing import Optional
from starlette.middleware.sessions import SessionMiddleware
import secrets
from utils import *

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
async def show_rating(request: Request):
    # Получаем данные рейтинга
    ratings = read_ratings()
    
    # Добавляем информацию о медалях (первые 3 места)
    for i, player in enumerate(ratings[:3], 1):
        player["medal"] = ["gold", "silver", "bronze"][i-1]
    
    return templates.TemplateResponse(
        "progress.html",
        {
            "request": request,
            "ratings": ratings
        }
    )

#Страница с правилами
@app.get("/rules", response_class=HTMLResponse)
async def rules_page(request: Request):
    return templates.TemplateResponse("rules.html", {"request": request})

#Страница добавления вопроса
@app.get("/add-question", response_class=HTMLResponse)
async def add_question_page(request: Request):
    return templates.TemplateResponse("add-question.html", {"request": request})

@app.post("/add-question", response_class=HTMLResponse)
async def save_question(
    request: Request,
    question: str = Form(...),
    correct_answer: str = Form(...),
    options: list = Form(...),  # ← Исправлено: options, а не answer_options_container
    answer_time: int = Form(...)
):
    # Сохраняем вопрос в файл
    question_number = save_question_to_file(question, options, correct_answer)

    # Возвращаем страницу с подтверждением
    return templates.TemplateResponse("add-question.html", {
        "request": request,
        "message": f"Вопрос #{question_number} успешно добавлен!"
    })
# Игра "Угадай число"
@app.get("/game", response_class=HTMLResponse)
async def game_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    if "secret" not in request.session:
        request.session["secret"] = random.randint(1, 100)
        request.session["attempts"] = 10
    
    return templates.TemplateResponse("game.html", {
        "request": request,
        "message": "Угадай число от 1 до 100!",
        "attempts": request.session["attempts"],
        "is_admin": user.get("role") == "admin"
    })

# Обработка попытки угадать число
@app.post("/guess")
async def handle_guess(request: Request, guess: int = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    secret = request.session["secret"]
    request.session["attempts"] -= 1
    attempts = request.session["attempts"]
    
    if guess == secret:
        message = f"🎉 Победа! Это число {secret}!"
        request.session.pop("secret", None)
        request.session.pop("attempts", None)
    elif attempts == 0:
        message = f"💥 Проигрыш! Число было: {secret}."
        request.session.pop("secret", None)
        request.session.pop("attempts", None)
    elif guess < secret:
        message = "⬆️ Больше!"
    else:
        message = "⬇️ Меньше!"
    
    return templates.TemplateResponse("game.html", {
        "request": request,
        "message": message,
        "attempts": attempts,
        "is_admin": user.get("role") == "admin",
        "game_over": guess == secret or attempts == 0
    })

# Выход из системы
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)