import os
import sys

if __name__ == "__main__":
    try:
        from streamlit.web import cli as stcli
    except ImportError:
        import streamlit.cli as stcli

    sys.argv = ["streamlit", "run", "app.py"]
    sys.exit(stcli.main())
