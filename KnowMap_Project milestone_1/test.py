import requests
import json

BASE_URL = "http://localhost:8001"

def test_backend():
    print("🔍 Testing Backend Connection...")
    print("=" * 50)
    
    # Test root
    try:
        r = requests.get(BASE_URL)
        print(f"✅ Root: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"❌ Backend not running: {e}")
        return
    
    # Test signup - use short password
    print("\n📝 Testing Signup...")
    try:
        r = requests.post(f"{BASE_URL}/signup", 
                         json={"username": "testuser", "password": "test123"})  # Short password
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test login
    print("\n🔑 Testing Login...")
    try:
        r = requests.post(f"{BASE_URL}/login", 
                         json={"username": "testuser", "password": "test123"})
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test save profile
    print("\n💾 Testing Save Profile...")
    try:
        r = requests.post(f"{BASE_URL}/save_profile", 
                         json={"username": "testuser", "interests": ["AI", "ML"]})
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Debug info
    print("\n🐛 Debug Info:")
    try:
        r = requests.get(f"{BASE_URL}/debug")
        print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_backend()