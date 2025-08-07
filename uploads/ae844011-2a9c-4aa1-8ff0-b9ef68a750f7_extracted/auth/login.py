
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
