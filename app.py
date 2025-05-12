from flask import Flask, request, render_template_string
import random

app = Flask(__name__)

# Главная страница с игрой
@app.route("/", methods=["GET", "POST"])
def guess_number():
    secret_number = random.randint(1, 100)
    message = ""
    attempts_left = 10

    if request.method == "POST":
        guess = int(request.form["guess"])
        secret = int(request.form["secret"])
        attempts = int(request.form["attempts"]) - 1

        if guess == secret:
            message = f"🎉 Победа! Это число {secret}!"
        elif attempts == 0:
            message = f"💥 Проигрыш! Число было: {secret}."
        elif guess < secret:
            message = "⬆️ Больше!"
        else:
            message = "⬇️ Меньше!"

        return render_template_string(TEMPLATE, 
                                   message=message, 
                                   secret=secret, 
                                   attempts=attempts)

    return render_template_string(TEMPLATE, 
                               message="Угадай число от 1 до 100!", 
                               secret=secret_number, 
                               attempts=attempts_left)

# HTML-шаблон (простой интерфейс)
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Угадай число</title>
</head>
<body>
    <h1>{{ message }}</h1>
    <p>Попыток осталось: {{ attempts }}</p>
    <form method="POST">
        <input type="number" name="guess" min="1" max="100" required>
        <input type="hidden" name="secret" value="{{ secret }}">
        <input type="hidden" name="attempts" value="{{ attempts }}">
        <button type="submit">Проверить</button>
    </form>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))