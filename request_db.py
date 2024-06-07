def check_on_admin(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT tg_id FROM" + '"master"' + f"WHERE tg_id = '{user_id}';")
    result = cursor.fetchall()
    cursor.close()
    if len(result) == 0:
        return False
    else:
        return True


def get_start_message(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM" + '"main_message"' + f"WHERE tg_id = '{user_id}';")
    result = cursor.fetchall()
    cursor.close()
    text = result[0][0]
    return text


def set_new_main_text(conn, user_id, text):
    cursor = conn.cursor()
    cursor.execute('UPDATE "main_message" SET text =' + f"('{text}') WHERE tg_id = '{user_id}';")
    cursor.close()


def get_info_service_message(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM" + '"info_service_message"' + f"WHERE tg_id = '{user_id}';")
    result = cursor.fetchall()
    cursor.close()
    text = result[0][0]
    return text


def set_new_info_service_text(conn, user_id, text):
    cursor = conn.cursor()
    cursor.execute('UPDATE "info_service_message" SET text =' + f"('{text}') WHERE tg_id = '{user_id}';")
    cursor.close()


def get_master_service(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT name_service FROM" + '"services_master"' + f"WHERE tg_id = '{user_id}';")
    result = cursor.fetchall()
    cursor.close()
    services = result

    return services


def delete_service_master(conn, name_service, user_id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM" + '"services_master"' + f"WHERE tg_id = '{user_id}'"
                       f" AND name_service = '{name_service}';")
        cursor.close()
    except:
        return False

    return True


def append_service(conn, name_service, user_id):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO "services_master" (name_service, tg_id)'
                   'VALUES' + f"('{name_service}', '{user_id}');")
    cursor.close()
    return True


def get_current_informathion_message(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM" + '"current_informathion_message"' + f"WHERE tg_id = '{user_id}';")
    result = cursor.fetchall()
    cursor.close()
    text = result[0][0]
    return text


def set_new_current_informathion_text(conn, user_id, text):
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE "current_informathion_message" SET text =' + f"('{text}') WHERE tg_id = '{user_id}';")
        cursor.close()
    except:
        return False
    return True


def set_social_link(conn, name_social, link, user_id):

    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE "social_link_master" SET link =' + f"('{link}') WHERE tg_id = '{user_id}'"
                                                                  f" AND name_social = '{name_social}';")
        cursor.close()
    except:
        return False
    return True


def get_social_link(conn, name_social, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM" + '"social_link_master"' + f"WHERE tg_id = '{user_id}'"
                                                                 f"AND name_social = '{name_social}';")
    result = cursor.fetchall()
    cursor.close()
    link = result[0][0]
    return link


def get_design_test(conn, user_id):
    try:
        query_set = []

        questions = get_questions(conn, user_id)
        for question in questions:
            question_and_answer = [question[0]]
            for answer in get_answers(conn, question[1]):
                for variant in answer:
                    question_and_answer.append(variant)
            query_set.append(question_and_answer)
        return query_set
    except:
        return False


def get_questions(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT text_question, id_question  FROM" + '"master_test_questions"' + f"WHERE tg_id = '{user_id}' ;")
    questions = cursor.fetchall()
    cursor.close()
    return questions


def get_answers(conn, question_id):
    cursor = conn.cursor()
    cursor.execute("SELECT first_answer, second_answer, third_answer, fourth_answer FROM " + '"master_test_answer"' +
                   f"WHERE id_question = '{question_id}' ;")
    answers = cursor.fetchall()
    cursor.close()
    return answers


def truncate_old_test(conn, user_id):
    try:
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM "master_test_questions" CASCADE ' + f"WHERE tg_id = '{user_id}' ;")
        cursor.close()
    except:
        return False
    return True


def create_questions_with_answers(conn, question, answers, user_id):
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO "master_test_questions" (text_question, tg_id)'
                       'VALUES' + f"('{question}', '{user_id}') RETURNING id_question;")
        id_question = cursor.fetchall()[0][0]
        cursor.close()
        add_question(conn, answers, id_question)
    except:
        return False
    return True


def add_question(conn, answers, id_question):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO "master_test_answer" (first_answer, second_answer, third_answer,'
                   ' fourth_answer, id_question)'
                   'VALUES' + f"('{answers[0]}', '{answers[1]}' , '{answers[2]}', '{answers[3]}', {id_question}) ;")
    cursor.close()