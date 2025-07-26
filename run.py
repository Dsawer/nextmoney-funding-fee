import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    required_packages = [
        'streamlit',
        'plotly', 
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_requirements():
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if requirements_file.exists():
        print("Installing requirements from requirements.txt...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
    else:
        print("requirements.txt not found. Installing packages individually...")
        packages = ['streamlit>=1.28.0', 'plotly>=5.15.0', 'pandas>=2.0.0', 'numpy>=1.24.0']
        for package in packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def run_streamlit_app():
    main_file = Path(__file__).parent / "main.py"
    
    if not main_file.exists():
        print(f"Error: {main_file} not found!")
        print("Make sure all files are in the same directory:")
        print("- main.py")
        print("- config.py") 
        print("- curve_functions.py")
        print("- visualization.py")
        print("- utils.py")
        print("- requirements.txt")
        return False
    
    print(f"Starting Streamlit app: {main_file}")
    print("The app will open in your default web browser...")
    print("Press Ctrl+C to stop the server.")
    print("-" * 50)
    
    try:
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(main_file),
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\nStreamlit server stopped.")
    except FileNotFoundError:
        print("Error: Streamlit not found. Please install it first.")
        return False
    
    return True

def main():
    """Ana fonksiyon"""
    print("=" * 60)
    print("Funding Fee System - Style Calculator")
    print("=" * 60)
    
    
    required_files = [
        "main.py",
        "config.py", 
        "curve_functions.py",
        "visualization.py",
        "utils.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("Error: Missing required files:")
        for file in missing_files:
            print(f"- {file}")
        print("\nPlease make sure all files are in the same directory.")
        return
    
    
    missing_packages = check_requirements()
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        install_choice = input("Do you want to install them? (y/n): ").lower().strip()
        
        if install_choice in ['y', 'yes']:
            try:
                install_requirements()
                print("Requirements installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Error installing requirements: {e}")
                print("Please install them manually:")
                print("pip install streamlit plotly pandas numpy")
                return
        else:
            print("Cannot proceed without required packages.")
            return
    
    
    success = run_streamlit_app()
    
    if not success:
        print("\nFailed to start the application.")
        print("Try running manually:")
        print("streamlit run main.py")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("\nTry running the app manually with:")
        print("streamlit run main.py")