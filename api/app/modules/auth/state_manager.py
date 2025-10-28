import hashlib
import hmac
import secrets
import time

from app.core.config import settings


class StateManager:
    def __init__(self) -> None:
        self._state_secret = settings.WORKOS_STATE_SECRET
        self._state_timeout = settings.WORKOS_STATE_TIMEOUT

    def generate_state(self) -> str:
        random_state = secrets.token_urlsafe(32)
        timestamp = str(int(time.time()))
        payload = f"{random_state}:{timestamp}"

        signature = hmac.new(
            self._state_secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        state = f"{signature}:{payload}"

        return state

    def validate_state(self, state: str) -> bool:
        if not state:
            return False

        try:
            parts = state.split(":", 2)
            if len(parts) != 3:
                return False

            signature, random_state, timestamp = parts
            payload = f"{random_state}:{timestamp}"
            expected_signature = hmac.new(
                self._state_secret.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                return False

            try:
                state_time = int(timestamp)
                current_time = int(time.time())
                if current_time - state_time > self._state_timeout:
                    return False
            except ValueError:
                return False

            return True

        except (ValueError, KeyError):
            return False
