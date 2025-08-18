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

class GraphState(TypedDict):
    messages: Annotated[List[str], operator.add]
    data: Dict[str, Any]

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
            int(f"[{node_id}] Woke up, passing state forward.")
            state = update_state(state, node_id, result)
            if("{{Human-approval}}" in text):
                is_approved = interrupt(
                    {
                        "question": "continue?",
                        "state": state
                    }
                )

                if is_approved:
                    return state
                else:
                    exit()

            return statetime.sleep(seconds)
            pr
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
            if("{{Human-approval}}" in text):
                is_approved = interrupt(
                    {
                        "question": "continue?",
                        "state": state
                    }
                )

                if is_approved:
                    return state
                else:
                    exit()
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
            if("{{Human-approval}}" in text):
                is_approved = interrupt(
                    {
                        "question": "continue?",
                        "state": state
                    }
                )

                if is_approved:
                    return state
                else:
                    exit()
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
            if("{{Human-approval}}" in text):
                is_approved = interrupt(
                    {
                        "question": "continue?",
                        "state": state
                    }
                )

                if is_approved:
                    return state
                else:
                    exit()
            return state
        return human_node

    
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
            if("{{Human-approval}}" in text):
                is_approved = interrupt(
                    {
                        "question": "continue?",
                        "state": state
                    }
                )

                if is_approved:
                    return state
                else:
                    exit()
            return state
        return computer_node
    
    elif "{{Conditional}}" in text:
        def conditional_node(state: State):
            condition_text = text.replace("{{Conditional}}", "").strip()
            print(f"[{node_id}] Conditional node: {condition_text}")
            
            # Simple evaluation - check for "true" or "false" keywords
            result = "true" in condition_text.lower() or "sunday" in condition_text.lower()
            
            state = update_state(state, node_id, f"Condition evaluated to: {result}")
            # Store condition result for routing
            state[f"{node_id}_condition"] = result
            
            if("{{Human-approval}}" in text):
                is_approved = interrupt(
                    {
                        "question": "continue?",
                        "state": state
                    }
                )

                if is_approved:
                    return state
                else:
                    exit()
            return state
        return conditional_node
    
    else:
        def default_node(state : State):
            # print(f"[{node_id}] Passing through.")
            result = f"[{node_id}] {text} passing through."
            state[node_id] = {"content": result}
            if("{{Human-approval}}" in text):
                is_approved = interrupt(
                    {
                        "question": "continue?",
                        "state": state
                    }
                )

                if is_approved:
                    return state
                else:
                    exit()
            return state
        return default_node

# --- Graph Builder ---
def create_langgraph(data: GraphData):
    node_ids = [n["id"] for n in data["nodeTexts"]]
    node_text_map = {n["id"]: n.get("text", "") for n in data["nodeTexts"]}

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
        node_text = node_text_map[node_id]
        
        if not next_nodes:
            builder.add_edge(node_id, END)
        elif len(next_nodes) == 1:
            builder.add_edge(node_id, next_nodes[0])
        elif len(next_nodes) == 2 and "{{Conditional}}" in node_text:
            # Conditional routing: first edge is TRUE, second is FALSE
            true_target = next_nodes[0]
            false_target = next_nodes[1]
            
            def make_conditional_router(source_node, true_node, false_node):
                def conditional_router(state):
                    condition_result = state.get(f"{source_node}_condition", True)
                    return true_node if condition_result else false_node
                return conditional_router
            
            router = make_conditional_router(node_id, true_target, false_target)
            builder.add_conditional_edges(node_id, router, [true_target, false_target])
        else:
            # Multiple edges - return first one for simplicity
            def make_simple_router(options):
                def simple_router(state):
                    return options[0]
                return simple_router
            
            router = make_simple_router(next_nodes)
            builder.add_conditional_edges(node_id, router, next_nodes)

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

    # Simple conditional example
    y = {
        "nodeTexts": [
            {"id": "main", "text": "Start Node"},
            {"id": "cond", "text": "{{Conditional}} false"},
            {"id": "true_path", "text": "Taking TRUE path"},
            {"id": "false_path", "text": "Taking FALSE path"}
        ],
        "edges": [
            {"id": "edge1", "source": "main", "target": "cond", "type": "buttonedge"},
            {"id": "edge_true", "source": "cond", "target": "true_path", "type": "buttonedge"},
            {"id": "edge_false", "source": "cond", "target": "false_path", "type": "buttonedge"}
        ]
    }
    
    print("Graph structure:")
    print(y)
    g = create_langgraph(y)
    
    # Initialize state properly for GraphState
    initial_state = {"messages": [], "data": {}}
    
    print("\nRunning graph:")
    result = g.invoke(initial_state)
    print("Final result:", result)
    
    print("\nStream execution:")
    for event in g.stream(initial_state):
        print("Event:", event)
