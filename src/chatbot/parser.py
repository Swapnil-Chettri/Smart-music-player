import ollama
import json

class ChatBotBrain:
    def __init__(self):
        self.model_name = "llama3.2"

        self.system_prompt = """
        You are the AI brain for a Smart Music Player.
        Your job is to extract the user's intent from their text.

        You must output ONLY valid JSON. Do not write normal text.

        The JSON structure must be: {"action": "string", "value": "string or number or null"}
        Here are the valid actions and values:
        - Playback: "play", "pause", "stop", (value is null)
        - Volume: "set_volume" (value is integer 0-100)
        - EQ Effects: "apply_effect" (values: "lofi", "bass_boost", "reset")
        - Processing: "apply_process" (values: "reverb")
        - Speed: "Set_rate" (values: 0.8 for slow, 1.2 for fast, 1.0 for normal)
        Info: "get_info" (values: "artist", "title")
        - ChitChat: "chat" (value is a string response to the user)

        Examples:
        User: "Play some music" -> {"action": "play", "value": null}
        User: "Make it sound lofi" -> {"action": "apply_effect", "value": "lofi"}
        User: "Who is this singer?" -> {"action": "get_info", "value": "artist"}
        User: "Hello" -> {"action": "chat", "value": "Hi there! Ready to play some tunes?"}
        """

    def analyze(self, user_text: str) -> tuple[str, any]:
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': user_text},
            ])

            content = response['message']['content']
            clean_text = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            return (data.get("action", "unknown"), data.get("value"))
        except json.JSONDecodeError:
            print(f"Ollama Error: could not parse JSON. Raw output: {content}")
            return ("unknown", None)
        except Exception as e:
            print(f"Ollama API Error: {e}")
            return ("unknown", None)

if __name__ == "__main__":
    brain = ChatBotBrain()
    print(brain.analyze("play some lofi music"))
        






















