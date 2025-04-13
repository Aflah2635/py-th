def edit_question(questions, question_id, new_text, is_admin=False):
    """
    Edit a question in the questions list
    :param questions: List of questions
    :param question_id: ID of question to edit
    :param new_text: New question text
    :param is_admin: If True, allows editing any question
    :return: Updated questions list
    """
    if is_admin:
        # Admin can edit any question
        for question in questions:
            if question['id'] == question_id:
                question['text'] = new_text
                question['last_edited_by'] = 'admin'
                break
    else:
        # Non-admin can only edit their own questions
        for question in questions:
            if question['id'] == question_id and question['author'] == 'current_user':
                question['text'] = new_text
                break
    return questions

# Example usage:
questions = [
    {'id': 1, 'text': 'What is Python?', 'author': 'user1'},
    {'id': 2, 'text': 'How to use lists?', 'author': 'user2'}
]

# Admin edit
questions = edit_question(questions, 1, 'What is Python programming?', is_admin=True)

# Regular user edit
questions = edit_question(questions, 2, 'How to use Python lists?') 