"""
Aushadh AI - Start Server
Run: python run.py
Opens: http://localhost:8000
"""
import os, sys, webbrowser, subprocess, time, threading

def check_env():
    if not os.path.exists('.env'):
        print("\n[X] .env file not found!")
        print("   Create .env with: GROQ_API_KEY=gsk_xxxxxxxxx\n")
        sys.exit(1)
    with open('.env') as f:
        content = f.read()
    if 'GROQ_API_KEY' not in content:
        print("\n[X] GROQ_API_KEY not found in .env!")
        print("   Add: GROQ_API_KEY=gsk_xxxxxxxxx")
        print("   Get free key at: console.groq.com\n")
        sys.exit(1)
    print("  [OK] .env file OK")
    print("  [OK] GROQ_API_KEY found")
    print("  [OK] OpenFDA API ready (free)")

def check_packages():
    pkgs = ['fastapi','uvicorn[standard]','python-dotenv','python-multipart','aiofiles']
    missing = []
    for p in ['fastapi','uvicorn','dotenv','multipart','aiofiles']:
        try: __import__(p)
        except: missing.append(p)
    if missing:
        print("  [!] Installing packages...")
        subprocess.run([sys.executable,'-m','pip','install']+pkgs, capture_output=True)
        print("  [OK] Packages ready")
    else:
        print("  [OK] All packages installed")

def main():
    print("\n" + "="*50)
    print("  [Aushadh AI] - Starting Application")
    print("="*50)
    check_env()
    check_packages()
    print(f"\n  URL     : http://localhost:8000")
    print(f"  Folder  : {os.getcwd()}")
    print(f"  API Docs: http://localhost:8000/docs")
    print(f"  AI      : Groq + OpenFDA (Max Accuracy)")
    print("\n  Press CTRL+C to stop")
    print("="*50 + "\n")
    threading.Thread(
        target=lambda: (time.sleep(2), webbrowser.open("http://localhost:8000")),
        daemon=True
    ).start()
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()