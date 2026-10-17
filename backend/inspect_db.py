import psycopg2

def inspect_database():
    conn = psycopg2.connect(host="localhost", port=5432, user="postgres", dbname="wallpapers_8k1_db")
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = [r[0] for r in cur.fetchall()]
    print(f"=== PUBLIC TABLES ({len(tables)}) ===")
    for t in tables:
        print(f"  - {t}")

    cur.execute("""
        SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name 
        FROM information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
        ORDER BY tc.table_name;
    """)
    fks = cur.fetchall()
    print(f"=== FOREIGN KEYS ({len(fks)}) ===")
    for fk in fks:
        print(f"  {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")

    cur.execute("""
        SELECT tc.table_name, tc.constraint_name
        FROM information_schema.table_constraints tc
        WHERE tc.constraint_type = 'UNIQUE' AND tc.table_schema = 'public'
        ORDER BY tc.table_name;
    """)
    uqs = cur.fetchall()
    print(f"=== UNIQUE CONSTRAINTS ({len(uqs)}) ===")
    for uq in uqs:
        print(f"  {uq[0]}: {uq[1]}")

    cur.execute("""
        SELECT tablename, indexname 
        FROM pg_indexes 
        WHERE schemaname = 'public' 
        ORDER BY tablename, indexname;
    """)
    indexes = cur.fetchall()
    print(f"=== INDEXES ({len(indexes)}) ===")
    for idx in indexes:
        print(f"  {idx[0]}: {idx[1]}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    inspect_database()
