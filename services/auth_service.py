import uuid
from services.data_store import UserStore, hash_password

ROLE_OWNER    = "Store Manager"
ROLE_EMPLOYEE = "Sales Associate"


class AuthService:
    """Responsible for login, registration, and user deletion logic."""

    def __init__(self, user_store: UserStore):
        self.store = user_store

    def authenticate(self, username: str, password: str) -> tuple[bool, dict | None]:
        """
        Returns (True, user_dict) on success, (False, None) on failure.
        Compares against hashed password stored in users.json.
        """
        user = self.store.find_by_username(username)
        if user and user["password"] == hash_password(password):
            return True, user
        return False, None

    def register_user(
        self, username: str, password: str, email: str, role: str
    ) -> tuple[bool, str]:
        """
        Validates all fields, checks for duplicates, then saves the new user.
        Returns (True, success_message) or (False, error_message).
        """
        # ── Field validation ──────────────────────────────────────────────────
        if not username or len(username.strip()) < 3:
            return False, "Username must be at least 3 characters."
        if not password or len(password) < 5:
            return False, "Password must be at least 5 characters."
        if "@" not in email or "." not in email.split("@")[-1]:
            return False, "Please enter a valid email address."
        if role not in (ROLE_OWNER, ROLE_EMPLOYEE):
            return False, "Invalid role selected."

        # ── Duplicate checks ──────────────────────────────────────────────────
        if self.store.find_by_username(username.strip()):
            return False, "Username already exists."
        if self.store.find_by_email(email.strip()):
            return False, "Email is already registered."

        # ── Create user ───────────────────────────────────────────────────────
        data = self.store.load()
        new_user = {
            "id": f"user_{uuid.uuid4().hex[:8]}",
            "username": username.strip(),
            "password": hash_password(password),
            "role": role,
            "email": email.strip(),
        }
        data["users"].append(new_user)
        self.store.save(data)
        return True, "Registration successful! Please log in."

    def delete_user(self, user_id: str, current_user_id: str) -> tuple[bool, str]:
        """
        Deletes a user by ID with two guards:
          1. Cannot delete your own account.
          2. Cannot delete the last Store Manager.
        Returns (True, message) or (False, error_message).
        """
        if user_id == current_user_id:
            return False, "You cannot delete your own account."

        data = self.store.load()
        target = next((u for u in data["users"] if u["id"] == user_id), None)
        if not target:
            return False, "User not found."

        if target["role"] == ROLE_OWNER:
            managers = [u for u in data["users"] if u["role"] == ROLE_OWNER]
            if len(managers) <= 1:
                return False, "Cannot delete the last Store Manager account."

        data["users"] = [u for u in data["users"] if u["id"] != user_id]
        self.store.save(data)
        return True, f"User '{target['username']}' has been removed."
