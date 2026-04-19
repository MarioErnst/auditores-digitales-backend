import requests
from uuid import uuid4

from backend.config import settings


class N8NClient:
    def __init__(self) -> None:
        self.base_url = settings.n8n_base_url
        self.timeout = 30

    def trigger_upload(self, file_base64: str, filename: str, session_id: str) -> dict:
        request_id = str(uuid4())
        url = f"{self.base_url}/webhook/upload-evidence"
        payload = {
            "request_id": request_id,
            "file": file_base64,
            "filename": filename,
            "session_id": session_id,
        }

        print(f"📤 Disparando N8N upload para {filename} (request_id={request_id})")
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            if response.status_code in (200, 202):
                print(f"✅ N8N respondió OK para request_id={request_id}")
                return response.json()
            print(f"⚠️ N8N respondió con status {response.status_code}")
            return {"status": "error", "detail": f"N8N status {response.status_code}"}
        except requests.Timeout:
            raise Exception("N8N no responde (timeout)")
        except Exception as e:
            print(f"⚠️ N8N no disponible: {e}")
            return {"status": "error", "detail": str(e)}

    def trigger_chat(self, question: str, session_id: str, request_id: str) -> dict:
        url = f"{self.base_url}/webhook/chat-query"
        payload = {
            "request_id": request_id,
            "question": question,
            "session_id": session_id,
        }

        print(f"💬 Disparando N8N chat para session_id={session_id} (request_id={request_id})")
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            if response.status_code in (200, 202):
                print(f"✅ N8N respondió OK para request_id={request_id}")
                return response.json()
            print(f"⚠️ N8N respondió con status {response.status_code}")
            return {"status": "error", "detail": f"N8N status {response.status_code}"}
        except requests.Timeout:
            raise Exception("N8N no responde (timeout)")
        except Exception as e:
            print(f"⚠️ N8N no disponible: {e}")
            return {"status": "error", "detail": str(e)}


n8n_client = N8NClient()
