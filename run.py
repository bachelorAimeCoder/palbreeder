import sys
import os
from streamlit.web import cli as stcli
import breeding_engine  # Added to ensure PyInstaller bundles the local dependencies

if __name__ == '__main__':
    # PyInstaller crée un dossier temporaire nommé _MEIPASS lors de l'exécution
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    app_path = os.path.join(base_dir, 'app.py')
    
    sys.argv = ["streamlit", "run", app_path, "--server.port=8501", "--server.address=localhost", "--global.developmentMode=false"]
    sys.exit(stcli.main())