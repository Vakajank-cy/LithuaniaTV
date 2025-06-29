import requests
import unittest
import json
import sys

class LithuanianTVBackendTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(LithuanianTVBackendTest, self).__init__(*args, **kwargs)
        self.base_url = "https://d0d1b961-4701-422c-9f92-9a999807b6ec.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.channel_id = None  # Will be set during test execution

    def test_01_health_check(self):
        """Test the health check endpoint"""
        print("\n🔍 Testing health check endpoint...")
        response = requests.get(f"{self.api_url}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "Lithuanian TV Backend")
        print("✅ Health check endpoint is working")

    def test_02_get_channels(self):
        """Test getting all channels"""
        print("\n🔍 Testing get channels endpoint...")
        response = requests.get(f"{self.api_url}/channels")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("channels", data)
        self.assertIsInstance(data["channels"], list)
        self.assertGreater(len(data["channels"]), 0)
        
        # Verify Lithuanian channels exist
        channel_names = [channel["name"] for channel in data["channels"]]
        self.assertIn("LRT Televizija", channel_names)
        self.assertIn("LNK", channel_names)
        self.assertIn("LRT Plius", channel_names)
        
        # Save a channel ID for later tests
        self.channel_id = data["channels"][0]["id"]
        
        # Verify channel structure
        first_channel = data["channels"][0]
        required_fields = ["id", "name", "logo", "stream_url", "category", "language", "description", "is_live"]
        for field in required_fields:
            self.assertIn(field, first_channel)
            
        print(f"✅ Get channels endpoint returned {len(data['channels'])} channels")
        print(f"✅ Found Lithuanian channels: {', '.join(channel_names)}")

    def test_03_get_specific_channel(self):
        """Test getting a specific channel"""
        if not self.channel_id:
            self.test_02_get_channels()
            
        print(f"\n🔍 Testing get specific channel endpoint for ID: {self.channel_id}...")
        response = requests.get(f"{self.api_url}/channels/{self.channel_id}")
        self.assertEqual(response.status_code, 200)
        channel = response.json()
        
        # Verify channel structure
        required_fields = ["id", "name", "logo", "stream_url", "category", "language", "description", "is_live"]
        for field in required_fields:
            self.assertIn(field, channel)
            
        print(f"✅ Successfully retrieved channel: {channel['name']}")
        
    def test_04_get_channel_programs(self):
        """Test getting programs for a specific channel"""
        if not self.channel_id:
            self.test_02_get_channels()
            
        print(f"\n🔍 Testing get channel programs endpoint for channel ID: {self.channel_id}...")
        response = requests.get(f"{self.api_url}/channels/{self.channel_id}/programs")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("programs", data)
        
        # Programs might be empty, but the structure should be correct
        print(f"✅ Successfully retrieved programs. Found {len(data['programs'])} programs")
        
    def test_05_get_current_programs(self):
        """Test getting currently playing programs"""
        print("\n🔍 Testing get current programs endpoint...")
        response = requests.get(f"{self.api_url}/programs/now")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("current_programs", data)
        print(f"✅ Successfully retrieved current programs")
        
    def test_06_get_stream_url(self):
        """Test getting stream URL for a specific channel"""
        if not self.channel_id:
            self.test_02_get_channels()
            
        print(f"\n🔍 Testing get stream URL endpoint for channel ID: {self.channel_id}...")
        response = requests.get(f"{self.api_url}/stream/{self.channel_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        required_fields = ["channel", "stream_url", "is_live"]
        for field in required_fields:
            self.assertIn(field, data)
            
        print(f"✅ Successfully retrieved stream URL for channel: {data['channel']}")
        
    def test_07_invalid_channel_id(self):
        """Test error handling for invalid channel ID"""
        invalid_id = "invalid-channel-id"
        print(f"\n🔍 Testing error handling for invalid channel ID: {invalid_id}...")
        
        response = requests.get(f"{self.api_url}/channels/{invalid_id}")
        self.assertEqual(response.status_code, 404)
        
        response = requests.get(f"{self.api_url}/stream/{invalid_id}")
        self.assertEqual(response.status_code, 404)
        
        print("✅ Error handling for invalid channel ID works correctly")

def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(LithuanianTVBackendTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)