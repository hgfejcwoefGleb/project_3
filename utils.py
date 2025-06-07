def read_questions(filename):
    questions = []
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_question = ""
    options = []
    correct_answer = ""

    for line in lines:
        text = line.strip()
        if not text:
            continue

        if text.lower().startswith("правильный ответ:"):
            correct_answer = text.split(":", 1)[1].strip()
            questions.append({
                "question": current_question.strip(),
                "options": options,
                "correct": correct_answer
            })
            current_question = ""
            options = []
            correct_answer = ""
        elif any(text.lower().startswith(prefix) for prefix in ["a)", "б)", "в)", "а)", "b)", "c)"]):
            options.append(text.split(")", 1)[1].strip())
        else:
            current_question += " " + text if current_question else text

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
