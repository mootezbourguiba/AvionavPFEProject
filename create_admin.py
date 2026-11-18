
from datetime import datetime
from getpass import getpass

from backend.database import SessionLocal
from backend.models.user import User, UserRole
from backend.core.security import get_password_hash


def create_admin():
    db = SessionLocal()

    try:
        existing = db.query(User).filter(
            User.username == "admin"
        ).first()

        if existing:
            print("An administrator account already exists.")
            return

        email = input("Enter administrator email: ").strip()
        password = getpass("Enter administrator password: ")
        confirm = getpass("Confirm administrator password: ")

        if not email or "@" not in email:
            print("Invalid email address.")
            return

        if len(password) < 8:
            print("Password must contain at least 8 characters.")
            return

        if password != confirm:
            print("Passwords do not match.")
            return

        now = datetime.utcnow()

        admin = User(
            username="admin",
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMINISTRATOR,
            disabled=False,
            created_at=now,
            updated_at=now
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\nSUCCESS: Administrator account created!")
        print("Username:", admin.username)
        print("Email:", admin.email)
        print("Role:", admin.role.value)
        print("Disabled:", admin.disabled)

    except Exception as e:
        db.rollback()
        print("ERROR:", e)

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
