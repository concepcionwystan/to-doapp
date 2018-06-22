import os
import json
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import flash


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "taskdatabase.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.secret_key = 'my_secret_key'
db = SQLAlchemy(app)

class Task(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)

    def __repr__(self):
        return "[Title: {}]".format(self.title)

@app.route("/", methods=["GET", "POST"])
def home():
    error = None
    if request.form:
        try:
            task = Task(title=request.form.get("title"))
            db.session.add(task)
            db.session.commit()
            error = None
        except IntegrityError:
            db.session.rollback()
            error = "Task already present"
    tasks = Task.query.all()
    taskList = []
    for item in tasks:
        taskList.append({'title':item.title,'isActive':False})
    taskjson = json.dumps(taskList)

    return render_template("home.html", tasks=taskjson,error=error)
    # except Exception as e:
    #     error = "Invalid task"
    #     return redirect("/")

@app.route("/update", methods=["POST"])
def update():
    try:
        newtitle = request.form.get("newtitle")
        oldtitle = request.form.get("oldtitle")
        task = Task.query.filter_by(title=oldtitle).first()
        task.title = newtitle
        db.session.commit()
    except Exception as e:
        error = "Task already present"
        flash('Task already present')
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    task = Task.query.filter_by(title=title).first()
    db.session.delete(task)
    db.session.commit()
    return redirect("/")

@app.route("/search", methods=["GET"])
def search():
    search = request.args.get("search")
    task = Task.query.filter_by(title=search).first()
    taskList = []
    if task != None:
        taskList.append({'title':task.title,'isActive':False})
        taskjson=json.dumps(taskList)
    else:
        taskjson = None
    return render_template("search.html",task=taskjson)

if __name__ == "__main__":
    app.run(debug=True)