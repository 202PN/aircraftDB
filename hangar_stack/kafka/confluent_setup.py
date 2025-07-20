#!/usr/bin/env python3
"""
Confluent Cloud Setup for HangarStack

This script helps set up Confluent Cloud integration for the HangarStack application.
It creates topics, sets up authentication, and configures the environment.
"""

import os
import json
import subprocess
import sys
from pathlib import Path

class ConfluentSetup:
    def __init__(self):
        self.config_file = Path('.env')
        self.topics = {
            'aircraft_views': 'hangarstack.aircraft.views',
            'user_activity': 'hangarstack.user.activity',
            'data_updates': 'hangarstack.data.updates',
            'search_queries': 'hangarstack.search.queries',
            'system_events': 'hangarstack.system.events'
        }

    def check_confluent_cli(self):
        """Check if Confluent CLI is installed"""
        try:
            result = subprocess.run(['confluent', 'version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Confluent CLI is installed")
                return True
            else:
                print("❌ Confluent CLI is not installed")
                return False
        except FileNotFoundError:
            print("❌ Confluent CLI is not installed")
            return False

    def install_confluent_cli(self):
        """Install Confluent CLI"""
        print("📦 Installing Confluent CLI...")
        
        # macOS
        if sys.platform == "darwin":
            subprocess.run(['brew', 'install', 'confluentinc/tap/cli'])
        # Linux
        elif sys.platform.startswith("linux"):
            subprocess.run(['curl', '-L', '--http1.1', 
                          'https://cnfl.io/cli', '|', 'sh', '-s', '--', '-b', '/usr/local/bin'])
        # Windows
        elif sys.platform == "win32":
            print("Please install Confluent CLI manually from: https://docs.confluent.io/confluent-cli/current/install.html")
            return False
        
        print("✅ Confluent CLI installed successfully")
        return True

    def login_to_confluent(self):
        """Login to Confluent Cloud"""
        print("🔐 Logging into Confluent Cloud...")
        print("You'll be redirected to your browser to complete authentication.")
        print("If the browser doesn't open automatically, please:")
        print("1. Open your browser manually")
        print("2. Go to https://confluent.cloud/")
        print("3. Login to your account")
        print("4. Return to this terminal")
        
        # Try interactive login first
        try:
            result = subprocess.run(['confluent', 'login'], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Successfully logged into Confluent Cloud")
                return True
            else:
                print(f"❌ Login failed with return code: {result.returncode}")
                print("Error output:", result.stderr)
                print("Standard output:", result.stdout)
                
                # Try alternative login method
                return self.try_alternative_login()
                
        except subprocess.TimeoutExpired:
            print("⏰ Login timed out. Trying alternative method...")
            return self.try_alternative_login()
        except Exception as e:
            print(f"❌ Login error: {e}")
            return self.try_alternative_login()

    def try_alternative_login(self):
        """Try alternative login methods"""
        print("\n🔄 Trying alternative login methods...")
        
        # Method 1: Try with --save flag
        print("Method 1: Trying with --save flag...")
        try:
            result = subprocess.run(['confluent', 'login', '--save'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Login successful with --save flag")
                return True
        except Exception as e:
            print(f"Method 1 failed: {e}")
        
        # Method 2: Try interactive mode
        print("Method 2: Trying interactive mode...")
        try:
            result = subprocess.run(['confluent', 'login', '--interactive'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Login successful in interactive mode")
                return True
        except Exception as e:
            print(f"Method 2 failed: {e}")
        
        # Method 3: Manual login instructions
        print("Method 3: Manual login required...")
        print("\n📋 Manual Login Instructions:")
        print("1. Open your terminal/command prompt")
        print("2. Run: confluent login")
        print("3. Follow the browser authentication")
        print("4. Return here and press Enter to continue")
        
        input("Press Enter after you've completed the manual login...")
        
        # Verify login
        try:
            result = subprocess.run(['confluent', 'whoami'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Manual login successful!")
                return True
            else:
                print("❌ Manual login verification failed")
                print("Please ensure you're logged in and try again")
                return False
        except Exception as e:
            print(f"❌ Error verifying login: {e}")
            return False

    def create_environment(self, env_name="hangarstack"):
        """Create a Confluent Cloud environment"""
        print(f"🌍 Creating environment: {env_name}")
        
        result = subprocess.run(['confluent', 'environment', 'create', env_name], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Environment '{env_name}' created successfully")
            return env_name
        else:
            print("❌ Failed to create environment")
            print("Error:", result.stderr)
            return None

    def create_cluster(self, env_id, cluster_name="hangarstack-cluster"):
        """Create a Confluent Cloud cluster"""
        print(f"🏢 Creating cluster: {cluster_name}")
        
        # Create basic cluster (free tier)
        result = subprocess.run([
            'confluent', 'kafka', 'cluster', 'create', cluster_name,
            '--cloud', 'aws',
            '--region', 'us-west-2',
            '--type', 'basic'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Cluster '{cluster_name}' created successfully")
            return cluster_name
        else:
            print("❌ Failed to create cluster")
            print("Error:", result.stderr)
            return None

    def create_api_key(self, cluster_id):
        """Create API key for the cluster"""
        print("🔑 Creating API key...")
        
        result = subprocess.run([
            'confluent', 'api-key', 'create',
            '--resource', cluster_id,
            '--output', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            api_key_data = json.loads(result.stdout)
            return api_key_data['key'], api_key_data['secret']
        else:
            print("❌ Failed to create API key")
            print("Error:", result.stderr)
            return None, None

    def create_topics(self, cluster_id):
        """Create Kafka topics"""
        print("📝 Creating topics...")
        
        for topic_name, topic in self.topics.items():
            print(f"Creating topic: {topic}")
            
            result = subprocess.run([
                'confluent', 'kafka', 'topic', 'create', topic,
                '--cluster', cluster_id,
                '--partitions', '3',
                '--replicas', '3'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Topic '{topic}' created successfully")
            else:
                print(f"⚠️ Topic '{topic}' may already exist or failed to create")
                print("Error:", result.stderr)

    def get_bootstrap_servers(self, cluster_id):
        """Get bootstrap servers for the cluster"""
        print("🔗 Getting bootstrap servers...")
        
        result = subprocess.run([
            'confluent', 'kafka', 'cluster', 'describe', cluster_id,
            '--output', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            cluster_data = json.loads(result.stdout)
            return cluster_data['endpoint']
        else:
            print("❌ Failed to get bootstrap servers")
            print("Error:", result.stderr)
            return None

    def create_env_file(self, bootstrap_servers, api_key, api_secret):
        """Create .env file with Confluent Cloud configuration"""
        print("📄 Creating .env file...")
        
        env_content = f"""# Confluent Cloud Configuration
KAFKA_BOOTSTRAP_SERVERS={bootstrap_servers}
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_USERNAME={api_key}
KAFKA_PASSWORD={api_secret}

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=true
"""
        
        with open(self.config_file, 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully")

    def setup_confluent_cloud(self):
        """Complete Confluent Cloud setup"""
        print("🚀 Setting up Confluent Cloud for HangarStack...")
        print("=" * 50)
        
        # Check/install Confluent CLI
        if not self.check_confluent_cli():
            if not self.install_confluent_cli():
                return False
        
        # Login to Confluent Cloud
        if not self.login_to_confluent():
            return False
        
        # Create environment
        env_name = self.create_environment()
        if not env_name:
            return False
        
        # Set environment
        subprocess.run(['confluent', 'environment', 'use', env_name])
        
        # Create cluster
        cluster_name = self.create_cluster(env_name)
        if not cluster_name:
            return False
        
        # Get cluster ID
        result = subprocess.run(['confluent', 'kafka', 'cluster', 'list', '--output', 'json'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            clusters = json.loads(result.stdout)
            cluster_id = None
            for cluster in clusters:
                if cluster['name'] == cluster_name:
                    cluster_id = cluster['id']
                    break
            
            if not cluster_id:
                print("❌ Could not find cluster ID")
                return False
        else:
            print("❌ Failed to get cluster list")
            return False
        
        # Create API key
        api_key, api_secret = self.create_api_key(cluster_id)
        if not api_key or not api_secret:
            return False
        
        # Get bootstrap servers
        bootstrap_servers = self.get_bootstrap_servers(cluster_id)
        if not bootstrap_servers:
            return False
        
        # Create topics
        self.create_topics(cluster_id)
        
        # Create .env file
        self.create_env_file(bootstrap_servers, api_key, api_secret)
        
        print("=" * 50)
        print("🎉 Confluent Cloud setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test the integration: python test_kafka.py producer")
        print("3. Run the application: python app.py")
        
        return True

def main():
    """Main function"""
    setup = ConfluentSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
Confluent Cloud Setup for HangarStack

Usage:
  python confluent_setup.py          # Run complete setup
  python confluent_setup.py --help   # Show this help

This script will:
1. Install Confluent CLI (if needed)
2. Login to Confluent Cloud
3. Create environment and cluster
4. Create API keys
5. Create Kafka topics
6. Generate .env file with configuration

Prerequisites:
- Confluent Cloud account (free tier available)
- Internet connection
- Python 3.8+
        """)
        return
    
    setup.setup_confluent_cloud()

if __name__ == "__main__":
    main() 