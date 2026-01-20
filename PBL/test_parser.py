from query_parser import QueryParser

def test_queries():
    queries = [
        "CREATE DATABASE testdb;",
        "DROP DATABASE testdb;",
        "USE testdb;",
        "SHOW DATABASES;",
        "SHOW TABLES;",
        "DESCRIBE users;",
        "CREATE TABLE users (id INT, name TEXT, age INT);",
        "DROP TABLE users;",
        "INSERT INTO users VALUES (1, 'Alice', 25);",
        "SELECT * FROM users;",
        "SELECT name, age FROM users WHERE age > 20 ORDER BY name LIMIT 5;",
        "SELECT COUNT(*) FROM users;",
        "UPDATE users SET age = 30 WHERE id = 1;",
        "DELETE FROM users WHERE id = 1;"
    ]
    
    for q in queries:
        try:
            result = QueryParser.parse(q)
            print(f"\n✅ Query: {q}\nParsed Result: {result}")
        except Exception as e:
            print(f"\n❌ Query: {q}\nError: {e}")

if __name__ == "__main__":
    test_queries()
