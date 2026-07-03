from sqlalchemy import text
from database.session import engine

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS preferences JSON 
                DEFAULT '{"theme": "system", "email_notifs": true, "data_sharing": false}'
            """))
            conn.commit()
            print("Successfully added preferences column to users table.")
        except Exception as e:
            # Fallback for databases that don't support IF NOT EXISTS on ALTER
            try:
                conn.rollback()
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN preferences JSON 
                    DEFAULT '{"theme": "system", "email_notifs": true, "data_sharing": false}'
                """))
                conn.commit()
                print("Successfully added preferences column to users table (fallback).")
            except Exception as e2:
                print(f"Column might already exist: {e2}")

if __name__ == "__main__":
    migrate()
