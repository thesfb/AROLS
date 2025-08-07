import os
import shutil
import zipfile
import requests
import time
import json
import textwrap

# The base URL of your running Go application
API_URL = "http://localhost:8080"

def create_dummy_project(base_path="temp_test_project"):
    """Creates a temporary directory with various Python files for testing."""
    print(f"🔧 Creating dummy project at '{base_path}'...")
    
    # Clean up any previous runs
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    
    # Define project structure and file content
    project_files = {
        "auth/login.py": textwrap.dedent("""
            # Hardcoded secret for security analysis
            SECRET_KEY = "super-secret-key-that-should-not-be-in-code"
            
            def login(user, password):
                # Hardcoded password for security analysis
                if user == "admin" and password == 'admin123':
                    return True
                return False

            # TODO: Add two-factor authentication
            def check_permissions(user):
                print("Checking permissions...")
        """),
        "core/calculator.py": textwrap.dedent("""
            # High complexity function for complexity analysis
            def complex_function(a, b, c, d, e):
                if a > b and (c < d or e == 1):
                    if b > c and (d < e or a == 2):
                        if c > d and (e < a or b == 3):
                            if d > e and (a < b or c == 4):
                                return 100 # This is a magic number
                elif a == 5 or b == 6 or c == 7 or d == 8 or e == 9:
                    return 200
                return 0
        """),
        "utils/formatter.py": textwrap.dedent("""
            # Long line for code smell analysis
            def long_line_function():
                # FIXME: This line is way too long and should be broken up into multiple lines for better readability and to adhere to style guides like PEP 8.
                very_long_variable_name_that_is_used_to_demonstrate_a_very_long_line_of_code = "This is a string that makes the line even longer than it needs to be."
                return very_long_variable_name_that_is_used_to_demonstrate_a_very_long_line_of_code
        """),
        "services/payment_service.py": textwrap.dedent("""
            # Business logic patterns
            def calculate_invoice_total(items, tax_rate):
                subtotal = sum(item['price'] for item in items)
                tax = subtotal * tax_rate
                return subtotal + tax

            def process_customer_payment(customer_id, amount):
                print(f"Processing payment of {amount} for customer {customer_id}")
                return {"status": "success"}
        """),
        "config.txt": "some_config_value=12345"
    }

    # Create directories and files
    for path, content in project_files.items():
        full_path = os.path.join(base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
            
    print("✅ Dummy project created.")
    return base_path

def zip_project(project_path, zip_name="test_project.zip"):
    """Zips the contents of the project directory."""
    print(f"📦 Zipping project '{project_path}' to '{zip_name}'...")
    shutil.make_archive(zip_name.replace('.zip', ''), 'zip', project_path)
    print("✅ Project zipped.")
    return zip_name

def cleanup(paths):
    """Removes temporary files and directories."""
    print("\n🧹 Cleaning up temporary files...")
    for path in paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    print("✅ Cleanup complete.")

def run_test():
    """Main function to run the end-to-end test."""
    project_path = None
    zip_path = None
    
    try:
        # 1. Setup project
        project_path = create_dummy_project()
        zip_path = zip_project(project_path)

        # 2. Upload and start analysis
        print(f"\n🚀 Uploading '{zip_path}' to the server...")
        with open(zip_path, 'rb') as f:
            files = {'codebase': (zip_path, f, 'application/zip')}
            response = requests.post(f"{API_URL}/api/analyze", files=files)
            response.raise_for_status() # Raise an exception for bad status codes
        
        job_info = response.json()
        job_id = job_info.get('job_id')
        
        if not job_id:
            raise Exception("Failed to get job_id from server.")
            
        print(f"✅ Upload successful. Job ID: {job_id}")

        # 3. Poll for results
        print("\n⏳ Waiting for analysis to complete (checking every 2 seconds)...")
        while True:
            response = requests.get(f"{API_URL}/api/job/{job_id}")
            response.raise_for_status()
            status_info = response.json()
            status = status_info.get('status')
            
            print(f"   Current status: {status}")
            
            if status == 'completed':
                print("✅ Analysis complete!")
                break
            if status == 'failed':
                raise Exception("Analysis failed on the server.")
                
            time.sleep(2)

        # 4. Fetch and display results
        print("\n📊 Fetching final results...")
        response = requests.get(f"{API_URL}/api/result/{job_id}")
        response.raise_for_status()
        results = response.json()
        
        print("\n" + "="*20 + " ANALYSIS RESULTS " + "="*20)
        print(json.dumps(results, indent=2))
        print("="*60)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: Could not connect to the server at {API_URL}.")
        print("   Please make sure your Go application is running.")
        print(f"   Details: {e}")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        # 5. Cleanup
        if project_path and zip_path:
            cleanup([project_path, zip_path])

if __name__ == "__main__":
    run_test()
