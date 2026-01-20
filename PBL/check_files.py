"""
check_files.py
Verify all required files exist and can be imported
"""

import os
import sys

print("StructDB File Checker")
print("=" * 60)

# Check current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {current_dir}\n")

# List of required files
required_files = [
    'main.py',
    'gui.py',
    'database_manager.py',
    'database.py',
    'query_parser.py',
    'data_structures.py',
    'requirements.txt',
    'README.md'
]

print("Checking for required files:")
print("-" * 60)
all_files_exist = True

for filename in required_files:
    filepath = os.path.join(current_dir, filename)
    exists = os.path.exists(filepath)
    status = "✓ Found" if exists else "✗ MISSING"
    print(f"{status:12} - {filename}")
    if not exists:
        all_files_exist = False

print("-" * 60)

if all_files_exist:
    print("\n✓ All required files are present!")
    print("\nAttempting to import modules...")
    print("-" * 60)
    
    # Add current directory to path
    sys.path.insert(0, current_dir)
    
    modules = [
        ('data_structures', 'Data Structures'),
        ('query_parser', 'Query Parser'),
        ('database', 'Database Engine'),
        ('database_manager', 'Database Manager'),
        ('gui', 'GUI Module')
    ]
    
    import_success = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {display_name:20} - Imported successfully")
        except Exception as e:
            print(f"✗ {display_name:20} - Error: {str(e)}")
            import_success = False
    
    print("-" * 60)
    
    if import_success:
        print("\n✓ All modules imported successfully!")
        print("\nYou can now run: python main.py")
    else:
        print("\n✗ Some modules failed to import. Check the errors above.")
else:
    print("\n✗ Some required files are missing!")
    print("Please make sure all files are in the same directory.")

print("\n" + "=" * 60)