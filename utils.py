def read_questions(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    blocks = content.strip().split("\n\n")
    questions = []

    for block in blocks:
        lines = block.strip().splitlines()
        if not lines or len(lines) < 4:
            continue

        question_text = lines[0]
        options = [line for line in lines[1:] if line.lower().startswith(('a)', 'б)', 'в)', 'а)', 'b)', 'c)'))]
        correct_line = [line for line in lines if "правильный ответ" in line.lower()]
        if not correct_line or not options:
            continue

        correct = correct_line[0].split(":", 1)[1].strip()
        questions.append({
            "question": question_text,
            "options": options,
            "correct": correct
        })

    return questions


def generate_question_html(questions):
    html_items = []
    for idx, question in enumerate(questions, start=1):
        options_html = "<ul>" + "".join(f"<li>{opt}</li>" for opt in question["options"]) + "</ul>"
        item = f"""
        <div class="question-item">
            <div class="question-text">
                <strong>Вопрос #{idx}:</strong> {question["question"]}
                {options_html}
                <div><em>Правильный ответ:</em> {question["correct"]}</div>
            </div>
            <div class="question-actions">
                <i class="fas fa-edit action-icon" title="Редактировать"></i>
                <i class="fas fa-trash action-icon" title="Удалить"></i>
            </div>
        </div>
        """
        html_items.append(item)
    return "\n".join(html_items)


def save_question_to_file(question: str, options: list, correct_answer: str, filename: str = "tasks.txt"):
    """
    Сохраняет вопрос и варианты ответов в файл в заданном формате.
    """
    print(options)
    question_number = 1
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        question_number = content.count("Правильный ответ:") + 1

    # Формируем блок вопроса
    question_block = f"{question_number}. {question}\n"
    # Назначаем буквы вариантам
    for idx, option in enumerate(options):
        question_block += f"{chr(97 + idx)}) {option}\n"

    question_block += f"Правильный ответ: {correct_answer}\n\n"
    # Записываем в файл
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(question_block)

    return question_number

def read_ratings(file_path: str = "progress.txt"):
    """Чтение рейтинга из текстового файла (формат: Имя:Очки)"""
    ratings = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()  # Удаляем пробелы и переносы строк
                if not line or line.startswith('#'):  # Пропускаем пустые строки и комментарии
                    continue
                
                # Разделяем строку по разделителю (можно использовать ':', ';', ',' и т.д.)
                if ':' in line:
                    name, score = line.split(':', 1)  # Разделяем только по первому вхождению
                else:
                    continue  # Пропускаем строки без разделителя
                
                name = name.strip()
                try:
                    score = int(score.strip())
                    ratings.append({
                        "name": name,
                        "score": score
                    })
                except ValueError:
                    print(f"Ошибка преобразования очков в строке: {line}")
                    continue
                
    except FileNotFoundError:
        print(f"Файл {file_path} не найден")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
    
    # Сортируем по убыванию очков
    return sorted(ratings, key=lambda x: x["score"], reverse=True)

