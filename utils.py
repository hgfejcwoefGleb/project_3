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

        questions.append({
            "question": question_text,
            "options": options,
            "correct": correct_line[0].split(":", 1)[1].strip()
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
