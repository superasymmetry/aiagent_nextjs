import pinecone
import uiautomation as automation
import pyautogui
from groq import Groq
import os
import json
import base64

class AutomationAgent():
    def __init__(self):
        # for UIAutomation
        self.max_depth = 5
        self.root_control = automation.GetRootControl()
        # Use a dictionary comprehension to assign a separate list for each key.
        self.tree = {key: [] for key in [
            'WindowControl', 'PaneControl', 'DocumentControl', 'ButtonControl',
            'EditControl', 'CheckBoxControl', 'RadioButtonControl', 'ComboBoxControl',
            'ListControl', 'ListItemControl', 'MenuControl', 'TreeControl',
            'TabControl', 'SliderControl', 'CustomControl'
        ]}

        # for Groq client
        self.action_history = []
        self.task = ""
        basedir = os.path.dirname(os.path.abspath(__file__))
        self.api_key = "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"
        # self.client = Groq(api_key=self.api_key)

        # pinecone.init(
        #     api_key='sk_wzWHqxR19xuEM4HD1nIjWGdyb3FYEO0eA8yBtSvpn1phnpjRxXkx',
        #     environment='us-west-2'
        # )
        # pinecone_index = pinecone.Index('name-of-index')
        
        self.task_library = {
            "left_click": self.left_click,
            "right_click": self.right_click,
            "double_click": self.double_click,
            "move_cursor": self.move_cursor,
            "type": self.type,
            # "select": self.select,
            "vertical_scroll": self.vertical_scroll,
            "horizontal_scroll": self.horizontal_scroll,
            # "search_web": self.search_web,
        }
        self.interactive_controls=[
            'ButtonControl','ListItemControl','MenuItemControl','DocumentControl',
            'EditControl','CheckBoxControl', 'RadioButtonControl','ComboBoxControl',
            'HyperlinkControl','SplitButtonControl','TabItemControl','CustomControl',
            'TreeItemControl','DataItemControl','HeaderItemControl','TextBoxControl',
            'ImageControl'
        ]

    def get_control_coordinates(self, control):
        """Return control's bounding rectangle as (left, top, width, height) if available."""
        try:
            rect = control.BoundingRectangle
            if isinstance(rect, tuple) and len(rect) == 4:
                left, top, right, bottom = rect
            else:
                left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
            width = right - left
            height = bottom - top
            return (left, top, width, height)
        except Exception as e:
            print(f"Error getting coordinates for {control.ControlTypeName}: {e}")
            return None

    def get_major_controls(self, control, indent=0, max_depth=None):
        if max_depth is None:
            max_depth = self.max_depth
        if indent // 4 >= max_depth:
            return

        try:
            name = control.Name.strip() if control.Name else ''
            if control.IsOffscreen and "Grammarly" in name and control.ControlTypeName not in self.interactive_controls:
                return

            coords = self.get_control_coordinates(control)
            if name and coords:
                controlType = control.ControlTypeName
                # Only add if the controlType is one of the keys in our tree.
                if controlType in self.tree:
                    self.tree[controlType].append({"feature": name, "coordinates": coords})
                    print(f"{indent*' '} Added {controlType}: {name} - Coordinates: {coords}")
        except Exception as e:
            try:
                ctype = control.ControlTypeName
            except Exception:
                ctype = "<unknown>"
            print(' ' * indent + f'{ctype}: <error retrieving info> - {e}')

        try:
            # Recursively process child controls
            for child in control.GetChildren():
                self.get_major_controls(child, indent + 4, max_depth)
        except Exception as e:
            print(' ' * indent + f'<error iterating children> - {e}')

    # get only clickable elements
    def get_clickable_elements(max_depth = 35):
        root_control = automation.GetRootControl()
        screen_width, screen_height = pyautogui.size()
        element_dict = {}

        def tree_traversal(node, depth = 0):
            if depth > 35:
                return
            for child in node.GetChildren():
                if child.ControlTypeName in ["Button", "ListItem", "Hyperlink", "CheckBox", "RadioButton"]:
                    element_name = child.Name.strip() if child.Name else "Unnamed"
                    box = child.BoundingRectangle
                    element_dict[element_name] = ((box.left+box.right)/2, (box.top+box.bottom)/2)
                    print(element_dict[element_name])
                tree_traversal(child, depth + 1)
            
        tree_traversal(root_control)
        return element_dict

    def move_cursor(self, x, y):
        pyautogui.moveTo(x, y)
        return True
    
    def left_click(self, x, y):
        pyautogui.click(x, y)
        return True
    
    def right_click(self, x, y):
        pyautogui.rightClick(x, y)
        return True
    
    def double_click(self, x, y):
        pyautogui.doubleClick(x, y)
        return True
    
    def type(self, text):
        pyautogui.typewrite(text)
        return True

    def select(self, text):
        pyautogui.press('down')
        
    def vertical_scroll(self, direction):
        if direction == "up":
            pyautogui.scroll(1)
        elif direction == "down":
            pyautogui.scroll(-1)
        return True
        
    def horizontal_scroll(self, direction):
        if direction == "left":
            pyautogui.hscroll(-1)
        elif direction == "right":
            pyautogui.hscroll(1)
        return True
    
    def search_web(self, query):
        pass

    def hotkey(self, key):
        pyautogui.press(key)
        return True
    
    def getTree(self):
        return self.tree
    
    def capture_screen(self):
        im1 = pyautogui.screenshot()
        im1.save(r"C:\Users\2025130\Documents\aiagent\screenshot.jpeg")
        # image_path = pathlib.Path("C:\\Users\\2025130\\Documents\\aiagent\\screenshot.png").as_uri()

        with open(r"C:\Users\2025130\Documents\aiagent\screenshot.jpeg", "rb") as f:
            img = base64.b64encode(f.read()).decode("utf-8")

        img = f"data:image/jpeg;base64,{img}"
        return img
        


if __name__ == "__main__":
    agent = AutomationAgent()
    # Start recursion with the root control
    print(agent.get_clickable_elements())
    tree = agent.getTree()
    print(tree)
    msg = input("Query: ")
    print(agent.get_action(msg, tree))
