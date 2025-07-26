# run_simple.py - Simplified Streamlit launcher
import sys
import os
import subprocess
import time

def main():
    """Simple launcher without complex port handling"""
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Starting Streamlit application...")
    
    try:
        # Simple approach - just run streamlit directly
        result = subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'main.py',
            '--server.headless=true',
            '--browser.gatherUsageStats=false'
        ], check=False)
        
        print(f"Streamlit exited with code: {result.returncode}")
        
    except KeyboardInterrupt:
        print("\n🛑 Streamlit stopped by user")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        print("💡 Try running: streamlit run main.py")

if __name__ == "__main__":
    main()