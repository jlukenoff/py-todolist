from flask import Blueprint, Flask, render_template, session, request, redirect
from sqlalchemy import select, desc, asc

from database import db, DATABASE_URI
from models.todo import Todo

root_blueprint = Blueprint("root", __name__)

# http://localhost:5000/todos?orderBy=completed&desc=1
@root_blueprint.route("/")
def index():
    # check if session has order_by param
    print(session)
    if 'orderBy' in session:
        # query with order by
        if 'desc' in session and session['desc']:
            todos = db.session.execute(select(Todo).order_by(desc(session['orderBy']))).scalars()
        else:
            todos = db.session.execute(select(Todo).order_by(asc(session['orderBy']))).scalars()
    else:
        todos = db.session.execute(select(Todo)).scalars()
    return render_template("index.html", todos=todos)


@root_blueprint.post("/add")
def add():
    title = request.form.get("title")

    new_todo = Todo(title=title)
    db.session.add(new_todo)
    db.session.commit()

    return redirect("/")


@root_blueprint.post("/complete/<int:todo_id>")
def complete(todo_id):
    statement = select(Todo).where(Todo.id == todo_id)
    todo = db.session.execute(statement).scalar_one()
    todo.completed = True
    db.session.commit()

    return redirect("/")


@root_blueprint.post("/delete/<int:todo_id>")
def delete(todo_id):
    statement = select(Todo).where(Todo.id == todo_id)
    todo = db.session.execute(statement).scalar_one()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")

'''
feature we will add is the ability for the user to change the order of todos
1.  Drop down allowing user to select what to order by
2. API handler that takes in order_by and returns tasks by specified order
/todos/?order_by="completed | title"
'''
@root_blueprint.get("/todos")
def order_by():
    order_by = request.args.get('orderBy')
    descending_order = request.args.get('desc')
    session['orderBy'] = order_by
    session['desc'] = True if descending_order == '1' else False
    return redirect("/")


def initialize_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.secret_key = 'TEST'

    db.init_app(app)

    app.register_blueprint(root_blueprint)

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    initialize_app().run(debug=True)
