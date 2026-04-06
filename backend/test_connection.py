from sqlalchemy import text

from backend.database import engine


def main():
    with engine.connect() as conn:
        version = conn.execute(text("select version()")).scalar()
        print("Conexion OK")
        print(version)


if __name__ == "__main__":
    main()
