"""
Test script for the Word Vector API
Run this after starting the API server to verify all endpoints work correctly
"""

import requests
import time
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_similarity():
    """Test the similarity endpoint"""
    print("\n🔍 Testing similarity...")
    test_cases = [
        ("king", "queen"),
        ("man", "woman"),
        ("good", "bad"),
        ("cat", "dog")
    ]
    
    for word1, word2 in test_cases:
        try:
            response = requests.get(f"{BASE_URL}/similarity", params={
                "word1": word1,
                "word2": word2
            })
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {word1} ↔ {word2}: {data['similarity']:.4f}")
            else:
                print(f"❌ {word1} ↔ {word2}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error testing {word1} ↔ {word2}: {e}")

def test_analogy():
    """Test the analogy endpoint"""
    print("\n🔍 Testing analogies...")
    test_cases = [
        ("king", "man", "woman"),
        ("paris", "france", "italy"),
        ("good", "better", "bad"),
        ("walk", "walking", "swim")
    ]
    
    for a, b, c in test_cases:
        try:
            response = requests.get(f"{BASE_URL}/analogy", params={
                "a": a,
                "b": b, 
                "c": c,
                "topn": 3
            })
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {a} - {b} + {c} =")
                for result in data['results']:
                    print(f"   {result['word']} ({result['similarity']:.4f})")
            else:
                print(f"❌ {a} - {b} + {c}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error testing {a} - {b} + {c}: {e}")

def test_neighbors():
    """Test the neighbors endpoint"""
    print("\n🔍 Testing neighbors...")
    test_words = ["king", "computer", "happy", "dog"]
    
    for word in test_words:
        try:
            response = requests.get(f"{BASE_URL}/neighbors", params={
                "word": word,
                "topn": 5
            })
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Neighbors of '{word}':")
                for neighbor in data['neighbors']:
                    print(f"   {neighbor['word']} ({neighbor['similarity']:.4f})")
            else:
                print(f"❌ {word}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error testing neighbors for {word}: {e}")

def test_vocabulary():
    """Test the vocabulary endpoint"""
    print("\n🔍 Testing vocabulary info...")
    try:
        response = requests.get(f"{BASE_URL}/vocabulary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Vocabulary size: {data['vocabulary_size']:,}")
            print(f"✅ Vector dimensions: {data['vector_dimensions']}")
            print(f"✅ Sample words: {', '.join(data['sample_words'][:10])}...")
        else:
            print(f"❌ Vocabulary test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing vocabulary: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting API tests...")
    print("Make sure the API server is running on http://localhost:8000")
    print("=" * 60)
    
    # Wait a moment for the server to be ready
    time.sleep(1)
    
    # Run tests
    if test_health_check():
        test_similarity()
        test_analogy() 
        test_neighbors()
        test_vocabulary()
        print("\n✅ All tests completed!")
    else:
        print("\n❌ Health check failed. Make sure the server is running.")

if __name__ == "__main__":
    main()
