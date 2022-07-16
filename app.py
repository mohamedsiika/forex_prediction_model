from flask import Flask, request, jsonify
import pandas as pd
from model_retrain import Model_Retrain
from datetime import datetime
from Predict import Predict

app = Flask(__name__)


@app.route('/')
def default():
    return 'Connected'


@app.route("/getAction", methods=["POST"])
def post():
    pred = Predict()
    post_data = request.get_json()
    df = pd.DataFrame.from_dict(post_data['df'], orient='columns')
    action = pred.action(df)
    action = action.astype(str)
    return jsonify({
        "Response": {
            "Action": action
        }
    })


@app.route("/dataUpdate")
def check_updates():
    mr = Model_Retrain()
    mr.check_update()
    if mr.update_is_needed():
        return jsonify({
            "Response": {
                "Dict": mr.updatingDataNeeded
            }})

    else:
        return jsonify({
            "Response": {
                "Dict": "False"
            }
        })


@app.route("/updateModels", methods=["POST"])
def update_models():
    now = datetime.now()
    if now.hour != 00:
        return jsonify({
            "Response": "No Updated data"
        })
    mr = Model_Retrain()
    post_data = request.get_json()
    df = pd.DataFrame.from_dict(post_data['df'], orient='columns')
    mr.update_models(df)
    return jsonify({
        "Response": "Models Updated"
    })


if __name__ == '__main__':
    app.run(debug=True)
