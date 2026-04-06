import argparse
import logging
import sys

from sqlalchemy import select

from config import configure_logging
from app.db import init_db, Session, Staff, StaffContact, Group, ContactType


log = logging.getLogger(__name__)


def create_staff():
    init_db()

    first_name = input("First name: ").strip()
    if not first_name:
        log.error("First name is required.")
        sys.exit(1)

    last_name = input("Last name: ").strip()
    if not last_name:
        log.error("Last name is required.")
        sys.exit(1)

    email = input("Email: ").strip()
    if not email:
        log.error("Email is required.")
        sys.exit(1)

    with Session() as session:
        groups = session.execute(select(Group).order_by(Group.name)).scalars().all()

        selected_group = None
        if groups:
            log.info("Available groups:")
            for i, group in enumerate(groups, start=1):
                log.info(f"  {i}. {group.name}")
            log.info(f"  0. Skip (don't add to any group)")

            choice = input("\nSelect group number [0]: ").strip()
            if choice == "" or choice == "0":
                selected_group = None
            else:
                try:
                    idx = int(choice)
                    if 1 <= idx <= len(groups):
                        selected_group = groups[idx - 1]
                    else:
                        log.error("Invalid group number.")
                        sys.exit(1)
                except ValueError:
                    log.error("Please enter a valid number.")
                    sys.exit(1)
        else:
            log.warning("No groups available, skipping group assignment.")

        staff = Staff(first_name=first_name, last_name=last_name)
        contact = StaffContact(value=email, type=ContactType.EMAIL)
        staff.contacts.append(contact)

        if selected_group:
            staff.groups.append(selected_group)

        session.add(staff)
        session.commit()

        group_info = f", group: {selected_group.name}" if selected_group else ""
        log.info(f"Staff created: {last_name} {first_name} ({email}{group_info})")


def create_group():
    init_db()

    name = input("Group name: ").strip()
    if not name:
        log.error("Group name is required.")
        sys.exit(1)

    with Session() as session:
        existing = session.execute(select(Group).where(Group.name == name)).scalar_one_or_none()
        if existing:
            log.error(f"Group '{name}' already exists.")
            sys.exit(1)

        session.add(Group(name=name))
        session.commit()
        log.info(f"Group '{name}' created.")


def main():
    configure_logging()
    parser = argparse.ArgumentParser(description="Notify service CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("create-staff", help="Create a new staff member")
    subparsers.add_parser("create-group", help="Create a new group")

    args = parser.parse_args()

    commands = {
        "create-staff": create_staff,
        "create-group": create_group,
    }

    if args.command in commands:
        commands[args.command]()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
