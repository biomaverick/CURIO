from __future__ import annotations
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Settings & Logs", page_icon="⚙️", layout="wide")
st.title("Settings & Logs")

# Settings in session_state
settings = st.session_state.setdefault("settings", {})

st.subheader("General Settings")
settings["timeout_seconds"] = st.slider("HTTP Timeout (seconds)", 5, 60, settings.get("timeout_seconds", 20))
settings["retries"] = st.slider("Retry attempts", 0, 5, settings.get("retries", 2))
settings["show_debug"] = st.checkbox("Show debug logs in modules", settings.get("show_debug", False))

st.success("Settings updated")

st.subheader("Logs")
log_path = Path(__file__).resolve().parents[1] / "curio" / "logs" / "curio.log"
if log_path.exists():
    txt = log_path.read_text(encoding="utf-8").splitlines()
    st.code("\n".join(txt[-200:]), language="text")
else:
    st.info("No logs available yet.")