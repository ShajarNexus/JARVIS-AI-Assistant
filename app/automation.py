
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
            "open_youtube",
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
    # 1. Understand the user's intention
    # -----------------------------------------

    def understand_request(self, user_request):

        system_prompt = """
You are the intent detection and PC command understanding system
for a Windows AI assistant named JARVIS.

Return ONLY valid JSON in this structure:

{
    "intent": "conversation",
    "actions": [],
    "message": ""
}

There are TWO possible intents:

1. conversation
2. automation

IMPORTANT CONVERSATION RULES:

- Questions about JARVIS are normal conversation.
- Greetings are normal conversation.
- General questions are normal conversation.
- Asking about your name is normal conversation.
- Asking how you are is normal conversation.
- Asking what you can do is normal conversation.
- Talking about computers does not automatically mean a PC action.
- Never invent a PC command from a normal sentence.
- If uncertain, choose conversation.

NORMAL CONVERSATION EXAMPLES:

User: Is your name Jarvis?
Output:
{
    "intent": "conversation",
    "actions": [],
    "message": ""
}

User: How are you Jarvis?
Output:
{
    "intent": "conversation",
    "actions": [],
    "message": ""
}

User: Can you tell me what you can do?
Output:
{
    "intent": "conversation",
    "actions": [],
    "message": ""
}

User: I like Google Chrome.
Output:
{
    "intent": "conversation",
    "actions": [],
    "message": ""
}

AUTOMATION RULES:

Choose automation ONLY when the user clearly requests
an action to be performed on the computer.

IMPORTANT YOUTUBE RULE:

YouTube is a WEBSITE, not the Chrome application.

When the user asks to open, visit, launch, or go to YouTube,
ALWAYS use the open_youtube action.

NEVER use open_app with chrome for an explicit request
to open YouTube.

Examples:

User: Open YouTube.
Output:
{
    "intent": "automation",
    "actions": [
        {"type": "open_youtube"}
    ],
    "message": ""
}

User: Go to YouTube.
Output:
{
    "intent": "automation",
    "actions": [
        {"type": "open_youtube"}
    ],
    "message": ""
}

User: Visit YouTube.
Output:
{
    "intent": "automation",
    "actions": [
        {"type": "open_youtube"}
    ],
    "message": ""
}

User: Launch YouTube.
Output:
{
    "intent": "automation",
    "actions": [
        {"type": "open_youtube"}
    ],
    "message": ""
}

User: Open Chrome.
Output:
{
    "intent": "automation",
    "actions": [
        {"type": "open_app", "name": "chrome"}
    ],
    "message": ""
}

User: Please open Notepad.
Output:
{
    "intent": "automation",
    "actions": [
        {"type": "open_app", "name": "notepad"}
    ],
    "message": ""
}

User: Search YouTube for Python tutorials.
Output:
{
    "intent": "automation",
    "actions": [
        {"type": "youtube_search", "query": "Python tutorials"}
    ],
    "message": ""
}

User: What time is it?
Output:
{
    "intent": "automation",
    "actions": [
        {"type": "get_time"}
    ],
    "message": ""
}

AVAILABLE AUTOMATION ACTIONS:

1. open_app
Required field: name

Allowed names:
chrome, notepad, calculator, file explorer, explorer, vscode

2. open_path
Required field: path

Use only when the user clearly asks to open a specific drive or folder.

3. open_youtube
No additional fields.
Opens https://www.youtube.com/

4. youtube_search
Required field: query

Searches YouTube for the requested content.

5. get_time
No additional fields.

6. shutdown
No additional fields.

7. restart
No additional fields.

8. cancel_shutdown
No additional fields.

ADDITIONAL RULES:

- Understand natural language commands.
- Multiple actions are allowed if explicitly requested.
- Maximum 5 actions.
- Never invent a folder path.
- Never create unsupported actions.
- Never execute anything.
- If the user requests an unsupported PC action, choose conversation.
- If the request is unclear, choose conversation.
- Return only valid JSON.
- Do not include explanations outside JSON.
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
                    "stream": False,
                    "options": {
                        "temperature": 0
                    }
                },
                timeout=120
            )

            response.raise_for_status()

            result = response.json()
            content = result["message"]["content"]

            plan = json.loads(content)

            return self.validate_plan(plan)

        except requests.exceptions.ConnectionError:

            return self.invalid_plan()

        except requests.exceptions.Timeout:

            return self.invalid_plan()

        except Exception as error:

            print("Understanding error:", error)

            return self.invalid_plan()

    # -----------------------------------------
    # 2. Validate the AI-generated action plan
    # -----------------------------------------

    def validate_plan(self, plan):

        if not isinstance(plan, dict):
            return self.invalid_plan()

        intent = plan.get("intent")

        if intent != "automation":
            return self.invalid_plan()

        actions = plan.get("actions", [])

        if not isinstance(actions, list) or not actions:
            return self.invalid_plan()

        if len(actions) > 5:
            return self.invalid_plan()

        validated_actions = []

        for action in actions:

            if not isinstance(action, dict):
                return self.invalid_plan()

            action_type = action.get("type")

            if action_type not in self.allowed_actions:
                return self.invalid_plan()

            if action_type == "open_app":

                name = action.get("name")

                if not isinstance(name, str):
                    return self.invalid_plan()

                name = name.lower().strip()

                if name not in self.apps:
                    return self.invalid_plan()

                validated_actions.append({
                    "type": "open_app",
                    "name": name
                })

            elif action_type == "open_path":

                path = action.get("path")

                if not isinstance(path, str) or not path.strip():
                    return self.invalid_plan()

                path = os.path.expandvars(
                    os.path.expanduser(path.strip())
                )

                if not os.path.exists(path):
                    return self.invalid_plan()

                validated_actions.append({
                    "type": "open_path",
                    "path": path
                })

            elif action_type == "open_youtube":

                validated_actions.append({
                    "type": "open_youtube"
                })

            elif action_type == "youtube_search":

                query = action.get("query")

                if not isinstance(query, str) or not query.strip():
                    return self.invalid_plan()

                validated_actions.append({
                    "type": "youtube_search",
                    "query": query.strip()
                })

            else:

                validated_actions.append({
                    "type": action_type
                })

        return {
            "intent": "automation",
            "actions": validated_actions,
            "message": ""
        }

    def invalid_plan(self):

        return {
            "intent": "conversation",
            "actions": [],
            "message": ""
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

        if action_type == "open_youtube":
            return "Open YouTube"

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

                if app_name == "chrome":

                    chrome_path = self.find_chrome()

                    if chrome_path:
                        subprocess.Popen([chrome_path])
                    else:
                        raise RuntimeError(
                            "Google Chrome was not found on this PC."
                        )

                else:

                    executable = self.apps[app_name][0]

                    if executable == "code" and not shutil.which("code"):

                        raise RuntimeError(
                            "VS Code command was not found. "
                            "You may need to add it to PATH."
                        )

                    subprocess.Popen([executable])

                return f"Opening {app_name}."

            elif action_type == "open_path":

                path = os.path.abspath(
                    os.path.expandvars(
                        os.path.expanduser(action["path"])
                    )
                )

                if not os.path.exists(path):
                    return f"I could not find this location: {path}"

                os.startfile(path)

                return f"Opening {path}."

            elif action_type == "open_youtube":

                self.open_url_in_chrome(
                    "https://www.youtube.com/"
                )

                return "Opening YouTube."

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
            os.path.join(
                os.environ.get("PROGRAMFILES", ""),
                "Google",
                "Chrome",
                "Application",
                "chrome.exe"
            ),

            os.path.join(
                os.environ.get("PROGRAMFILES(X86)", ""),
                "Google",
                "Chrome",
                "Application",
                "chrome.exe"
            ),

            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Google",
                "Chrome",
                "Application",
                "chrome.exe"
            )
        ]

        for path in possible_paths:

            if path and os.path.isfile(path):
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
    # 7. Execute an approved plan
    # -----------------------------------------

    def execute_plan(self, plan):

        if plan.get("intent") != "automation":
            return ["There are no actions to execute."]

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
    print("Type 'exit' to stop.")

    while True:

        user_request = input("\nYou: ").strip()

        if user_request.lower() in ["exit", "quit"]:

            print("JARVIS: Goodbye!")
            break

        if not user_request:
            continue

        plan = jarvis.understand_request(user_request)

        actions = plan.get("actions", [])

        if plan.get("intent") != "automation" or not actions:

            print("\nJARVIS: This is normal conversation.")
            print("The main JARVIS application should answer this.")
            continue

        print("\nJARVIS wants to perform:")

        for number, action in enumerate(actions, start=1):

            print(
                f"{number}. {jarvis.describe_action(action)}"
            )

        confirmation = input(
            "\nShould I perform these actions? (yes/no): "
        ).strip().lower()

        if confirmation in ["yes", "y"]:

            results = jarvis.execute_plan(plan)

            for result in results:
                print("\nJARVIS:", result)

        else:

            print("\nJARVIS: Okay, I will not perform those actions.")
