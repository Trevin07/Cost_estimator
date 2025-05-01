from flask import Flask, render_template, request
import pandas as pd
import joblib
import os

app = Flask(__name__)

state_encoder = joblib.load(os.path.join("state_encoder.pkl"))
cost_lookup = pd.read_csv(os.path.join("cost_lookup.csv"))

@app.route("/", methods=["GET"])
def home():
    states = sorted(state_encoder.classes_)
    return render_template("index.html", states=states, prediction=None,
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
    return render_template("index.html",
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
