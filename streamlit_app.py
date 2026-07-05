"""Entry point for Streamlit Community Cloud.

When deploying at https://share.streamlit.io, set the "Main file path" to `streamlit_app.py`.
Dependencies come from `requirements.txt` (the published `divvy-backtest[ui]` package).
"""

from divvy.ui import render

render()
