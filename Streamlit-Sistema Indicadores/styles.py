"""
Custom CSS styles for modern card-based UI
"""

def get_custom_css():
    """Return custom CSS for the application"""
    return """
    <style>
    /* Global styles */
    .main {
        padding: 2rem;
    }
    
    /* Card container */
    .card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
    }
    
    .card-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: #1f1f1f;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 0.75rem;
    }
    
    /* Form styling */
    .stForm {
        background: transparent;
        border: none;
        padding: 0;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #d0d0d0;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 500;
        color: #666;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-por-comenzar {
        background: #E3F2FD;
        color: #1976D2;
    }
    
    .status-en-progreso {
        background: #FFF3E0;
        color: #F57C00;
    }
    
    .status-completado {
        background: #E8F5E9;
        color: #388E3C;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Data table */
    .dataframe {
        border: none !important;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-weight: 600;
        padding: 1rem;
        text-align: left;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background: #f8f9fa;
    }
    
    .dataframe tbody tr:hover {
        background: #e9ecef;
    }
    
    .dataframe tbody tr td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e0e0e0;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: #E8F5E9;
        border-left: 4px solid #4CAF50;
        border-radius: 4px;
        padding: 1rem;
    }
    
    .stError {
        background: #FFEBEE;
        border-left: 4px solid #F44336;
        border-radius: 4px;
        padding: 1rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Spacing utilities */
    .mt-1 { margin-top: 0.5rem; }
    .mt-2 { margin-top: 1rem; }
    .mt-3 { margin-top: 1.5rem; }
    .mb-1 { margin-bottom: 0.5rem; }
    .mb-2 { margin-bottom: 1rem; }
    .mb-3 { margin-bottom: 1.5rem; }
    </style>
    """


def get_status_badge(estado: str) -> str:
    """
    Generate HTML for status badge
    
    Args:
        estado: Status string
    
    Returns:
        HTML string for badge
    """
    status_class = {
        "Por comenzar": "status-por-comenzar",
        "En progreso": "status-en-progreso",
        "Completado": "status-completado"
    }
    
    emoji = {
        "Por comenzar": "🔵",
        "En progreso": "🟡",
        "Completado": "🟢"
    }
    
    css_class = status_class.get(estado, "status-por-comenzar")
    icon = emoji.get(estado, "⚪")
    
    return f'<span class="status-badge {css_class}">{icon} {estado}</span>'


def get_progress_bar(avance: int) -> str:
    """
    Generate HTML for progress bar
    
    Args:
        avance: Progress percentage (0-100)
    
    Returns:
        HTML string for progress bar
    """
    color = "#1976D2" if avance < 30 else "#F57C00" if avance < 100 else "#388E3C"
    
    return f"""
    <div style="background: #e0e0e0; border-radius: 8px; height: 24px; overflow: hidden;">
        <div style="background: {color}; width: {avance}%; height: 100%; 
                    display: flex; align-items: center; justify-content: center;
                    color: white; font-weight: 600; font-size: 0.85rem;
                    transition: width 0.3s ease;">
            {avance}%
        </div>
    </div>
    """
