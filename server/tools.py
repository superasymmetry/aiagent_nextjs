from langgraph.types import Command, interrupt
import langgraph.graph as lg
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import langgraph.graph as lg
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, TypedDict, Any, Dict, List
from langgraph.graph import StateGraph
from langgraph.channels.any_value import AnyValue
import time
import datetime
from types import new_class
import ast
import json
import re
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import operator
import win32api
import win32con

def update_state(state, node_id, content):
    state[node_id] = {"content": content}
    return state

State = Dict[str, Any]

class MyState(State):
    state: Annotated[list[str], operator.add]

load_dotenv()  # Load .env variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyB72U5x4IDzKYELDbIosdVL-ntSfe-wr-k"
GOOGLE_CX = os.getenv("GOOGLE_CX") or "067c547b9424e4810"

#Search and scrape functions
def google_search(query):
    api_key = "AIzaSyB72U5x4IDzKYELDbIosdVL-ntSfe-wr-k"
    cx = '067c547b9424e4810'
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}&fields=items(link)'
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    results = response.json()
    print(results)
    if 'items' in results:
        return results
    else:
        return None

def scrape_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    session = requests.Session()
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    content = ' '.join([para.get_text() for para in paragraphs])
    return content

def search_and_scrape(query):
    search_results = google_search(query)
    links = [item['link'] for item in search_results.get('items', [])]
    scraped_contents = []
    '''
    for link in links:
        content = scrape_content(link)
        scraped_contents.append(content)
    '''
    scraped_contents.append(scrape_content(links[0]))
    return scraped_contents

# --- Graph Input Type ---
class GraphData(TypedDict):
    nodeTexts: List[Dict[str, str]]
    edges: List[Dict[str, str]]

# --- Node Behavior Factory ---
def make_node_fn(node_id: str, text: str):
    if ("{{timing:elapsed}}" in text):
        seconds = int(re.findall(r"{{timing:elapsed}}(\d+)", text)[0])
        def timing_node(state):
            result = f"[{node_id}] Sleeping for {seconds} seconds..."
            time.sleep(seconds)
            print(f"[{node_id}] Woke up, passing state forward.")
            state = update_state(state, node_id, result)
            return state
        return timing_node

    elif ("{{timing:set}}" in text):
        dt_str = text.split("}}", 1)[1].strip()
        dt = datetime.datetime.fromisoformat(dt_str)
        def timing_node(state: State):
            now = datetime.datetime.now()
            wait_seconds = (dt - now).total_seconds()
            if wait_seconds > 0:
                result = f"[{node_id}] Waiting until {dt} ({int(wait_seconds)}s)..."
                time.sleep(wait_seconds)
            else:
                result = f"[{node_id}] Time already passed, continuing immediately."
            state = update_state(state, node_id, result)
            return state
        return timing_node

    elif ("{{Researcher}}" in text):
        def browse_node(state : State):
            # input_val = next(iter(state.values()), None)
            input_val = text.replace("{{Researcher}}", "").strip()
            if input_val is None:
                print(f"[{node_id}] No valid input found, skipping browse.")
                return {node_id: {"content": "No valid input provided."}}
            query = input_val if isinstance(input_val, str) else input_val.get("content", "")
            result = search_and_scrape(query)
            state = update_state(state, node_id, result)
            return state
        return browse_node

    elif ("{{Human-in-the-loop}}" in text):
        def human_node(state : State):
            input_val = text.replace("{{Human-in-the-loop}}", "").strip()
            print(f"[{node_id}] Human node activated with input: {input_val}")

            if input_val is None:
                print(f"[{node_id}] No valid input found, skipping human node.")
                return
            # Handle both string and dict input safely
            if isinstance(input_val, str):
                question = input_val
            elif isinstance(input_val, dict):
                question = input_val.get("content", "")
            else:
                question = str(input_val)

            # answer = input(" " + question)
            answer = input({"prompt": question})

            state = update_state(state, node_id, {"humanquestion": question, "answer": answer})
            return state
        return human_node
    
    elif "{{Human-approval}}" in text:
        def human_approval(state: State):
        #  -> Command[Literal["some_node", "another_node"]]:
            # is_approved = interrupt(
            #     {
            #         "question": "Is this correct?",
            #         # Surface the output that should be
            #         # reviewed and approved by the human.
            #         "llm_output": state["llm_output"]
            #     }
            # )

            # if is_approved:
            #     return Command(goto="some_node")
            # else:
            #     return Command(goto="another_node")
            result = win32api.MessageBox(
                0,
                'Do you want to continue?',
                'Confirmation',
                win32con.MB_YESNO | win32con.MB_SYSTEMMODAL
            )

        
            # Handle the result
            if result == win32con.IDYES:
                state = update_state(state, node_id, result)
            else:
                state = update_state(state, node_id, result)
            return state
        return human_approval
    
    elif "{{computer}}" in text:
        def computer_node(state : State):
            input_val = text.replace("{{computer}}", "").strip()
            print(f"[{node_id}] Computer node activated with input: {input_val}")

            if input_val is None:
                print(f"[{node_id}] No valid input found, skipping computer node.")
                return
            # Handle both string and dict input safely
            if isinstance(input_val, str):
                question = input_val
            elif isinstance(input_val, dict):
                question = input_val.get("content", "")
            else:
                question = str(input_val)

            answer = search_and_scrape(question)

            state = update_state(state, node_id, {"question": question, "answer": answer})
            return state
        return computer_node
    
    else:
        def default_node(state : State):
            # print(f"[{node_id}] Passing through.")
            result = f"[{node_id}] {text} passing through."
            state[node_id] = {"content": result}
            return state
        return default_node

# --- Graph Builder ---
def create_langgraph(data: GraphData):
    node_ids = [n["id"] for n in data["nodeTexts"]]
    node_text_map = {n["id"]: n.get("text", "") for n in data["nodeTexts"]}
    GraphState = Dict[str, Any]

    builder = StateGraph(GraphState)

    for node_id in node_ids:
        fn = make_node_fn(node_id, node_text_map[node_id])
        builder.add_node(node_id, fn)

    edges_by_source = {}
    for edge in data["edges"]:
        source = edge["source"]
        target = edge["target"]
        edges_by_source.setdefault(source, []).append(target)

    for node_id in node_ids:
        next_nodes = edges_by_source.get(node_id, [])
        if not next_nodes:
            builder.add_edge(node_id, END)
        elif len(next_nodes) == 1:
            builder.add_edge(node_id, next_nodes[0])
        else:
            def router(state, *, options=next_nodes):
                return options
            builder.add_conditional_edges(node_id, router)

    entry = node_ids[0]
    builder.set_entry_point(entry)
    return builder.compile()

def to_double_quoted_json(single_quoted: str, *, indent: int = None) -> str:
    obj: Any = ast.literal_eval(single_quoted)
    return json.dumps(obj, indent=indent)

def parse_timing_info(text):
    if ("{{timing:set}}" in text):
        target_time = text[len("{{timing:set}}"):].strip()
        return ("set", target_time)
    elif ("{{timing:elapsed}}" in text):
        seconds = int(text[len("{{timing:elapsed}}"):].strip())
        return ("elapsed", seconds)
    return None

if __name__ == "__main__":

    y = {
        "nodeTexts": [
            {"id": "main", "text": "Start Node"},
            {"id": "timed1", "text": "{{timing:set}}2025-04-19 10:50"},
            {"id": "next", "text": "{{Researcher}} what is ai?"},
        ],
        "edges": [
            {"id": "edge1", "source": "main", "target": "timed1", "type": "buttonedge"},
            {"id": "edge2", "source": "timed1", "target": "next", "type": "buttonedge"},
        ]
    }
    print(y)
    g=create_langgraph(y)
    print(g.invoke({"state": "Start"}))
    last_state = None
    for event in g.stream({"state": "Start"}):
        last_key = list(event.keys())[-1]
        last_value = event[last_key]

        try:
            print(f"Last executed node: {last_key} | Output: {last_value['content']}")
        except KeyError:
            print(f"Last executed node: {last_key} | Output: {last_value[last_key]['content']}")

