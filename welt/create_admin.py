#!/usr/bin/env python3
"""Legt den 'daniel'-Admin-Account an, falls noch nicht vorhanden."""

import getpass
import sys

import psycopg2
import psycopg2.extras

sys.path.insert(0, "/root/werkraum/welt")
from auth import hash_password

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"

DEFAULT_MODULES = ["resonanz", "tagebuch", "notizen", "kalender"]


def main():
    username = "daniel"
    password = getpass.getpass(f"Passwort für '{username}': ")

    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, role FROM human_users WHERE username = %s", (username,))
            existing = cur.fetchone()

            if existing:
                print(f"User '{username}' existiert bereits (id={existing['id']}, role={existing['role']}).")
                return

            cur.execute(
                """
                INSERT INTO human_users (username, display_name, password_hash, role)
                VALUES (%s, %s, %s, 'admin')
                RETURNING id
                """,
                (username, "Daniel", hash_password(password)),
            )
            user_id = cur.fetchone()["id"]

            cur.execute("INSERT INTO human_profiles (user_id) VALUES (%s)", (user_id,))

            for module in DEFAULT_MODULES:
                cur.execute(
                    "INSERT INTO user_modules (user_id, module_name) VALUES (%s, %s)",
                    (user_id, module),
                )

        conn.commit()
        print(f"Admin '{username}' angelegt (id={user_id}).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
