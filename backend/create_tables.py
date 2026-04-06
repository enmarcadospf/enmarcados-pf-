from backend.database import Base, engine


def main():
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente en PostgreSQL.")


if __name__ == "__main__":
    main()
