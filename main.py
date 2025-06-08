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
import logging
logging.basicConfig(level=logging.DEBUG)
from fastapi.responses import PlainTextResponse

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
#Перехват всех ошибок
@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logging.exception("Unhandled exception:")
        return PlainTextResponse("Internal error:\n" + str(e), status_code=500)

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

    if "question_order" not in request.session:
        order = list(range(len(questions)))
        random.shuffle(order)
        request.session["question_order"] = order
        request.session["game_index"] = 0
        request.session["score"] = 0

    order = request.session["question_order"]
    idx = request.session["game_index"]

    if idx >= len(order):
        return RedirectResponse("/result", status_code=303)

    q_idx = order[idx]
    current = questions[q_idx]

    return templates.TemplateResponse("game.html", {
        "request": request,
        "question_text": current["question"],
        "answers": current["options"],
        "hint_text": "Подсказка: подумайте логически :)"
    })


#Обработка ответа
@app.post("/submit")
async def submit_answer(request: Request, selected_answer: str = Form(...)):
    questions = read_questions("questions.txt")
    idx = request.session.get("game_index", 0)
    current = questions[idx]

    correct_letter = current["correct"].split(")")[0].strip().lower()

    if selected_answer.lower() == correct_letter:
        request.session["score"] += 1

    request.session["game_index"] += 1
    return RedirectResponse("/game", status_code=303)
#Пропуск вопроса
@app.post("/skip")
def skip_question(request: Request):
    request.session["game_index"] = request.session.get("game_index", 0) + 1
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

#Перезапуск игры
@app.get("/play_again")
def play_again(request: Request):
    request.session.pop("question_order", None)
    request.session["game_index"] = 0
    request.session["score"] = 0
    return RedirectResponse("/game", status_code=303)


# Выход из системы
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)