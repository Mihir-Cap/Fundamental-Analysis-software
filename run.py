import subprocess

def run_script(file_name):
    try:
        print(f"Running {file_name}...")
        result = subprocess.run(['python', file_name], capture_output=True, text=True)
        print(f"Output of {file_name}:\n{result.stdout}")
        if result.stderr:
            print(f"Error in {file_name}:\n{result.stderr}")
    except Exception as e:
        print(f"Failed to run {file_name}: {e}")

def main():
    # Specify the names of the Python files to run
    file1 = 'main.py'
    file2 = 'swingtrading.py'

    # Run the scripts
    run_script(file2)
    run_script(file1)

if __name__ == "__main__":
    main()
