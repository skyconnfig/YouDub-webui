import os
import sys
import subprocess

def setup_deno_for_ytdlp():
    """Ensure Deno is available for yt-dlp"""
    
    # Possible Deno installation paths
    possible_paths = [
        os.path.expanduser("~/.deno/bin/deno.exe"),
        os.path.expanduser("~/.deno/bin/deno"),
        r"C:\Users\lixin\.deno\bin\deno.exe",
        r"C:\Program Files\deno\deno.exe",
    ]
    
    deno_path = None
    for path in possible_paths:
        if os.path.exists(path):
            deno_path = path
            break
    
    if deno_path:
        print(f"✅ Found Deno at: {deno_path}")
        
        # Add to PATH for current session
        deno_dir = os.path.dirname(deno_path)
        current_path = os.environ.get('PATH', '')
        
        if deno_dir not in current_path:
            os.environ['PATH'] = deno_dir + os.pathsep + current_path
            print(f"✅ Added Deno to PATH: {deno_dir}")
        
        # Set environment variable for yt-dlp
        os.environ['DENO_PATH'] = deno_path
        
        # Verify Deno works
        try:
            result = subprocess.run([deno_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Deno version: {result.stdout.strip()}")
                return True
        except Exception as e:
            print(f"❌ Deno test failed: {e}")
    else:
        print("❌ Deno not found in standard locations")
        print("Please install Deno: irm https://deno.land/install.ps1 | iex")
    
    return False

if __name__ == "__main__":
    setup_deno_for_ytdlp()
    
    # Now run the main app
    print("\n🚀 Starting YouDub-webui...\n")
    os.system("python app.py")
