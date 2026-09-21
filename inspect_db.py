from sqlalchemy import create_engine, inspect
from backend.database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
inspector = inspect(engine)

for table_name in inspector.get_table_names():
    print(f"\n================ TABLA: {table_name} ================")
    pk = inspector.get_pk_constraint(table_name)
    print(f"Primary Key: {pk.get('constrained_columns')}")
    
    print("Columnas:")
    for column in inspector.get_columns(table_name):
        print(f"  - {column['name']}: {column['type']} (Nullable: {column['nullable']})")
        
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        print("Foreign Keys:")
        for fk in fks:
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
