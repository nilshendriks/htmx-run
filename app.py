import os
import time

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, flash, send_file
from runs_model import Run, Archiver

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env
load_dotenv()

# Set secret key
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Load runs from database
Run.load_db()

# ========================================================
# Flask App
# ========================================================

@app.route('/')
def index():
    return redirect("/runs")


@app.route('/runs')
def runs():
    search = request.args.get("q")
    if search is not None:
        runs_set = Run.search(search)
    else:
        runs_set = Run.all()
    return render_template("index.html", runs=runs_set)


@app.route("/runs/new", methods=['GET'])
def runs_new_get():
    return render_template("new.html", run=Run())


@app.route("/runs/new", methods=['POST'])
def runs_new_post():
    run = Run(
        distance=request.form['distance'],
        duration=request.form['duration'],
        timestamp=request.form['timestamp']  # Ensure this includes the date and time
    )
    if run.save():
        flash("Created New Run!")
        return redirect("/runs")
    else:
        return render_template("new.html", run=run)


@app.route("/runs/<run_id>")
def runs_view(run_id):
    run = Run.find(run_id)
    return render_template("show.html", run=run)


@app.route("/runs/<run_id>/edit", methods=['GET'])
def runs_edit_get(run_id):
    run = Run.find(run_id)
    return render_template("edit.html", run=run)


@app.route("/runs/<run_id>/edit", methods=["POST"])
def runs_edit_post(run_id=0):
    run = Run.find(run_id)
    if run is not None:
        # Use the distance directly as a string
        distance = request.form['distance']

        # Use the duration directly as a string
        duration = request.form['duration']

        # Use the timestamp directly as a string
        timestamp = request.form['timestamp']

        # Update the run instance
        run.update(
            distance=distance,
            duration=duration,
            timestamp=timestamp
        )

        # Attempt to save the run
        if run.save():
            flash("Updated Run!")
            return redirect("/runs/" + str(run_id))
        else:
            return render_template("edit.html", run=run)
    else:
        flash("Run not found.")
        return redirect("/runs")


@app.route("/runs/<run_id>/delete", methods=["POST"])
def runs_delete(run_id=0):
    run = Run.find(run_id)
    if run is not None:
        run.delete()
        flash("Deleted Run!")
    else:
        flash("Run not found!")

    return redirect("/runs")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == '__main__':
    # app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.run(debug=True, host='0.0.0.0')
    # app.config['ENV'] = 'development'
    # app.run(debug=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')
