"""
Lance l'application Streamlit.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Lance Streamlit."""
    app_path = Path(__file__).parent / "frontend" / "streamlit_app.py"
    
    print("🚀 Démarrage de l'Assistant INSA HdF...")
    print("📍 URL: http://localhost:8501")
    print("\nAppuie sur Ctrl+C pour arrêter.\n")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false"
    ])


if __name__ == "__main__":
    main()