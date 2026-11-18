
import json
import os
import shutil
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus

import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:3b"


class JarvisAutomation:

    def __init__(self):
        self.allowed_actions = {
            "open_app",
            "open_path",
            "youtube_search",
            "get_time",
            "shutdown",
            "restart",
            "cancel_shutdown",
        }

        self.apps = {
            "chrome": ["chrome.exe"],
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "file explorer": ["explorer.exe"],
            "explorer": ["explorer.exe"],
            "vscode": ["code"],
            "visual studio code": ["code"],
        }

    # -----------------------------------------
    # 1. Ask local Qwen to understand the user
    # -----------------------------------------

    def understand_request(self, user_request):

        system_prompt = """
You are the command understanding system for a Windows PC assistant.

Convert the user's natural language request into a JSON action plan.

Return ONLY valid JSON in this exact structure:

{
    "actions": [
        {
            "type": "open_app",
            "name": "chrome"
        }
    ]
}

AVAILABLE ACTIONS:

1. open_app
   Required field: name
   Allowed names:
   chrome, notepad, calculator, file explorer, explorer, vscode

2. open_path
   Required field: path
   Use this for opening a drive or folder.
   Example: D:\\Projects

3. youtube_search
   Required field: query
   Example: relaxing music

4. get_time
   No additional fields.

5. shutdown
   No additional fields.

6. restart
   No additional fields.

7. cancel_shutdown
   No additional fields.

RULES:

- Understand natural language, not just exact commands.
- You may create multiple actions when the user requests multiple tasks.
- Keep actions in the order requested.
- Maximum 5 actions per request.
- Never create actions that are not in the available list.
- Never invent paths.
- If a path is unclear, do not guess it.
- If the request is unclear or unsupported, return:
  {"actions": [], "message": "Please clarify your request."}
- Do not execute anything.
- Do not return explanations outside the JSON.
"""

        try:

            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_request
                        }
                    ],
                    "format": "json",
                    "stream": False
                },
                timeout=120
            )

            response.raise_for_status()

            result = response.json()
            content = result["message"]["content"]

            plan = json.loads(content)

            return self.validate_plan(plan)

        except requests.exceptions.ConnectionError:

            return {
                "actions": [],
                "message": "I cannot connect to Ollama. Please make sure Ollama is running."
            }

        except requests.exceptions.Timeout:

            return {
                "actions": [],
                "message": "Qwen took too long to respond. Please try again."
            }

        except Exception as error:

            print("Understanding error:", error)

            return {
                "actions": [],
                "message": "I could not understand that request. Please try again."
            }

    # -----------------------------------------
    # 2. Validate the AI-generated action plan
    # -----------------------------------------

    def validate_plan(self, plan):

        if not isinstance(plan, dict):
            return {"actions": [], "message": "Invalid action plan."}

        actions = plan.get("actions", [])

        if not isinstance(actions, list):
            return {"actions": [], "message": "Invalid action list."}

        if len(actions) > 5:
            return {
                "actions": [],
                "message": "Too many actions in one request. Please split your request."
            }

        validated_actions = []

        for action in actions:

            if not isinstance(action, dict):
                return {"actions": [], "message": "Invalid action detected."}

            action_type = action.get("type")

            if action_type not in self.allowed_actions:
                return {"actions": [], "message": "Unsupported action detected."}

            if action_type == "open_app":

                name = action.get("name")

                if not isinstance(name, str):
                    return {"actions": [], "message": "Invalid application name."}

                name = name.lower().strip()

                if name not in self.apps:
                    return {"actions": [], "message": "This application is not allowed yet."}

                validated_actions.append({
                    "type": "open_app",
                    "name": name
                })

            elif action_type == "open_path":

                path = action.get("path")

                if not isinstance(path, str) or not path.strip():
                    return {"actions": [], "message": "Invalid folder path."}

                validated_actions.append({
                    "type": "open_path",
                    "path": path.strip()
                })

            elif action_type == "youtube_search":

                query = action.get("query")

                if not isinstance(query, str) or not query.strip():
                    return {"actions": [], "message": "Please specify what to search on YouTube."}

                validated_actions.append({
                    "type": "youtube_search",
                    "query": query.strip()
                })

            else:

                validated_actions.append({
                    "type": action_type
                })

        return {
            "actions": validated_actions,
            "message": plan.get("message", "")
        }

    # -----------------------------------------
    # 3. Describe actions before execution
    # -----------------------------------------

    def describe_action(self, action):

        action_type = action["type"]

        if action_type == "open_app":
            return f"Open {action['name']}"

        if action_type == "open_path":
            return f"Open folder or drive: {action['path']}"

        if action_type == "youtube_search":
            return f"Search YouTube for: {action['query']}"

        if action_type == "get_time":
            return "Tell you the current time"

        if action_type == "shutdown":
            return "Shut down this PC in 60 seconds"

        if action_type == "restart":
            return "Restart this PC in 60 seconds"

        if action_type == "cancel_shutdown":
            return "Cancel a pending shutdown or restart"

        return "Unknown action"

    # -----------------------------------------
    # 4. Execute approved actions only
    # -----------------------------------------

    def execute_action(self, action):

        action_type = action["type"]

        try:

            if action_type == "open_app":

                app_name = action["name"]
                commands = self.apps[app_name]

                if app_name == "chrome":

                    chrome_path = self.find_chrome()

                    if chrome_path:
                        subprocess.Popen([chrome_path])
                    else:
                        raise RuntimeError(
                            "Google Chrome was not found on this PC."
                        )

                else:

                    executable = commands[0]

                    if executable == "code" and not shutil.which("code"):
                        raise RuntimeError(
                            "VS Code command was not found. You may need to add it to PATH."
                        )

                    subprocess.Popen([executable])

                return f"Opening {app_name}."

            elif action_type == "open_path":

                path = os.path.expandvars(
                    os.path.expanduser(action["path"])
                )

                path = os.path.abspath(path)

                if not os.path.exists(path):
                    return f"I could not find this location: {path}"

                os.startfile(path)

                return f"Opening {path}."

            elif action_type == "youtube_search":

                query = quote_plus(action["query"])

                url = (
                    "https://www.youtube.com/results?search_query="
                    + query
                )

                self.open_url_in_chrome(url)

                return f"Searching YouTube for {action['query']}."

            elif action_type == "get_time":

                current_time = datetime.now().strftime("%I:%M %p")

                return f"The current time is {current_time}."

            elif action_type == "shutdown":

                subprocess.Popen(
                    ["shutdown", "/s", "/t", "60"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                return "PC shutdown scheduled in 60 seconds."

            elif action_type == "restart":

                subprocess.Popen(
                    ["shutdown", "/r", "/t", "60"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                return "PC restart scheduled in 60 seconds."

            elif action_type == "cancel_shutdown":

                subprocess.Popen(
                    ["shutdown", "/a"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                return "I requested cancellation of the pending shutdown or restart."

            return "This action is not supported."

        except Exception as error:

            return f"Action failed: {error}"

    # -----------------------------------------
    # 5. Find Google Chrome
    # -----------------------------------------

    def find_chrome(self):

        chrome_path = shutil.which("chrome")

        if chrome_path:
            return chrome_path

        possible_paths = [
            os.path.expandvars(
                r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"
            ),
            os.path.expandvars(
                r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"
            ),
            os.path.expandvars(
                r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
            )
        ]

        for path in possible_paths:

            if os.path.isfile(path):
                return path

        return None

    # -----------------------------------------
    # 6. Open a URL in Chrome when available
    # -----------------------------------------

    def open_url_in_chrome(self, url):

        chrome_path = self.find_chrome()

        if chrome_path:
            subprocess.Popen([chrome_path, url])
        else:
            webbrowser.open(url)

    # -----------------------------------------
    # 7. Execute a plan after user confirmation
    # -----------------------------------------

    def execute_plan(self, plan):

        actions = plan.get("actions", [])

        if not actions:
            return ["There are no actions to execute."]

        results = []

        for action in actions:

            result = self.execute_action(action)
            results.append(result)

        return results


# -----------------------------------------
# Standalone testing
# -----------------------------------------

if __name__ == "__main__":

    jarvis = JarvisAutomation()

    print("\nJARVIS PC AUTOMATION TEST")
    print("------------------------")

    while True:

        user_request = input("\nYou: ").strip()

        if user_request.lower() in ["exit", "quit"]:
            print("JARVIS: Goodbye!")
            break

        if not user_request:
            continue

        plan = jarvis.understand_request(user_request)

        actions = plan.get("actions", [])

        if not actions:

            print("\nJARVIS:", plan.get("message", "I could not understand that."))
            continue

        print("\nJARVIS wants to perform:")

        for number, action in enumerate(actions, start=1):
            print(f"{number}. {jarvis.describe_action(action)}")

        confirmation = input(
            "\nShould I perform these actions? (yes/no): "
        ).strip().lower()

        if confirmation in ["yes", "y"]:

            results = jarvis.execute_plan(plan)

            for result in results:
                print("\nJARVIS:", result)

        else:

            print("\nJARVIS: Okay, I will not perform those actions.")
