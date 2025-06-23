import uiautomation as automation
import pyautogui

class uiFeatures():
    def __init__(self):
        pass

    def get_clickable_elements(max_depth = 35):
        root_control = automation.GetRootControl()
        screen_width, screen_height = pyautogui.size()
        element_dict = {}

        def tree_traversal(node, depth = 0):
            if depth > max_depth:
                return
            for child in node.GetChildren():
                if child.ControlTypeName in ["Button", "ListItem", "Hyperlink", "CheckBox", "RadioButton"]:
                    element_name = child.Name.strip() if child.Name else "Unnamed"
                    box = child.BoundingRectangle
                    element_dict[element_name] = ((box.left+box.right)/2, (box.top+box.bottom)/2)

                tree_traversal(child, depth + 1)
            
        tree_traversal(root_control)
        return element_dict
    
