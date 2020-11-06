import json
from flask import request, Response, make_response, jsonify, redirect, url_for, render_template, flash, session
from .models.reporting import Reporting
from backend import app
from .models.monitor import Monitor


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')


@app.route("/monitor")
def monitor():
    return render_template("monitor.html")


@app.route("/start", methods=["POST"])
def monitoring_start():
    # TODO: エラーハンドリング
    event_id = request.json['eventId']

    monitor = Monitor()
    message = monitor.run(event_id)

    return Response(response=json.dumps({'message': message}))


@app.route("/record", methods=["POST"])
def record_stop_event():
    stopped_time = request.json['stoppedTime']
    stop_reason = request.json['stopReason']
    stop_factor = request.json['stopFactor']

    event_id = request.json['eventId']

    monitor = Monitor()
    monitor.record_stop_event(event_id, stopped_time, stop_reason, stop_factor)

    message = "停止中"

    return Response(response=json.dumps({'message': message}))


@app.route("/report")
def report():
    repData = Reporting().getMetaData()
    return jsonify(repData)
