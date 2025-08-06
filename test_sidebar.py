"""
Simple test to verify sidebar expand/collapse functionality
"""

import streamlit as st

# Page configuration with sidebar
st.set_page_config(
    page_title="Sidebar Test",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS to ensure toggle button works
st.markdown("""
<style>
/* Ensure sidebar toggle is always functional */
[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
    position: fixed !important;
    top: 1rem !important;
    left: 1rem !important;
    background: #2a1f3d !important;
    border: 2px solid #00d4ff !important;
    border-radius: 8px !important;
    color: #00d4ff !important;
    width: 3rem !important;
    height: 3rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
}

[data-testid="collapsedControl"]:hover {
    background: #00d4ff !important;
    color: #1a1625 !important;
    transform: scale(1.05) !important;
}

/* Basic sidebar styling */
.stSidebar {
    background: #1a1625 !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    st.title("🔧 Sidebar Test")
    st.write("This is a test sidebar")
    st.selectbox("Test Select", ["Option 1", "Option 2", "Option 3"])
    st.button("Test Button")
    
    st.markdown("---")
    st.write("**Instructions:**")
    st.write("1. Try clicking the collapse button (arrow) in the top-left")
    st.write("2. When collapsed, click the hamburger menu to expand")
    st.write("3. The sidebar should expand and collapse normally")

# Main content
st.title("Sidebar Functionality Test")
st.write("This is a simple test to verify that the sidebar expand/collapse functionality works correctly.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Test Results")
    if st.button("Test Sidebar State"):
        st.success("✅ Sidebar toggle button should be working!")
        st.info("If you can see this message and the sidebar is working, the fix is successful.")

with col2:
    st.subheader("Troubleshooting")
    st.write("If the sidebar still doesn't work:")
    st.write("1. **Refresh the page** (F5 or Ctrl+R)")
    st.write("2. **Clear browser cache** (Ctrl+Shift+R)")
    st.write("3. **Try a different browser**")
    st.write("4. **Check browser console** for JavaScript errors")

st.markdown("---")
st.write("**Expected Behavior:**")
st.write("- Sidebar should be expanded by default")
st.write("- Clicking the arrow button should collapse the sidebar")
st.write("- When collapsed, a hamburger menu (☰) should appear in the top-left")
st.write("- Clicking the hamburger menu should expand the sidebar again")