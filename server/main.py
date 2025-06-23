from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask import session, redirect, url_for
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from extract import extractModel
from combined import combinedModel
import sqlite3
import time
from tools import create_langgraph, to_double_quoted_json


app = Flask(__name__)
cors = CORS(app, origins="*")

# @app.route('/api/graph', methods=['GET'])
# def users():
#     if "user" in session:
#         user = session["user"]
#         return user
#     else:
#         return redirect(url_for("views.signin"))

# @app.route('/api/graph', methods=['GET', 'POST'])
# def receive_graph():
#     data = request.get_json()
#     json.dumps(data)
    
#     print("Received graph data:", data)
#     def generate():
#         g=create_langgraph(data)
#         # Start streaming from the graph
#         for event in g.stream({"state": "Start"}):
#             last_key = list(event.keys())[-1]
#             last_value = event[last_key]

#             try:
#                 content = last_value['content']
#             except KeyError:
#                 content = last_value[last_key]['content']

#             display = f"Last executed node: {last_key} | Output: {content}\n"
#             print(display)
#             yield f"data: {display}\n\n"  # SSE format

#         yield "data: Export complete.\n\n"

#     return Response(generate(), mimetype='text/event-stream')


@app.route('/api/graph', methods=['POST'])
def receive_graph():
    data = request.get_json()
    print("Received graph data:", data)

    g = create_langgraph(data)  # Your graph builder

    def generate():
        for event in g.stream({"state": "Start"}):
            last_key = list(event.keys())[-1]
            last_value = event[last_key]
            try:
                content = last_value[last_key]['content']
            except (KeyError, TypeError):
                content = last_key['content']
            display = f"Last executed node: {last_key} | Output: {content}\n"
            yield f"data: {display}\n" 
            time.sleep(0.1)

        yield "event: end\ndata: Stream finished\n\n"

    return Response(generate(), mimetype='text/event-stream')



if __name__ == "__main__":
    conn = sqlite3.connect('agents.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS agents (id INTEGER, name TEXT, prompt TEXT)''')
    conn.commit()

    # combined_model = combinedModel()
    app.run(debug=True, port=8080)