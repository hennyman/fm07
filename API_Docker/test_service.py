from flask import Flask, request, abort, jsonify, render_template

app = Flask(__name__)

status = True

@app.route("/", methods=['GET'])
def hello():
    return "Hello World"


@app.route('/UI')
def ui():
    """ Render the HTML UI."""
    return render_template('example.html')


@app.route('/status', methods=['GET'])
def get_status():
    global status
    if not status:
        abort(500, "Status set to False")
    else:
        return 'OK'

    
@app.route('/predict', methods=['POST'])
def make_prediction():
    
    global status

    if not status:
        abort(500, "Status set to False")

    return "Prediction: "


@app.route('/predict_json', methods=['POST'])
def make_prediction_json():
    # curl -X POST http://<ip>:<port>/predict_json -d "{\"x\": 10}" --header "Content-Type: application/json"
    # or
    # curl -X POST http://<ip>:<port>/predict_json -d  @"[full filepath]" --header "Content-Type: application/json"

    #     input (json):
    #     {
    #         "x": 10
    #     }
    #     output (json):
    #     {
    #         "y": 20
    #     }

    global status

    if not status:
        abort(500, "Status set to False")

    if not request.json:
        abort(400, "Request did not contain JSON")

    json = request.get_json()
    try:

        x = json['x']
        
        result = {
            'y': 2 * x
        }

        return jsonify(result)

    except Exception:
        abort(400, "Unexpected JSON format")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
