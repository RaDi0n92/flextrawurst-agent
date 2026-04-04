from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"


def postgres_kontext():
    return PostgresSaver.from_conn_string(DB_URI)
