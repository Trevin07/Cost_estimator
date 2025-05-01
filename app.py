import os
from flask import Flask, render_template_string, request, send_from_directory
import pandas as pd
import joblib

app = Flask(__name__, template_folder='.')  # templates in current folder

# Load encoder and cost data
state_encoder = joblib.load("state_encoder.pkl")
cost_lookup = pd.read_csv("cost_lookup.csv")

# Serve the image from the main folder
@app.route('/money.jpg')
def image():
    return send_from_directory('.', 'money.jpg')

@app.route("/", methods=["GET"])
def home():
    states = sorted(state_encoder.classes_)
    with open("index.html") as f:
        html_template = f.read()

    return render_template_string(html_template, states=states, prediction=None,
                                  input_state=None, input_is_metro=None,
                                  input_parent_count=None, input_child_count=None,
                                  input_needs_childcare=None)

@app.route("/predict", methods=["POST"])
def predict():
    state = request.form["state"]
    is_metro = int(request.form["is_metro"])
    parent_count = int(request.form["parent_count"])
    child_count = int(request.form["child_count"])
    needs_childcare = int(request.form["needs_childcare"])

    state_encoded = state_encoder.transform([state])[0]

    row = cost_lookup[
        (cost_lookup["state"] == state_encoded) &
        (cost_lookup["isMetro"] == is_metro) &
        (cost_lookup["parent_count"] == parent_count) &
        (cost_lookup["child_count"] == child_count) &
        (cost_lookup["needs_childcare"] == needs_childcare)
    ]

    if not row.empty:
        prediction = round(float(row["total_cost"].values[0]), 2)
        income = round(float(row["median_family_income"].values[0]), 2)
        gap = round(prediction - income, 2)
    else:
        prediction = "Not Available"
        gap = "-"

    states = sorted(state_encoder.classes_)

    with open("index.html") as f:
        html_template = f.read()

    return render_template_string(html_template,
                                  states=states,
                                  prediction=prediction,
                                  gap=gap,
                                  input_state=state,
                                  input_is_metro=str(is_metro),
                                  input_parent_count=str(parent_count),
                                  input_child_count=str(child_count),
                                  input_needs_childcare=str(needs_childcare))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
