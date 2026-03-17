from .api import AgentAPI

class ChatInterface:
    def __init__(self, api: AgentAPI):
        self.api = api
        self._history: dict[str, list[dict]] = {}

    def send_message(self, session_id: str, message: str, user_id: str = "anonymous") -> str:
        result = self.api.submit_goal(message, session_id, user_id)
        entry = {"role": "user", "content": message}
        if session_id not in self._history:
            self._history[session_id] = []
        self._history[session_id].append(entry)
        
        session_result = self.api.get_result(session_id)
        if "error" in session_result:
            response = f"Error: {session_result['error']}"
        else:
            results = session_result.get("results", {})
            if results:
                successes = sum(1 for r in results.values() if r.get("status") == "success")
                response = f"Completed {successes}/{len(results)} steps for: {message}"
            else:
                response = f"Processing: {message}"
        
        self._history[session_id].append({"role": "assistant", "content": response})
        return response

    def get_history(self, session_id: str) -> list[dict]:
        return self._history.get(session_id, [])

    def reset_session(self, session_id: str) -> None:
        self._history.pop(session_id, None)
