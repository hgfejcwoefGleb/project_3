from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import random
from typing import Optional
from starlette.middleware.sessions import SessionMiddleware
import secrets

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
    return templates.TemplateResponse("login_choice.html", {"request": request})


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
async def handle_admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = USERS.get(username)
    if not user or user["password"] != password:
        return templates.TemplateResponse("admin_login.html",
                                          {"request": request, "error": "Неверные учетные данные!"})

    request.session["user"] = {"username": username, "role": user["role"]}
    return RedirectResponse(url="/game", status_code=303)

# Страница для входа как гость
@app.get("/guest", response_class=HTMLResponse)
async def guest(request: Request):
    return templates.TemplateResponse("guest.html", {"request": request})

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