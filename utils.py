import re

def read_questions(file_path: str) -> list:
    """Чтение вопросов из файла нового формата"""
    questions = []
    current_question = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            # Пропускаем пустые строки
            if not line:
                continue

            # Проверяем, начинается ли строка с номера вопроса: "1.", "2." и т.д.
            question_match = re.match(r'^(\d+)\.\s*(.+)$', line)
            if question_match:
                if current_question:
                    questions.append(current_question)

                # Начинаем новый вопрос
                current_question = {
                    "text": question_match.group(2),
                    "options": [],
                    "correct_answer": None
                }

            # Варианты ответа: a), b), c)
            elif line.startswith(("a)", "b)", "c)")):
                if current_question is not None:
                    current_question["options"].append(line)

            # Правильный ответ
            elif line.startswith("Правильный ответ:"):
                if current_question is not None:
                    current_question["correct_answer"] = line.split(": ", 1)[1]

    # Добавляем последний вопрос
    if current_question:
        questions.append(current_question)

    return questions

def read_questions_(filename):
    questions = []
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.read().split('\n\n')  # Разделяем по пустым строкам
        
    for block in lines:
        if not block.strip():
            continue
            
        parts = block.split('\n')
        if len(parts) < 4:  # Как минимум: вопрос, 2 варианта, правильный ответ
            continue
            
        question = {
            "text": parts[0].strip(),
            "options": [opt.strip() for opt in parts[1:-1] if opt.strip()],
            "correct_answer": parts[-1].replace("Правильный ответ:", "").strip()
        }
        questions.append(question)
    print(questions)
    return questions

def generate_question_html(questions: list) -> str:
    """Генерация HTML для списка вопросов"""
    html = []
    for i, question in enumerate(questions, 1):
        html.append(f"""
        <div class="question-item" data-id="{i}">
            <div class="question-text">
                <strong>{question['text']}</strong>
                <div class="question-answer">{question['correct_answer']}</div>
            </div>
            <div class="question-actions">
                <i class="fas fa-edit action-icon" title="Редактировать"></i>
                <i class="fas fa-trash action-icon" title="Удалить"></i>
            </div>
        </div>
        """)
    return "\n".join(html)

def save_question_to_file(question: str, options: list, correct_answer: str, filename: str = "tasks.txt"):
    """
    Сохраняет вопрос и варианты ответов в файл в заданном формате.
    """
    question_number = 1
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        question_number = content.count("Правильный ответ:") + 1

    # Формируем блок вопроса
    question_block = f"{question_number}. {question}\n"
    # Назначаем буквы вариантам
    for idx, option in enumerate(options):
        question_block += f"{chr(97 + idx)}) {option}\n"
        last_let = chr(97 + idx)
    question_block += f"Правильный ответ: {last_let}) {correct_answer}\n\n"
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

