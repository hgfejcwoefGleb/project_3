def read_questions(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

def generate_question_html(questions):
    html_items = []
    for idx, question in enumerate(questions, start=1):
        item = f"""
        <div class="question-item">
            <div class="question-text">
                <strong>Вопрос #{idx}:</strong> {question}
            </div>
            <div class="question-actions">
                <i class="fas fa-edit action-icon" title="Редактировать"></i>
                <i class="fas fa-trash action-icon" title="Удалить"></i>
            </div>
        </div>
        """
        html_items.append(item)
    return "\n".join(html_items)