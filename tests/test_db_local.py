from database import Database
import pandas as pd

def test_local():
    print("Testing locally with SQLite...")
    db = Database()
    
    # Test get_unique_values
    print("\nTesting get_unique_values('area')...")
    areas = db.get_unique_values('area')
    print(f"Areas found: {areas}")
    assert isinstance(areas, list)
    
    # Test get_all_indicadores
    print("\nTesting get_all_indicadores()...")
    df = db.get_all_indicadores()
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    if not df.empty:
        print(f"First row ID: {df.iloc[0]['id']} (Type: {type(df.iloc[0]['id'])})")
    
    print("\n✅ Tests passed!")

if __name__ == "__main__":
    test_local()
