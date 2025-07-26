# app.py - Streamlit Cloud entry point
"""
Streamlit Cloud için ana giriş dosyası
Bu dosya run.py'deki port yönetimi olmadan direkt main.py'yi çalıştırır
"""

# main.py'yi direkt import et ve çalıştır
from main import main

if __name__ == "__main__":
    main()