from data import db_session
from data.__all_models import *

import argparse
import re
from pprint import pprint
import os
import sqlalchemy as sa


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="parse file with test")
    parser.add_argument("file", help="path to file with test")
    parser.add_argument("-s", "--save", help="save test", action="store_true")
    parser.add_argument("-n", "--name", help="test name, required for saving")
    parser.add_argument("-d", "--desc", help="test description, empty by default")
    parser.add_argument("-a", "--author", help="test author id")
    parser.add_argument("-q", "--quiet", help="do not print parsed", action="store_true")

    args = parser.parse_args()

    fn = args.file
    try:
        with open(fn, 'rt') as f:
            test = f.read().strip()
    except FileNotFoundError:
        print("File not found")
        exit(1)

    # delete comments
    questions = ''.join(re.split('//.*\n', test))
    # and blank lines
    questions = ''.join(re.split('\n', questions))
    # split questions
    questions = questions.split('::')

    # let's get that party started
    test_questions = []
    for q in questions:
        q = q.strip()
        if not q:
            continue
        # get the question title
        q_text = q.split("{")[0].strip()
        # get part of the string that contains options
        options = re.search('{.*}', q).group()[1:-1]
        # get index of the correct answer
        ind_correct = re.findall('[=~]', options).index('=')
        # get all answers
        answers = list(a.strip() for a in re.split('[=~]', options)[1:])
        # append question object to the test
        test_questions.append({
            "text": q_text,
            "answers": [
                {"text": answers[i],
                 "is_correct": i == ind_correct}
                for i in range(len(answers))]
        })

    if not args.quiet:
        pprint(test_questions)

    if not args.save:
        exit(0)

    a = input('save test? y/n: ').lower().strip()
    while a not in ['y', 'n']:
        a = input('save test? y/n: ').lower().strip()

    if a == 'y':
        # check test name
        if not args.name:
            print("Test name must be provided")
            exit(1)
        # connect to db
        try:
            db_session.global_init(os.path.join(os.getcwd(), "db", "tests.sqlite"))
        except sa.exc.OperationalError:
            db_session.global_init("/home/ilyav/testing-system/db/tests.sqlite")
        db = db_session.create_session()
        # check if author id is given and ask if not
        if not args.author:
            # get all users
            authors = db.query(User).filter(User.type_id != 3).all()
            # save their ids
            ids = list(str(user.id) for user in authors)
            # ask
            print(*list(f"{user.nickname}\t{user.id}" for user in authors), sep="\n")
            author_id = input("Author id: ")
            while author_id not in ids:
                author_id = input("Author id: ")
        else:
            author_id = args.author
        # create test object
        test = Test()
        test.name = args.name
        test.description = args.desc
        test.creator_id = author_id
        db.add(test)
        # create questions objects
        for q in test_questions:
            question = Question()
            question.text = q["text"]
            question.test = test
            db.add(question)
            # create answers objects
            for a in q["answers"]:
                answer = Answer()
                answer.text = a["text"]
                answer.is_correct = a["is_correct"]
                answer.question = question
                db.add(answer)
        # commit changes
        db.commit()
        print("test saved")
        # you are great!
