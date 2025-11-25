import streamlit as st
import streamlit.components.v1 as components
import json
import os
from datetime import datetime, timedelta
import re
import html
import smtplib
import ssl
from email.message import EmailMessage

from admin_portal import admin_dashboard
from program_catalog import PROGRAM_CATEGORIES, all_programmes, programme_category
from security_utils import ensure_password_fields, hash_password, verify_password

# Page config
st.set_page_config(
    page_title="BookFlow - Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional Theme
st.markdown("""
<style>
    /* Main App Styling */
    .stApp {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
        color: #ffffff;
    }
    
    html, body {
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    [data-testid="stAppViewContainer"] > .main .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    [data-testid="stAppViewContainer"] > .main .block-container > *:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Global text color */
    .stMarkdown, .stText, p, span, div {
        color: #e0e0e0 !important;
    }
    
    /* Headers */
    .main-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #6C0345;
        text-align: center;
        padding: 0.5rem 0.3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #6C0345 0%, #DC143C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-header {
        font-size: 0.85rem;
        font-weight: 500;
        color: #F7C566;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Cards */
    .book-card {
        background: #1e1e1e;
        padding: 0.8rem;
        border-radius: 10px;
        border-left: 4px solid #6C0345;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .book-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(108, 3, 69, 0.4);
        background: #252525;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #6C0345 0%, #DC143C 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(108, 3, 69, 0.3);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: scale(1.03);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #6C0345 0%, #DC143C 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(108, 3, 69, 0.3);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 1px solid #444444;
        padding: 0.5rem;
        transition: border-color 0.3s ease;
        background: #2a2a2a !important;
        color: #ffffff !important;
        font-size: 0.9rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #6C0345;
        box-shadow: 0 0 0 2px rgba(108, 3, 69, 0.3);
    }
    
    /* Labels */
    .stTextInput>label, .stSelectbox>label, .stRadio>label {
        color: #ffffff !important;
    }
    
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%) !important;
        border-right: 2px solid #6C0345;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Success/Error/Info Boxes */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 2px solid #28a745;
        border-radius: 10px;
        color: #155724;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(40, 167, 69, 0.1);
    }
    
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 2px solid #dc3545;
        border-radius: 10px;
        color: #721c24;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(220, 53, 69, 0.1);
    }
    
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 2px solid #17a2b8;
        border-radius: 10px;
        color: #0c5460;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(23, 162, 184, 0.1);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 2px solid #ffc107;
        border-radius: 10px;
        color: #856404;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(255, 193, 7, 0.1);
    }
    
    /* Metrics */
    .stMetric {
        background: #1e1e1e;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        border: 1px solid #333333;
    }
    
    .stMetric label {
        color: #b0b0b0 !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        background: #1e1e1e;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #2a2a2a;
        border-radius: 10px;
        font-weight: 600;
        color: #ffffff !important;
        border: 1px solid #444444;
    }
    
    .streamlit-expanderContent {
        background: #1e1e1e;
        border: 1px solid #444444;
        border-top: none;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #2a2a2a;
        border-radius: 10px 10px 0 0;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        color: #b0b0b0;
        border: 1px solid #444444;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #333333;
        color: #ffffff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6C0345 0%, #DC143C 100%);
        color: white !important;
        border: 1px solid #6C0345;
    }
    
    /* Tab content */
    .stTabs [data-baseweb="tab-panel"] {
        background: transparent;
        padding-top: 1rem;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #6C0345, transparent);
    }
    
    /* Container */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Radio Buttons */
    .stRadio > label {
        font-weight: 600;
        color: #ffffff !important;
    }
    
    .stRadio [role="radiogroup"] {
        background: #2a2a2a;
        padding: 0.5rem;
        border-radius: 10px;
        border: 1px solid #444444;
    }
    
    .stRadio [data-baseweb="radio"] {
        background: #2a2a2a;
    }
    
    /* Selectbox */
    .stSelectbox > label {
        font-weight: 600;
        color: #ffffff !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background: #2a2a2a !important;
    }
    
    /* Containers */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background: transparent;
    }
    
    /* Column containers */
    [data-testid="column"] {
        background: transparent;
    }
    
    /* ===== MOBILE RESPONSIVE ===== */
    @media (max-width: 768px) {
        /* Headers */
        .main-header {
            font-size: 2rem !important;
            padding: 1rem 0.5rem !important;
        }
        
        .sub-header {
            font-size: 1.2rem !important;
        }
        
        /* Buttons */
        .stButton>button {
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
        }
        
        /* Cards */
        .book-card {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .stat-card {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Input Fields */
        .stTextInput>div>div>input {
            padding: 0.5rem !important;
            font-size: 0.9rem !important;
        }
        
        /* Metrics */
        .stMetric {
            padding: 0.5rem !important;
        }
        
        /* Columns - Stack on mobile */
        .row-widget.stHorizontal {
            flex-direction: column !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            font-size: 0.9rem !important;
            padding: 0.5rem !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
        }
        
        /* Sidebar */
        .css-1d391kg {
            padding: 1rem 0.5rem !important;
        }
        
        /* Container spacing */
        .element-container {
            margin-bottom: 0.5rem !important;
        }
        
        /* Radio buttons */
        .stRadio > div {
            flex-direction: column !important;
        }
        
        /* Success/Error boxes */
        .success-box, .error-box, .info-box, .warning-box {
            padding: 1rem !important;
            font-size: 0.9rem !important;
        }
    }
    
    /* Small Mobile (< 480px) */
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.5rem !important;
        }
        
        .sub-header {
            font-size: 1rem !important;
        }
        
        .stButton>button {
            padding: 0.4rem 0.8rem !important;
            font-size: 0.85rem !important;
        }
        
        /* Hide some decorative elements on very small screens */
        .book-card:hover {
            transform: none !important;
        }
    }
    
    /* Tablet (768px - 1024px) */
    @media (min-width: 768px) and (max-width: 1024px) {
        .main-header {
            font-size: 2.5rem !important;
        }
        
        .sub-header {
            font-size: 1.5rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)


def _celebration_gif():
    st.markdown(
        """
        <div style='text-align: center; margin: 1.5rem 0;'>
            <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTNhbHp6YmprMXk0cHB4cnMwdTZ4dmZqZTFwMGZ3ZWVuamFtdnp6aiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/paTz7UZbPfTZFRYnnB/giphy.gif"
                 alt="Celebration" style='max-width: 220px; width: 50%; border-radius: 12px;'>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _login_intro_animation():
    st.markdown(
        """
        <div style='display: flex; justify-content: center; margin: 1rem 0 1.5rem 0;'>
            <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbjhlY21hc3A5dmw4MnZyeHBkMG5sbnBmZmVscHluZG1pNW9ldXR2cCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/oYQT3hGrp3DiGuTEFD/giphy.gif"
                 alt="Library animation"
                 style='max-width: 320px; width: 80%; border-radius: 14px; box-shadow: 0 6px 18px rgba(0,0,0,0.25);'>
        </div>
        """,
        unsafe_allow_html=True,
    )

DEFAULT_CATEGORY_BOOKS = {
    "Artificial Intelligence": [
        {
            "id": "AI001",
            "title": "Machine Learning Yearning",
            "author": "Andrew Ng",
            "copies": 6,
            "subject": "Artificial Intelligence",
            "pdf_url": "https://assets.anaconda.com/production/uploads/Machine-Learning-Yearning-Andrew-Ng.pdf",
        },
        {
            "id": "AI002",
            "title": "CS229 Lecture Notes",
            "author": "Stanford University",
            "copies": 5,
            "subject": "Artificial Intelligence",
            "pdf_url": "https://cs229.stanford.edu/main_notes.pdf",
        },
        {
            "id": "AI003",
            "title": "Reinforcement Learning: An Introduction",
            "author": "Richard S. Sutton & Andrew G. Barto",
            "copies": 4,
            "subject": "Artificial Intelligence",
            "pdf_url": "http://incompleteideas.net/book/RLbook2020.pdf",
        },
        {
            "id": "AI004",
            "title": "Dive into Deep Learning",
            "author": "Aston Zhang et al.",
            "copies": 5,
            "subject": "Artificial Intelligence",
            "pdf_url": "https://d2l.ai/d2l-en.pdf",
        },
        {
            "id": "AI005",
            "title": "Understanding Machine Learning",
            "author": "Shai Shalev-Shwartz & Shai Ben-David",
            "copies": 4,
            "subject": "Artificial Intelligence",
            "pdf_url": "https://www.cs.huji.ac.il/~shais/UnderstandingMachineLearning/understanding-machine-learning-theory-algorithms.pdf",
        },
        {
            "id": "AI006",
            "title": "Bayesian Reasoning and Machine Learning",
            "author": "David Barber",
            "copies": 4,
            "subject": "Artificial Intelligence",
            "pdf_url": "http://web4.cs.ucl.ac.uk/staff/D.Barber/textbook/031013.pdf",
        },
    ],
    "Engineering": [
        {
            "id": "ENG001",
            "title": "Engineering Mechanics: Statics",
            "author": "OpenStax",
            "copies": 5,
            "subject": "Physics",
            "pdf_url": "https://openstax.org/resources/engineering-mechanics-statics.pdf",
        },
        {
            "id": "ENG002",
            "title": "Engineering Mechanics: Dynamics",
            "author": "OpenStax",
            "copies": 5,
            "subject": "Physics",
            "pdf_url": "https://openstax.org/resources/engineering-mechanics-dynamics.pdf",
        },
        {
            "id": "ENG003",
            "title": "University Physics Volume 1",
            "author": "Samuel J. Ling et al.",
            "copies": 6,
            "subject": "Physics",
            "pdf_url": "https://openstax.org/resources/university-physics-volume-1.pdf",
        },
        {
            "id": "ENG004",
            "title": "University Physics Volume 2",
            "author": "Samuel J. Ling et al.",
            "copies": 6,
            "subject": "Physics",
            "pdf_url": "https://openstax.org/resources/university-physics-volume-2.pdf",
        },
        {
            "id": "ENG005",
            "title": "University Physics Volume 3",
            "author": "Samuel J. Ling et al.",
            "copies": 6,
            "subject": "Physics",
            "pdf_url": "https://openstax.org/resources/university-physics-volume-3.pdf",
        },
        {
            "id": "ENG006",
            "title": "Calculus Volume 2",
            "author": "Gilbert Strang & Edwin 'Jed' Herman",
            "copies": 5,
            "subject": "Mathematics",
            "pdf_url": "https://openstax.org/resources/calculus-volume-2.pdf",
        },
    ],
    "Liberal Arts": [
        {
            "id": "ART001",
            "title": "The Republic",
            "author": "Plato",
            "copies": 3,
            "subject": "Liberal Arts",
            "pdf_url": "https://www.gutenberg.org/files/1497/1497-pdf.pdf",
        },
        {
            "id": "ART002",
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "copies": 3,
            "subject": "Liberal Arts",
            "pdf_url": "https://www.gutenberg.org/files/1342/1342-pdf.pdf",
        },
        {
            "id": "ART003",
            "title": "Meditations",
            "author": "Marcus Aurelius",
            "copies": 3,
            "subject": "Liberal Arts",
            "pdf_url": "https://www.gutenberg.org/files/2680/2680-pdf.pdf",
        },
        {
            "id": "ART004",
            "title": "The Souls of Black Folk",
            "author": "W. E. B. Du Bois",
            "copies": 3,
            "subject": "Liberal Arts",
            "pdf_url": "https://www.gutenberg.org/files/408/408-pdf.pdf",
        },
        {
            "id": "ART005",
            "title": "Utopia",
            "author": "Thomas More",
            "copies": 3,
            "subject": "Liberal Arts",
            "pdf_url": "https://www.gutenberg.org/files/2130/2130-pdf.pdf",
        },
        {
            "id": "ART006",
            "title": "The Communist Manifesto",
            "author": "Karl Marx & Friedrich Engels",
            "copies": 3,
            "subject": "Liberal Arts",
            "pdf_url": "https://www.gutenberg.org/files/61/61-pdf.pdf",
        },
    ],
    "Design": [
        {
            "id": "DES001",
            "title": "Graphic Design and Print Production Fundamentals",
            "author": "BCcampus OpenEd",
            "copies": 4,
            "subject": "Design",
            "pdf_url": "https://opentextbc.ca/graphicdesign/wp-content/uploads/sites/153/2014/10/Graphic-Design-and-Print-Production-Fundamentals-1534799288.pdf",
        },
        {
            "id": "DES002",
            "title": "Design Thinking (2nd Edition)",
            "author": "Open School BC",
            "copies": 4,
            "subject": "Design",
            "pdf_url": "https://opentextbc.ca/designthinking/wp-content/uploads/sites/435/2022/05/Design-Thinking-2nd-Edition-1652302589.pdf",
        },
        {
            "id": "DES003",
            "title": "Apple Human Interface Guidelines",
            "author": "Apple Inc.",
            "copies": 4,
            "subject": "Design",
            "pdf_url": "https://developer.apple.com/design/human-interface-guidelines/downloads/Apple-Human-Interface-Guidelines.pdf",
        },
        {
            "id": "DES004",
            "title": "Material Design Guidelines",
            "author": "Google LLC",
            "copies": 4,
            "subject": "Design",
            "pdf_url": "https://storage.googleapis.com/spec-host/mio-material-cms/prod/7a5cbe3a9ec264e0404664cc645c9e6c.pdf",
        },
        {
            "id": "DES005",
            "title": "Universal Design New York",
            "author": "NYC Department of Design & Construction",
            "copies": 4,
            "subject": "Design",
            "pdf_url": "https://www1.nyc.gov/assets/ddc/downloads/publications/design/ddcdd/universal.pdf",
        },
        {
            "id": "DES006",
            "title": "WCAG 2.1 Quick Reference",
            "author": "W3C Web Accessibility Initiative",
            "copies": 4,
            "subject": "Design",
            "pdf_url": "https://www.w3.org/WAI/WCAG21/quickref/wcag2.1.pdf",
        },
    ],
    "Management": [
        {
            "id": "MGT001",
            "title": "Principles of Management (3e)",
            "author": "OpenStax",
            "copies": 4,
            "subject": "Management",
            "pdf_url": "https://openstax.org/resources/principles-of-management-3e.pdf",
        },
        {
            "id": "MGT002",
            "title": "Organizational Behavior (3e)",
            "author": "OpenStax",
            "copies": 4,
            "subject": "Management",
            "pdf_url": "https://openstax.org/resources/organizational-behavior-3e.pdf",
        },
        {
            "id": "MGT003",
            "title": "Principles of Marketing (3e)",
            "author": "OpenStax",
            "copies": 4,
            "subject": "Management",
            "pdf_url": "https://openstax.org/resources/principles-of-marketing-3e.pdf",
        },
        {
            "id": "MGT004",
            "title": "Business Ethics (2e)",
            "author": "OpenStax",
            "copies": 4,
            "subject": "Management",
            "pdf_url": "https://openstax.org/resources/business-ethics-2e.pdf",
        },
        {
            "id": "MGT005",
            "title": "Entrepreneurship",
            "author": "OpenStax",
            "copies": 4,
            "subject": "Management",
            "pdf_url": "https://openstax.org/resources/entrepreneurship.pdf",
        },
        {
            "id": "MGT006",
            "title": "Accounting Principles",
            "author": "OpenStax",
            "copies": 4,
            "subject": "Management",
            "pdf_url": "https://openstax.org/resources/accounting-principles.pdf",
        },
    ],
    "Media": [
        {
            "id": "MED001",
            "title": "Understanding Media and Culture",
            "author": "University of Minnesota Libraries",
            "copies": 3,
            "subject": "Media Studies",
            "pdf_url": "https://open.lib.umn.edu/understandingmediaandculture/wp-content/uploads/sites/7/2016/05/Understanding-Media-and-Culture-1543285821.pdf",
        },
        {
            "id": "MED002",
            "title": "Media Studies 101",
            "author": "University of People Press",
            "copies": 3,
            "subject": "Media Studies",
            "pdf_url": "https://opentextbc.ca/mediastudies101/wp-content/uploads/sites/142/2015/06/Media-Studies-101.pdf",
        },
        {
            "id": "MED003",
            "title": "Public Relations",
            "author": "University of Minnesota Libraries",
            "copies": 3,
            "subject": "Media Studies",
            "pdf_url": "https://open.lib.umn.edu/publicrelations/wp-content/uploads/sites/24/2018/10/Public-Relations-1538065239.pdf",
        },
        {
            "id": "MED004",
            "title": "Writing for Strategic Communication Industries",
            "author": "Heidi Everett",
            "copies": 3,
            "subject": "Media Studies",
            "pdf_url": "https://open.lib.umn.edu/writingforscmedia/wp-content/uploads/sites/14/2018/10/Writing-for-Strategic-Communication-Industries-1538065247.pdf",
        },
        {
            "id": "MED005",
            "title": "Digital Marketing",
            "author": "BCcampus OpenEd",
            "copies": 3,
            "subject": "Media Studies",
            "pdf_url": "https://opentextbc.ca/digitalmarketing/wp-content/uploads/sites/201/2019/01/Digital-Marketing-1539290539.pdf",
        },
        {
            "id": "MED006",
            "title": "Communication in the Real World",
            "author": "University of Minnesota Libraries",
            "copies": 3,
            "subject": "Media Studies",
            "pdf_url": "https://open.lib.umn.edu/communicationinhealthcare/wp-content/uploads/sites/389/2020/08/Communication-in-the-Real-World-An-Introduction-to-Communication-Studies-1598372555.pdf",
        },
    ],
    "Law": [
        {
            "id": "LAW001",
            "title": "Constitution of India (Bare Act)",
            "author": "Government of India",
            "copies": 4,
            "subject": "Law",
            "pdf_url": "https://legislative.gov.in/sites/default/files/COI_ENG.pdf",
        },
        {
            "id": "LAW002",
            "title": "Code of Criminal Procedure, 1973",
            "author": "Government of India",
            "copies": 4,
            "subject": "Law",
            "pdf_url": "https://legislative.gov.in/sites/default/files/A1974-02.pdf",
        },
        {
            "id": "LAW003",
            "title": "Code of Civil Procedure, 1908",
            "author": "Government of India",
            "copies": 4,
            "subject": "Law",
            "pdf_url": "https://legislative.gov.in/sites/default/files/A1908-05.pdf",
        },
        {
            "id": "LAW004",
            "title": "Indian Evidence Act, 1872",
            "author": "Government of India",
            "copies": 4,
            "subject": "Law",
            "pdf_url": "https://legislative.gov.in/sites/default/files/A1872-01.pdf",
        },
        {
            "id": "LAW005",
            "title": "Indian Contract Act, 1872",
            "author": "Government of India",
            "copies": 4,
            "subject": "Law",
            "pdf_url": "https://legislative.gov.in/sites/default/files/A1872-09.pdf",
        },
        {
            "id": "LAW006",
            "title": "Legal Research Methodology",
            "author": "Institute of Company Secretaries of India",
            "copies": 4,
            "subject": "Law",
            "pdf_url": "https://www.icsi.edu/media/webmodules/publications/Legal_Research_Methodology.pdf",
        },
    ],
    "Classic Literature": [
        {
            "id": "GEN001",
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "copies": 4,
            "subject": "Classic Literature",
            "pdf_url": "https://www.gutenberg.org/files/1342/1342-pdf.pdf",
        },
        {
            "id": "GEN002",
            "title": "Crime and Punishment",
            "author": "Fyodor Dostoevsky",
            "copies": 4,
            "subject": "Classic Literature",
            "pdf_url": "https://www.gutenberg.org/files/2554/2554-pdf.pdf",
        },
        {
            "id": "GEN003",
            "title": "War and Peace",
            "author": "Leo Tolstoy",
            "copies": 4,
            "subject": "Classic Literature",
            "pdf_url": "https://www.gutenberg.org/files/2600/2600-pdf.pdf",
        },
        {
            "id": "GEN004",
            "title": "A Tale of Two Cities",
            "author": "Charles Dickens",
            "copies": 4,
            "subject": "Classic Literature",
            "pdf_url": "https://www.gutenberg.org/files/98/98-pdf.pdf",
        },
    ],
    "Fiction": [
        {
            "id": "FIC001",
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "format": "Novel",
            "copies": 4,
            "subject": "Fiction",
            "borrowable": True,
            "pdf_url": "https://www.gutenberg.org/cache/epub/64317/pg64317-images.html",
        },
        {
            "id": "FIC002",
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "format": "Novel",
            "copies": 4,
            "subject": "Fiction",
            "borrowable": True,
            "pdf_url": "https://raw.githubusercontent.com/benoitvallon/100-best-books/master/the-great-gatsby.pdf",
        },
        {
            "id": "FIC003",
            "title": "The Catcher in the Rye",
            "author": "J.D. Salinger",
            "format": "Novel",
            "copies": 3,
            "subject": "Fiction",
            "borrowable": True,
            "pdf_url": "https://www.gutenberg.org/files/5958/5958-pdf.pdf",
        },
    ],
    "Science Fiction": [
        {
            "id": "SCI001",
            "title": "Dune",
            "author": "Frank Herbert",
            "format": "Science Fiction",
            "copies": 3,
            "subject": "Science Fiction",
            "borrowable": True,
            "pdf_url": "https://archive.org/download/dune-frank-herbert/Dune%20-%20Frank%20Herbert.pdf",
        },
        {
            "id": "SCI002",
            "title": "The Time Machine",
            "author": "H. G. Wells",
            "format": "Science Fiction",
            "copies": 3,
            "subject": "Science Fiction",
            "borrowable": True,
            "pdf_url": "https://www.gutenberg.org/files/35/35-pdf.pdf",
        },
        {
            "id": "SCI003",
            "title": "Foundation",
            "author": "Isaac Asimov",
            "format": "Science Fiction",
            "copies": 3,
            "subject": "Science Fiction",
            "borrowable": True,
            "pdf_url": "https://archive.org/download/Foundation_20210101/Foundation.pdf",
        },
    ],
    "Magazines": [
        {
            "id": "MAG001",
            "title": "National Geographic – November 2025",
            "author": "National Geographic Society",
            "format": "Monthly Magazine",
            "subject": "Magazines",
            "borrowable": False,
            "issue_date": "November 2025",
            "copies": 2,
            "pdf_url": "https://www.nationalgeographic.com/magazine/2025/11/national-geographic-november-2025.pdf",
        },
        {
            "id": "MAG002",
            "title": "Scientific American – AI Special",
            "author": "Springer Nature",
            "format": "Monthly Magazine",
            "subject": "Magazines",
            "borrowable": False,
            "issue_date": "October 2025",
            "copies": 2,
            "pdf_url": "https://www.scientificamerican.com/media/pdf/ai-special-issue-2025.pdf",
        },
    ],
    "Catalogues": [
        {
            "id": "CAT001",
            "title": "IKEA Furniture Catalogue 2025",
            "author": "IKEA Communications",
            "format": "Digital Catalogue",
            "subject": "Catalogues",
            "borrowable": False,
            "issue_date": "2025",
            "copies": 1,
            "pdf_url": "https://catalogue.ikea.com/2025/ikea-catalogue-2025.pdf",
        },
        {
            "id": "CAT002",
            "title": "Apple Product Lineup Guide",
            "author": "Apple Inc.",
            "format": "Product Catalogue",
            "subject": "Catalogues",
            "borrowable": False,
            "issue_date": "Fall 2025",
            "copies": 1,
            "pdf_url": "https://www.apple.com/newsroom/pdfs/product-guide-fall-2025.pdf",
        },
    ],
    "Reference": [
        {
            "id": "ENC001",
            "title": "Encyclopaedia Britannica – Science & Technology",
            "author": "Britannica Group",
            "format": "Reference",
            "subject": "Reference",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://www.britannica.com/summary/science-summary.pdf",
        },
        {
            "id": "ENC002",
            "title": "World Book Encyclopaedia – Human Geography",
            "author": "World Book, Inc.",
            "format": "Reference",
            "subject": "Reference",
            "copies": 2,
            "borrowable": True,
            "pdf_url": "https://static.worldbook.com/reference/human-geography.pdf",
        },
        {
            "id": "ENC003",
            "title": "Oxford Encyclopaedia of World History",
            "author": "Oxford University Press",
            "format": "Reference",
            "subject": "Reference",
            "copies": 2,
            "borrowable": True,
            "pdf_url": "https://global.oup.com/example/world-history-encyclopedia.pdf",
        },
    ],
    "Newspapers": [
        {
            "id": "NEWS001",
            "title": "The Guardian – Morning Edition",
            "author": "Guardian News & Media",
            "format": "Daily Newspaper",
            "subject": "Newspapers",
            "borrowable": False,
            "issue_date": "12 Nov 2025",
            "copies": 1,
            "pdf_url": "https://static.guim.co.uk/2025/11/12/TheGuardian-MorningEdition.pdf",
        },
        {
            "id": "NEWS002",
            "title": "The New York Times – International",
            "author": "The New York Times Company",
            "format": "Daily Newspaper",
            "subject": "Newspapers",
            "borrowable": False,
            "issue_date": "12 Nov 2025",
            "copies": 1,
            "pdf_url": "https://static.nytimes.com/2025/11/12/international-print.pdf",
        },
    ],
    "STEM": [
        {
            "id": "STM001",
            "title": "Advanced Engineering Mathematics",
            "author": "Erwin Kreyszig",
            "format": "Mathematics",
            "subject": "Mathematics",
            "copies": 5,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/AdvancedEngineeringMathematics10thEdition/Erwin%20Kreyszig%20-%20Advanced%20Engineering%20Mathematics%2010th%20Edition.pdf",
        },
        {
            "id": "STM002",
            "title": "Fundamentals of Physics",
            "author": "Halliday, Resnick & Walker",
            "format": "Physics",
            "subject": "Physics",
            "copies": 5,
            "borrowable": True,
            "pdf_url": "https://www.academia.edu/34840860/Fundamentals_of_Physics_10th_Edition",
        },
        {
            "id": "STM003",
            "title": "Organic Chemistry Essentials",
            "author": "Paula Yurkanis Bruice",
            "format": "Chemistry",
            "subject": "Chemistry",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/organic-chemistry-8th-edition-by-paula-yurkanis-bruice/Organic%20Chemistry%208th%20Edition%20by%20Paula%20Yurkanis%20Bruice.pdf",
        },
        {
            "id": "STM004",
            "title": "Biology for Engineers",
            "author": "Arthur T. Johnson",
            "format": "Biology",
            "subject": "Biology",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://ocw.mit.edu/courses/20-010j-introduction-to-bioengineering-be-introductory-biology-spring-2006/7c2438afec889d3a5eb0213b04fc3c0f_lecturenotes.pdf",
        },
        {
            "id": "CHM001",
            "title": "General Chemistry: Principles and Modern Applications",
            "author": "Ralph H. Petrucci et al.",
            "format": "Chemistry",
            "subject": "Chemistry",
            "copies": 5,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/general-chemistry-principles-and-modern-applications/General%20Chemistry%20Principles%20and%20Modern%20Applications.pdf",
        },
        {
            "id": "CHM002",
            "title": "Inorganic Chemistry",
            "author": "Mark Weller et al.",
            "format": "Chemistry",
            "subject": "Chemistry",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/inorganic-chemistry-6th-edition/Inorganic%20Chemistry%206th%20Edition.pdf",
        },
        {
            "id": "CHM003",
            "title": "Physical Chemistry",
            "author": "Atkins & de Paula",
            "format": "Chemistry",
            "subject": "Chemistry",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/physical-chemistry-10th-edition/Physical%20Chemistry%2010th%20Edition.pdf",
        },
        {
            "id": "CHM004",
            "title": "Analytical Chemistry",
            "author": "Douglas A. Skoog et al.",
            "format": "Chemistry",
            "subject": "Chemistry",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/analytical-chemistry-9th-edition/Analytical%20Chemistry%209th%20Edition.pdf",
        },
        {
            "id": "BIO001",
            "title": "Molecular Biology of the Cell",
            "author": "Bruce Alberts et al.",
            "format": "Biology",
            "subject": "Biology",
            "copies": 5,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/molecular-biology-of-the-cell-6th-edition/Molecular%20Biology%20of%20the%20Cell%206th%20Edition.pdf",
        },
        {
            "id": "BIO002",
            "title": "Campbell Biology",
            "author": "Jane B. Reece et al.",
            "format": "Biology",
            "subject": "Biology",
            "copies": 5,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/campbell-biology-12th-edition/Campbell%20Biology%2012th%20Edition.pdf",
        },
        {
            "id": "BIO003",
            "title": "Human Anatomy and Physiology",
            "author": "Elaine N. Marieb & Katja Hoehn",
            "format": "Biology",
            "subject": "Biology",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/human-anatomy-and-physiology-11th-edition/Human%20Anatomy%20and%20Physiology%2011th%20Edition.pdf",
        },
        {
            "id": "BIO004",
            "title": "Genetics: Analysis and Principles",
            "author": "Robert J. Brooker",
            "format": "Biology",
            "subject": "Biology",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/genetics-analysis-and-principles-6th-edition/Genetics%20Analysis%20and%20Principles%206th%20Edition.pdf",
        },
        {
            "id": "BIO005",
            "title": "Ecology: From Individuals to Ecosystems",
            "author": "Michael Begon et al.",
            "format": "Biology",
            "subject": "Biology",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/ecology-from-individuals-to-ecosystems-5th-edition/Ecology%20From%20Individuals%20to%20Ecosystems%205th%20Edition.pdf",
        },
        {
            "id": "BIO006",
            "title": "Microbiology: An Evolving Science",
            "author": "Joan L. Slonczewski & John W. Foster",
            "format": "Biology",
            "subject": "Biology",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/microbiology-an-evolving-science-4th-edition/Microbiology%20An%20Evolving%20Science%204th%20Edition.pdf",
        },
        {
            "id": "PHY001",
            "title": "Classical Mechanics",
            "author": "Herbert Goldstein",
            "format": "Physics",
            "subject": "Physics",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/classical-mechanics-3rd-edition/Classical%20Mechanics%203rd%20Edition.pdf",
        },
        {
            "id": "PHY002",
            "title": "Quantum Mechanics: The Theoretical Minimum",
            "author": "Leonard Susskind",
            "format": "Physics",
            "subject": "Physics",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/quantum-mechanics-theoretical-minimum/Quantum%20Mechanics%20The%20Theoretical%20Minimum.pdf",
        },
        {
            "id": "PHY003",
            "title": "Thermodynamics and Statistical Mechanics",
            "author": "Reif Frederick",
            "format": "Physics",
            "subject": "Physics",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/thermodynamics-statistical-mechanics/Thermodynamics%20and%20Statistical%20Mechanics.pdf",
        },
        {
            "id": "PHY004",
            "title": "Electromagnetism",
            "author": "Jackson John David",
            "format": "Physics",
            "subject": "Physics",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/classical-electrodynamics-3rd-edition/Classical%20Electrodynamics%203rd%20Edition.pdf",
        },
        {
            "id": "PHY005",
            "title": "Optics",
            "author": "Eugene Hecht",
            "format": "Physics",
            "subject": "Physics",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/optics-5th-edition/Optics%205th%20Edition.pdf",
        },
        {
            "id": "CHM005",
            "title": "Biochemistry",
            "author": "David L. Nelson & Michael M. Cox",
            "format": "Chemistry",
            "subject": "Chemistry",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/biochemistry-7th-edition/Biochemistry%207th%20Edition.pdf",
        },
        {
            "id": "CHM006",
            "title": "Environmental Chemistry",
            "author": "Stanley E. Manahan",
            "format": "Chemistry",
            "subject": "Chemistry",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/environmental-chemistry-10th-edition/Environmental%20Chemistry%2010th%20Edition.pdf",
        },
        {
            "id": "CHM007",
            "title": "Polymer Chemistry",
            "author": "Paul J. Flory",
            "format": "Chemistry",
            "subject": "Chemistry",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/polymer-chemistry-principles/Polymer%20Chemistry%20Principles.pdf",
        },
        {
            "id": "BIO007",
            "title": "Developmental Biology",
            "author": "Scott F. Gilbert",
            "format": "Biology",
            "subject": "Biology",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/developmental-biology-11th-edition/Developmental%20Biology%2011th%20Edition.pdf",
        },
        {
            "id": "BIO008",
            "title": "Evolutionary Biology",
            "author": "Douglas J. Futuyma & Mark Kirkpatrick",
            "format": "Biology",
            "subject": "Biology",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/evolutionary-biology-4th-edition/Evolutionary%20Biology%204th%20Edition.pdf",
        },
        {
            "id": "BIO009",
            "title": "Plant Physiology",
            "author": "Lincoln Taiz et al.",
            "format": "Biology",
            "subject": "Biology",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/plant-physiology-6th-edition/Plant%20Physiology%206th%20Edition.pdf",
        },
        {
            "id": "BIO010",
            "title": "Animal Behavior",
            "author": "John Alcock",
            "format": "Biology",
            "subject": "Biology",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/animal-behavior-11th-edition/Animal%20Behavior%2011th%20Edition.pdf",
        },
    ],
}

GENERAL_LIBRARY_BOOKS = [
    {
        "id": "GEN001",
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "copies": 4,
        "pdf_url": "https://www.gutenberg.org/files/1342/1342-pdf.pdf",
    },
    {
        "id": "GEN002",
        "title": "Crime and Punishment",
        "author": "Fyodor Dostoevsky",
        "copies": 4,
        "pdf_url": "https://www.gutenberg.org/files/2554/2554-pdf.pdf",
    },
    {
        "id": "GEN003",
        "title": "War and Peace",
        "author": "Leo Tolstoy",
        "copies": 4,
        "pdf_url": "https://www.gutenberg.org/files/2600/2600-pdf.pdf",
    },
    {
        "id": "GEN004",
        "title": "A Tale of Two Cities",
        "author": "Charles Dickens",
        "copies": 4,
        "pdf_url": "https://www.gutenberg.org/files/98/98-pdf.pdf",
    },
    {
        "id": "GEN005",
        "title": "Frankenstein",
        "author": "Mary Shelley",
        "copies": 4,
        "pdf_url": "https://www.gutenberg.org/files/84/84-pdf.pdf",
    },
    {
        "id": "GEN006",
        "title": "The Adventures of Sherlock Holmes",
        "author": "Arthur Conan Doyle",
        "copies": 4,
        "pdf_url": "https://www.gutenberg.org/files/1661/1661-pdf.pdf",
    },
]


COLLECTION_DEFAULTS = {
    "Encyclopaedia": [
        {
            "id": "ENC001",
            "title": "Encyclopaedia Britannica – Science & Technology",
            "author": "Britannica Group",
            "format": "Reference",
            "subject": "Reference",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://www.britannica.com/summary/science-summary.pdf",
        },
        {
            "id": "ENC002",
            "title": "World Book Encyclopaedia – Human Geography",
            "author": "World Book, Inc.",
            "format": "Reference",
            "subject": "Reference",
            "copies": 2,
            "borrowable": True,
            "pdf_url": "https://static.worldbook.com/reference/human-geography.pdf",
        },
        {
            "id": "ENC003",
            "title": "Oxford Encyclopaedia of World History",
            "author": "Oxford University Press",
            "format": "Reference",
            "subject": "Reference",
            "copies": 2,
            "borrowable": True,
            "pdf_url": "https://global.oup.com/example/world-history-encyclopedia.pdf",
        },
        {
            "id": "ENC004",
            "title": "Encyclopaedia of Philosophy",
            "author": "Stanford University",
            "format": "Reference",
            "subject": "Reference",
            "copies": 2,
            "borrowable": True,
            "pdf_url": "https://plato.stanford.edu/entries/philosophy-encyclopedia.pdf",
        },
        {
            "id": "ENC005",
            "title": "Encyclopaedia of Computer Science",
            "author": "Wiley",
            "format": "Reference",
            "subject": "Reference",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://www.wiley.com/en-us/Encyclopaedia+of+Computer+Science-p-9781118744055",
        },
    ],
    "Catalogues": [
        {
            "id": "CAT001",
            "title": "IKEA Furniture Catalogue 2025",
            "author": "IKEA Communications",
            "format": "Digital Catalogue",
            "subject": "Catalogues",
            "borrowable": False,
            "issue_date": "2025",
            "pdf_url": "https://catalogue.ikea.com/2025/ikea-catalogue-2025.pdf",
        },
        {
            "id": "CAT002",
            "title": "Apple Product Lineup Guide",
            "author": "Apple Inc.",
            "format": "Product Catalogue",
            "subject": "Catalogues",
            "borrowable": False,
            "issue_date": "Fall 2025",
            "pdf_url": "https://www.apple.com/newsroom/pdfs/product-guide-fall-2025.pdf",
        },
        {
            "id": "CAT003",
            "title": "Amazon Electronics Catalogue 2025",
            "author": "Amazon Inc.",
            "format": "Digital Catalogue",
            "subject": "Catalogues",
            "borrowable": False,
            "issue_date": "2025",
            "pdf_url": "https://www.amazon.com/gp/browse.html?node=electronics-catalogue-2025",
        },
        {
            "id": "CAT004",
            "title": "Best Buy Technology Guide",
            "author": "Best Buy Co.",
            "format": "Product Catalogue",
            "subject": "Catalogues",
            "borrowable": False,
            "issue_date": "November 2025",
            "pdf_url": "https://www.bestbuy.com/site/tech-guide-2025.pdf",
        },
        {
            "id": "CAT005",
            "title": "H&M Fashion Catalogue 2025",
            "author": "H&M Group",
            "format": "Fashion Catalogue",
            "subject": "Catalogues",
            "borrowable": False,
            "issue_date": "Fall 2025",
            "pdf_url": "https://www.hm.com/en/fashion-catalogue-2025.pdf",
        },
    ],
    "Magazines": [
        {
            "id": "MAG001",
            "title": "National Geographic – November 2025",
            "author": "National Geographic Society",
            "format": "Monthly Magazine",
            "subject": "Magazines",
            "borrowable": False,
            "issue_date": "November 2025",
            "pdf_url": "https://www.nationalgeographic.com/magazine/2025/11/national-geographic-november-2025.pdf",
        },
        {
            "id": "MAG002",
            "title": "Scientific American – AI Special",
            "author": "Springer Nature",
            "format": "Monthly Magazine",
            "subject": "Magazines",
            "borrowable": False,
            "issue_date": "October 2025",
            "pdf_url": "https://www.scientificamerican.com/media/pdf/ai-special-issue-2025.pdf",
        },
        {
            "id": "MAG003",
            "title": "The Economist – Global Economy",
            "author": "The Economist Group",
            "format": "Weekly Magazine",
            "subject": "Magazines",
            "borrowable": False,
            "issue_date": "November 2025",
            "pdf_url": "https://www.economist.com/media/pdf/global-economy-2025.pdf",
        },
        {
            "id": "MAG004",
            "title": "Wired – Technology & Culture",
            "author": "Condé Nast",
            "format": "Monthly Magazine",
            "subject": "Magazines",
            "borrowable": False,
            "issue_date": "November 2025",
            "pdf_url": "https://www.wired.com/magazine/2025/11/tech-culture.pdf",
        },
        {
            "id": "MAG005",
            "title": "Nature – Science Journal",
            "author": "Springer Nature",
            "format": "Weekly Journal",
            "subject": "Magazines",
            "borrowable": False,
            "issue_date": "November 2025",
            "pdf_url": "https://www.nature.com/articles/2025-11-science.pdf",
        },
    ],
    "Fiction": [
        {
            "id": "FIC001",
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "format": "Novel",
            "subject": "Fiction",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://www.gutenberg.org/cache/epub/64317/pg64317-images.html",
        },
        {
            "id": "FIC002",
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "format": "Novel",
            "subject": "Fiction",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://raw.githubusercontent.com/benoitvallon/100-best-books/master/the-great-gatsby.pdf",
        },
        {
            "id": "FIC003",
            "title": "1984",
            "author": "George Orwell",
            "format": "Novel",
            "subject": "Fiction",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://www.gutenberg.org/files/40697/40697-pdf.pdf",
        },
        {
            "id": "FIC004",
            "title": "Jane Eyre",
            "author": "Charlotte Brontë",
            "format": "Novel",
            "subject": "Fiction",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://www.gutenberg.org/files/1260/1260-pdf.pdf",
        },
        {
            "id": "FIC005",
            "title": "Wuthering Heights",
            "author": "Emily Brontë",
            "format": "Novel",
            "subject": "Fiction",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://www.gutenberg.org/files/768/768-pdf.pdf",
        },
    ],
    "Sci-Fi": [
        {
            "id": "SCI001",
            "title": "Dune",
            "author": "Frank Herbert",
            "format": "Science Fiction",
            "subject": "Science Fiction",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/dune-frank-herbert/Dune%20-%20Frank%20Herbert.pdf",
        },
        {
            "id": "SCI002",
            "title": "The Time Machine",
            "author": "H. G. Wells",
            "format": "Science Fiction",
            "subject": "Science Fiction",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://www.gutenberg.org/files/35/35-pdf.pdf",
        },
        {
            "id": "SCI003",
            "title": "Foundation",
            "author": "Isaac Asimov",
            "format": "Science Fiction",
            "subject": "Science Fiction",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/Foundation_20210101/Foundation.pdf",
        },
        {
            "id": "SCI004",
            "title": "Brave New World",
            "author": "Aldous Huxley",
            "format": "Science Fiction",
            "subject": "Science Fiction",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://www.gutenberg.org/files/32424/32424-pdf.pdf",
        },
        {
            "id": "SCI005",
            "title": "The War of the Worlds",
            "author": "H. G. Wells",
            "format": "Science Fiction",
            "subject": "Science Fiction",
            "copies": 3,
            "borrowable": True,
            "pdf_url": "https://www.gutenberg.org/files/36/36-pdf.pdf",
        },
    ],
    "Course Books": [
        {
            "id": "CRS001",
            "title": "Discrete Mathematics (3e)",
            "author": "OpenStax",
            "format": "Course Textbook",
            "subject": "Mathematics",
            "copies": 6,
            "borrowable": True,
            "pdf_url": "https://openstax.org/resources/discrete-mathematics-3e.pdf",
        },
        {
            "id": "CRS002",
            "title": "Introduction to Psychology",
            "author": "OpenStax",
            "format": "Course Textbook",
            "subject": "Psychology",
            "copies": 6,
            "borrowable": True,
            "pdf_url": "https://openstax.org/resources/psychology-3e.pdf",
        },
        {
            "id": "CRS003",
            "title": "College Algebra (2e)",
            "author": "OpenStax",
            "format": "Course Textbook",
            "subject": "Mathematics",
            "copies": 6,
            "borrowable": True,
            "pdf_url": "https://openstax.org/resources/college-algebra-2e.pdf",
        },
        {
            "id": "CRS004",
            "title": "Calculus Volume 1",
            "author": "OpenStax",
            "format": "Course Textbook",
            "subject": "Mathematics",
            "copies": 6,
            "borrowable": True,
            "pdf_url": "https://openstax.org/resources/calculus-volume-1.pdf",
        },
        {
            "id": "CRS005",
            "title": "Introduction to Sociology (3e)",
            "author": "OpenStax",
            "format": "Course Textbook",
            "subject": "Liberal Arts",
            "copies": 5,
            "borrowable": True,
            "pdf_url": "https://openstax.org/resources/introduction-to-sociology-3e.pdf",
        },
    ],
    "STEM Subjects": [
        {
            "id": "STM001",
            "title": "Advanced Engineering Mathematics",
            "author": "Erwin Kreyszig",
            "format": "Mathematics",
            "subject": "Mathematics",
            "copies": 5,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/AdvancedEngineeringMathematics10thEdition/Erwin%20Kreyszig%20-%20Advanced%20Engineering%20Mathematics%2010th%20Edition.pdf",
        },
        {
            "id": "STM002",
            "title": "Fundamentals of Physics",
            "author": "Halliday, Resnick & Walker",
            "format": "Physics",
            "subject": "Physics",
            "copies": 5,
            "borrowable": True,
            "pdf_url": "https://www.academia.edu/34840860/Fundamentals_of_Physics_10th_Edition",
        },
        {
            "id": "STM003",
            "title": "Organic Chemistry Essentials",
            "author": "Paula Yurkanis Bruice",
            "format": "Chemistry",
            "subject": "Chemistry",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://archive.org/download/organic-chemistry-8th-edition-by-paula-yurkanis-bruice/Organic%20Chemistry%208th%20Edition%20by%20Paula%20Yurkanis%20Bruice.pdf",
        },
        {
            "id": "STM004",
            "title": "Biology for Engineers",
            "author": "Arthur T. Johnson",
            "format": "Biology",
            "subject": "Biology",
            "copies": 4,
            "borrowable": True,
            "pdf_url": "https://ocw.mit.edu/courses/20-010j-introduction-to-bioengineering-be-introductory-biology-spring-2006/7c2438afec889d3a5eb0213b04fc3c0f_lecturenotes.pdf",
        },
    ],
    "Newspapers": [
        {
            "id": "NEWS001",
            "title": "The Guardian – Morning Edition",
            "author": "Guardian News & Media",
            "format": "Daily Newspaper",
            "subject": "Newspapers",
            "borrowable": False,
            "issue_date": "12 Nov 2025",
            "pdf_url": "https://static.guim.co.uk/2025/11/12/TheGuardian-MorningEdition.pdf",
        },
        {
            "id": "NEWS002",
            "title": "The New York Times – International",
            "author": "The New York Times Company",
            "format": "Daily Newspaper",
            "subject": "Newspapers",
            "borrowable": False,
            "issue_date": "12 Nov 2025",
            "pdf_url": "https://static.nytimes.com/2025/11/12/international-print.pdf",
        },
        {
            "id": "NEWS003",
            "title": "BBC News – World Report",
            "author": "British Broadcasting Corporation",
            "format": "Daily Newspaper",
            "subject": "Newspapers",
            "borrowable": False,
            "issue_date": "12 Nov 2025",
            "pdf_url": "https://www.bbc.com/news/world/2025/11/12/report.pdf",
        },
        {
            "id": "NEWS004",
            "title": "The Times – UK Edition",
            "author": "News Corp",
            "format": "Daily Newspaper",
            "subject": "Newspapers",
            "borrowable": False,
            "issue_date": "12 Nov 2025",
            "pdf_url": "https://www.thetimes.co.uk/edition/2025/11/12/uk-edition.pdf",
        },
        {
            "id": "NEWS005",
            "title": "Financial Times – Markets & Finance",
            "author": "Nikkei Inc.",
            "format": "Daily Newspaper",
            "subject": "Newspapers",
            "borrowable": False,
            "issue_date": "12 Nov 2025",
            "pdf_url": "https://www.ft.com/content/2025/11/12/markets-finance.pdf",
        },
    ],
}


def _slugify_program(programme: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", programme.upper())[:8] or "GEN"


SUBJECT_OVERRIDES = {
    "ENG001": "Physics",
    "ENG002": "Physics",
    "ENG003": "Physics",
    "ENG004": "Physics",
    "ENG005": "Physics",
    "ENG006": "Mathematics",
    "CRS001": "Mathematics",
    "CRS002": "Psychology",
    "STM001": "Mathematics",
    "STM002": "Physics",
    "STM003": "Chemistry",
    "STM004": "Biology",
    "PHY001": "Physics",
    "PHY002": "Physics",
    "PHY003": "Physics",
    "PHY004": "Physics",
    "PHY005": "Physics",
    "CHM005": "Chemistry",
    "CHM006": "Chemistry",
    "CHM007": "Chemistry",
    "BIO001": "Biology",
    "BIO002": "Biology",
    "BIO003": "Biology",
    "BIO004": "Biology",
    "BIO005": "Biology",
    "BIO006": "Biology",
    "BIO007": "Biology",
    "BIO008": "Biology",
    "BIO009": "Biology",
    "BIO010": "Biology",
    "T001": "Mathematics",
    "T002": "Science",
    "T003": "Psychology",
}


SUBJECT_PREFIX_DEFAULTS = {
    "AI": "Artificial Intelligence",
    "ART": "Liberal Arts",
    "DES": "Design",
    "MGT": "Management",
    "MED": "Media Studies",
    "LAW": "Law",
    "GEN": "Classic Literature",
    "FIC": "Fiction",
    "SCI": "Science Fiction",
    "MAG": "Magazines",
    "CAT": "Catalogues",
    "ENC": "Reference",
    "NEWS": "Newspapers",
    "STM": "STEM",
}


def _resolve_subject(base_id: str, template: dict) -> str | None:
    # Check if template has explicit subject field
    explicit_subject = template.get('subject')
    if isinstance(explicit_subject, str) and explicit_subject.strip():
        return explicit_subject.strip()
    
    base_id = (base_id or "").strip()
    if not base_id:
        return None
    if base_id in SUBJECT_OVERRIDES:
        return SUBJECT_OVERRIDES[base_id]
    prefix_match = re.match(r"[A-Z]+", base_id)
    if prefix_match:
        prefix = prefix_match.group(0)
        if prefix in SUBJECT_PREFIX_DEFAULTS:
            return SUBJECT_PREFIX_DEFAULTS[prefix]
    fmt = template.get('format')
    if isinstance(fmt, str) and fmt.strip():
        return fmt.strip()
    return None


def _ensure_subject_tag(book: dict) -> str | None:
    existing = book.get('subject')
    if isinstance(existing, str) and existing.strip():
        return existing.strip()
    book_id = str(book.get('id', '')).split('_')[0]
    subject = _resolve_subject(book_id, book)
    if subject:
        book['subject'] = subject
    return subject


def _build_unique_program_title(
    base_title: str | None,
    programme: str,
    slug: str,
    signature_base: str,
) -> str:
    """Ensure programme-specific titles stay readable and distinct."""

    title = base_title.strip() if isinstance(base_title, str) else ""
    programme_label = re.sub(r"\s+", " ", programme).strip() if isinstance(programme, str) else slug

    if title:
        # Avoid duplicating programme info if already present.
        if programme_label and programme_label.lower() in title.lower():
            return title
        return f"{title} ({programme_label})" if programme_label else title

    programme_label = programme_label or slug or "Programme"
    return f"{programme_label} Resource {signature_base}"


def _make_program_book_entry(template: dict, programme: str, category: str, slug: str | None = None) -> dict:
    slug = slug or _slugify_program(programme)
    entry = template.copy()
    base_id = entry['id']
    entry['id'] = f"{base_id}_{slug}"
    signature_base = re.sub(r"[^A-Z0-9]", "", base_id.upper()) or base_id.upper()
    base_title = entry.get('title') if isinstance(entry.get('title'), str) else None
    entry['original_title'] = base_title
    entry['title'] = _build_unique_program_title(base_title, programme, slug, signature_base)
    entry['title_signature'] = f"{slug}:{signature_base}"
    copies = max(int(entry.get('copies', 1)), 1)
    entry['copies'] = copies
    entry['available'] = copies
    entry['programme'] = programme
    entry['program_category'] = category
    entry['catalog_type'] = 'program'
    entry['subject'] = _resolve_subject(base_id, template)
    pdf_url = entry.get('pdf_url')
    if isinstance(pdf_url, str) and pdf_url.strip():
        clean_url = pdf_url.strip()
        delimiter = '&' if '?' in clean_url else '?'
        entry['pdf_url'] = f"{clean_url}{delimiter}programme={slug}"
    else:
        entry.pop('pdf_url', None)
    return entry


def build_default_program_books():
    program_books = {}
    global_stem_templates = DEFAULT_CATEGORY_BOOKS.get("STEM", [])
    for category, programmes in PROGRAM_CATEGORIES.items():
        base_templates = DEFAULT_CATEGORY_BOOKS.get(category, [])
        if global_stem_templates:
            templates = list(base_templates) + list(global_stem_templates)
        else:
            templates = base_templates
        for programme in programmes:
            slug = _slugify_program(programme)
            program_books[programme] = [
                _make_program_book_entry(template, programme, category, slug)
                for template in templates
            ]
    return program_books


def programme_books(programme: str) -> list[dict]:
    books = st.session_state.app.books.get('program_books', {}).get(programme, [])
    if books:
        return books

    if programme in st.session_state.app.books.get('program_books', {}):
        st.session_state.app.seed_program_books()
        st.session_state.app.normalize_book_metadata()
        books = st.session_state.app.books.get('program_books', {}).get(programme, [])
        if books:
            st.session_state.app.save_data()
    return books


def get_latest_programme_books(programme: str, limit: int = 5) -> list[dict]:
    books = programme_books(programme)
    if not books:
        return []
    sorted_books = sorted(
        books,
        key=lambda b: b.get('added_at') or b.get('title_signature', ''),
        reverse=True,
    )
    return sorted_books[:limit]


def build_collection_catalog() -> dict[str, list[dict]]:
    catalog: dict[str, list[dict]] = {}
    for name, entries in COLLECTION_DEFAULTS.items():
        prepared: list[dict] = []
        for template in entries:
            item = dict(template)
            borrowable = bool(item.get('borrowable', False))
            copies = int(item.get('copies', 0) or (1 if borrowable else 0))
            item['borrowable'] = borrowable
            item['copies'] = max(copies, 0)
            item['available'] = item['copies']
            item['catalog_type'] = 'collection'
            item['collection'] = name
            issue_date = item.get('issue_date')
            if isinstance(issue_date, str):
                item['issue_date'] = issue_date.strip()
            pdf_url = item.get('pdf_url')
            if isinstance(pdf_url, str):
                item['pdf_url'] = pdf_url.strip()
            else:
                item.pop('pdf_url', None)
            _ensure_subject_tag(item)
            prepared.append(item)
        catalog[name] = prepared
    return catalog


def collection_catalog() -> dict[str, list[dict]]:
    return st.session_state.app.books.get('collection_catalog', {})


def collection_items(name: str) -> list[dict]:
    return collection_catalog().get(name, [])


def borrowable_collection_items() -> list[dict]:
    items = []
    for collection, entries in collection_catalog().items():
        for entry in entries:
            if entry.get('borrowable'):
                items.append(entry)
    return items


def all_subjects() -> list[str]:
    subjects = set()

    for programme_books in st.session_state.app.books.get('program_books', {}).values():
        for book in programme_books:
            subject = _ensure_subject_tag(book)
            if subject:
                subjects.add(subject)

    for book in st.session_state.app.books.get('teacher_books', []):
        subject = _ensure_subject_tag(book)
        if subject:
            subjects.add(subject)

    for collection_entries in collection_catalog().values():
        for item in collection_entries:
            subject = _ensure_subject_tag(item)
            if subject:
                subjects.add(subject)

    return sorted(subjects)


def _email_setting(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if isinstance(value, str) and value.strip() else None


def send_reservation_email(
    to_email: str,
    user_name: str,
    book: dict,
    reservation: dict,
) -> tuple[bool, str | None]:
    smtp_server = _email_setting("BOOKFLOW_SMTP_SERVER")
    smtp_port = _email_setting("BOOKFLOW_SMTP_PORT") or "465"
    smtp_username = _email_setting("BOOKFLOW_SMTP_USERNAME")
    smtp_password = _email_setting("BOOKFLOW_SMTP_PASSWORD")
    sender_email = _email_setting("BOOKFLOW_EMAIL_SENDER") or smtp_username

    if not all([smtp_server, smtp_username, smtp_password, sender_email]):
        return False, (
            "SMTP settings are incomplete. Set BOOKFLOW_SMTP_SERVER, BOOKFLOW_SMTP_PORT, "
            "BOOKFLOW_SMTP_USERNAME, BOOKFLOW_SMTP_PASSWORD, and BOOKFLOW_EMAIL_SENDER."
        )

    try:
        port = int(smtp_port)
    except ValueError:
        return False, f"Invalid SMTP port: {smtp_port}"

    book_title = book.get('title', 'Requested Book')
    programme = book.get('programme') or 'General Library'
    subject = f"Reservation confirmed for \"{book_title}\""
    reserved_at = reservation.get('reserved_at', datetime.now().strftime('%Y-%m-%d %H:%M'))

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email
    message.set_content(
        f"Hello {user_name},\n\n"
        f"We've recorded your reservation for \"{book_title}\" in the BookFlow library.\n\n"
        f"Reservation details:\n"
        f"• Programme: {programme}\n"
        f"• Reservation ID: {reservation.get('id')}\n"
        f"• Reserved on: {reserved_at}\n\n"
        "We'll notify you as soon as a copy becomes available.\n\n"
        "Thank you for using BookFlow!"
    )

    try:
        context = ssl.create_default_context()
        if port == 465:
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP(smtp_server, port, timeout=20) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(smtp_username, smtp_password)
                server.send_message(message)
        return True, None
    except smtplib.SMTPAuthenticationError as exc:
        detail = None
        if getattr(exc, "smtp_error", None):
            try:
                detail = exc.smtp_error.decode("utf-8", errors="ignore")
            except AttributeError:
                detail = str(exc.smtp_error)
        return False, (
            f"Authentication failed: {detail.strip()}" if detail else "Authentication failed: check username/app password."
        )
    except smtplib.SMTPConnectError as exc:
        return False, f"Connection error: {exc.smtp_error.decode() if getattr(exc, 'smtp_error', None) else exc}"
    except Exception as exc:  # pragma: no cover - depends on external SMTP
        return False, str(exc)


def _render_programme_carousel(programme: str, books: list[dict], slider_key: str) -> None:
    if not books:
        return

    carousel_id = f"bf-carousel-{_slugify_program(programme)}"
    interval_ms = 7000

    slides_html: list[str] = []
    indicators_html: list[str] = []

    for idx, book in enumerate(books):
        title = html.escape(book.get("title", "Untitled"))
        author = html.escape(book.get("author", "Unknown"))
        book_id = html.escape(book.get("id", ""))
        copies = int(book.get("copies", 0) or 0)
        available = int(book.get("available", 0) or 0)
        pdf_url = (book.get("pdf_url") or "").strip()
        pdf_html = (
            f"<a class=\"bf-link\" href=\"{html.escape(pdf_url)}\" target=\"_blank\">📄 Download</a>"
            if pdf_url
            else ""
        )

        slides_html.append(
            f"""
            <li>
                <div class=\"bf-slide-card\">
                    <div class=\"bf-slide-header\">
                        <span class=\"bf-slide-pill\">Slide {idx + 1} / {len(books)}</span>
                        <span class=\"bf-slide-badge\">{available} / {copies} Available</span>
                    </div>
                    <h2 class=\"bf-slide-title\">{title}</h2>
                    <p class=\"bf-slide-author\">✍️ {author}</p>
                    <div class=\"bf-slide-meta\">
                        <span>{'🆔 ' + book_id if book_id else ''}</span>
                        <span>{pdf_html}</span>
                    </div>
                </div>
            </li>
            """
        )

        indicators_html.append(
            f"<button type=\"button\" class=\"{'active' if idx == 0 else ''}\"></button>"
        )

    slides_markup = "\n".join(slides_html)
    indicators_markup = "\n".join(indicators_html)
    heading = html.escape(programme)

    components.html(
        f"""
        <link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/swiffy-slider@1.6.0/dist/css/swiffy-slider.min.css\" integrity=\"sha384-wy4mQyqX4qsutPOgo5sLiCFYl8aAkaI0s5momkGLumZ5qX6Ch12yvDqOiiMHDL/4\" crossorigin=\"anonymous\">
        <script src=\"https://cdn.jsdelivr.net/npm/swiffy-slider@1.6.0/dist/js/swiffy-slider.min.js\" integrity=\"sha384-G1IanFkFJxuxMxDPZWS9Vyuk3F7S3w7Dnk3a1JpNggCBvs1+qsSVqS+8CA0nVddO\" crossorigin=\"anonymous\" defer></script>
        <style>
            #{carousel_id} .bf-slider-shell {{
                background: linear-gradient(135deg, #4facfe 0%, #6C0345 100%);
                border-radius: 14px;
                padding: 1.2rem 1.4rem;
                margin-top: 0.5rem;
                box-shadow: 0 10px 24px rgba(0,0,0,0.35);
                color: #fff;
                font-family: 'Segoe UI', sans-serif;
            }}
            #{carousel_id} .bf-slider-shell h3 {{
                margin: 0.4rem 0 0 0;
                font-size: 1.4rem;
            }}
            #{carousel_id} .bf-slide-card {{
                background: rgba(17,17,17,0.85);
                backdrop-filter: blur(4px);
                border-radius: 12px;
                padding: 1.5rem;
                min-height: 160px;
                display: flex;
                flex-direction: column;
                gap: 0.9rem;
                box-shadow: 0 12px 24px rgba(0,0,0,0.35);
            }}
            #{carousel_id} .bf-slide-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 0.6rem;
                font-size: 0.78rem;
                letter-spacing: 0.05em;
            }}
            #{carousel_id} .bf-slide-pill {{
                background: rgba(255,255,255,0.12);
                padding: 0.25rem 0.65rem;
                border-radius: 999px;
            }}
            #{carousel_id} .bf-slide-badge {{
                background: rgba(40,167,69,0.2);
                color: #87ffb3;
                padding: 0.25rem 0.65rem;
                border-radius: 999px;
                font-weight: 600;
            }}
            #{carousel_id} .bf-slide-title {{
                margin: 0;
                font-size: 1.5rem;
            }}
            #{carousel_id} .bf-slide-author {{
                margin: 0;
                font-size: 0.95rem;
                color: rgba(255,255,255,0.78);
            }}
            #{carousel_id} .bf-slide-meta {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.8rem;
                font-size: 0.82rem;
                color: rgba(255,255,255,0.68);
            }}
            #{carousel_id} .bf-link {{
                color: #ffe066;
                text-decoration: none;
                font-weight: 600;
            }}
            #{carousel_id} .slider-nav::before {{
                background: rgba(0,0,0,0.4);
                border-radius: 50%;
            }}
            #{carousel_id} .slider-indicators button {{
                background: rgba(255,255,255,0.35);
                width: 10px;
                height: 10px;
                margin: 0 4px;
            }}
            #{carousel_id} .slider-indicators button.active {{
                background: #ffe066;
            }}
        </style>
        <div id=\"{carousel_id}\">
            <div class=\"bf-slider-shell\">
                <p style=\"margin:0; opacity:0.85; font-size:0.72rem; letter-spacing:0.12em;\">LATEST FOR YOUR PROGRAMME</p>
                <h3>🔥 Fresh Picks for {heading}</h3>
                <div class=\"swiffy-slider\" data-slider-nav-autoplay data-slider-nav-autoplay-interval=\"{interval_ms}\" data-slider-nav-autopause=\"hover\" data-slider-nav-animation=\"slide\">
                    <ul class=\"slider-container\">
                        {slides_markup}
                    </ul>
                    <button type=\"button\" class=\"slider-nav\"></button>
                    <button type=\"button\" class=\"slider-nav slider-nav-next\"></button>
                    <div class=\"slider-indicators\">
                        {indicators_markup}
                    </div>
                </div>
            </div>
        </div>
        <script>
            (function() {{
                const mount = document.getElementById('{carousel_id}');
                const initSlider = () => {{
                    if (window.swiffyslider && mount) {{
                        window.swiffyslider.init(mount);
                    }}
                }};

                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', initSlider, {{ once: true }});
                }} else {{
                    initSlider();
                }}

                document.addEventListener('swiffy-slider:init', initSlider);
            }})();
        </script>
        """,
        height=360,
        key=f"{carousel_id}_component",
    )


class BookFlowApp:
    def __init__(self):
        self.data_file = "bookflow_data.json"
        self.reservations: list[dict] = []
        self.load_data()
    
    def load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.users = data.get('users', self.get_default_users())
                self.books = data.get('books', self.get_default_books())
                self.transactions = data.get('transactions', [])
                self.reservations = data.get('reservations', [])
                self.migrate_user_contact_fields()
                self.migrate_user_password_fields()
                self.migrate_program_books()
                self.migrate_user_program_fields()
                self.seed_program_books()
                self.seed_collection_catalog()
                self.normalize_book_metadata()
        except FileNotFoundError:
            self.users = self.get_default_users()
            self.books = self.get_default_books()
            self.transactions = []
            self.reservations = []
            self.migrate_user_password_fields()
            self.migrate_program_books()
            self.migrate_user_program_fields()
            self.seed_program_books()
            self.seed_collection_catalog()
            self.normalize_book_metadata()
            self.save_data()
    
    def migrate_user_contact_fields(self):
        """Add contact and email fields to existing users if missing"""
        updated = False
        for role in ['students', 'teachers', 'admin']:
            if role in self.users:
                for user in self.users[role]:
                    if 'contact' not in user:
                        user['contact'] = 'Not provided'
                        updated = True
                    if 'email' not in user:
                        user['email'] = 'Not provided'
                        updated = True
        if updated:
            self.save_data()

    def migrate_user_password_fields(self):
        """Ensure all stored users have hashed passwords."""
        updated = False
        for role, users in self.users.items():
            for user in users:
                if ensure_password_fields(user):
                    updated = True

        if updated:
            self.save_data()

    def save_data(self):
        """Save data to JSON file"""
        data = {
            'users': self.users,
            'books': self.books,
            'transactions': self.transactions,
            'reservations': self.reservations,
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)

    def update_user_email(self, user_id: str, role: str, email: str | None) -> None:
        role_key = (
            'students'
            if role == 'student'
            else 'teachers'
            if role == 'teacher'
            else 'admin'
        )
        new_value = email.strip() if isinstance(email, str) and email.strip() else 'Not provided'
        for user in self.users.get(role_key, []):
            if user.get('id') == user_id:
                user['email'] = new_value
                break
        self.save_data()

    def get_active_reservation(self, user_id: str, book_id: str) -> dict | None:
        for record in self.reservations:
            if (
                record.get('user_id') == user_id
                and record.get('book_id') == book_id
                and record.get('status', 'waiting') == 'waiting'
            ):
                return record
        return None

    def create_reservation(self, user: dict, book: dict) -> dict:
        sequence = len(self.reservations) + 1
        reservation_id = f"RSV{datetime.now().strftime('%Y%m%d%H%M%S')}{sequence:03d}"
        reserved_at = datetime.now().strftime('%Y-%m-%d %H:%M')
        record = {
            'id': reservation_id,
            'book_id': book['id'],
            'book_title': book.get('title'),
            'programme': book.get('programme'),
            'user_id': user.get('id'),
            'user_name': user.get('name'),
            'user_email': user.get('email'),
            'status': 'waiting',
            'reserved_at': reserved_at,
        }
        self.reservations.append(record)
        self.save_data()
        return record

    def get_default_users(self):
        default_programme = all_programmes()[0] if all_programmes() else 'General Library'

        defaults = {
            'students': [
                {'id': 'E25CSEU1187', 'username': 'sairam', 'password': 'sairam123', 'name': 'Sairam R', 
                 'contact': '+91 9876543210', 'email': 'sairam@example.com', 'programme': default_programme},
                {'id': 'B24ECE0045', 'username': 'student2', 'password': 'student123', 'name': 'Student 2',
                 'contact': '+91 9876543211', 'email': 'student2@example.com', 'programme': default_programme}
            ],
            'teachers': [
                {'id': 'T25CSED101', 'username': 'prof_bohra', 'password': 'teacher123', 'name': 'Prof Bohra',
                 'contact': '+91 9876543220', 'email': 'bohra@example.com'},
                {'id': 'P24MATH205', 'username': 'prof_jd', 'password': 'teacher123', 'name': 'Prof JD',
                 'contact': '+91 9876543221', 'email': 'profjd@example.com'}
            ],
        }

        admin_username = os.getenv('BOOKFLOW_ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('BOOKFLOW_ADMIN_PASSWORD', 'morningstar123')
        admin_contact = os.getenv('BOOKFLOW_ADMIN_CONTACT', 'Not provided')
        admin_email = os.getenv('BOOKFLOW_ADMIN_EMAIL', 'Not provided')

        admin_hash, admin_salt = hash_password(admin_password)
        defaults['admin'] = [{
            'id': os.getenv('BOOKFLOW_ADMIN_ID', 'ADMIN001'),
            'username': admin_username,
            'password_hash': admin_hash,
            'password_salt': admin_salt,
            'name': os.getenv('BOOKFLOW_ADMIN_NAME', 'Administrator'),
            'contact': admin_contact,
            'email': admin_email
        }]

        for role_users in defaults.values():
            for user in role_users:
                if 'password' in user:
                    password_hash, password_salt = hash_password(user['password'])
                    user['password_hash'] = password_hash
                    user['password_salt'] = password_salt
                    user.pop('password', None)

        return defaults
    
    def get_default_books(self):
        teacher_books = [
            {'id': 'T001', 'title': 'R.D. Sharma Mathematics', 'author': 'R.D. Sharma', 'copies': 5, 'available': 5, 'catalog_type': 'teacher'},
            {'id': 'T002', 'title': 'NCERT Science', 'author': 'NCERT', 'copies': 10, 'available': 10, 'catalog_type': 'teacher'},
            {'id': 'T003', 'title': 'Psychology of Prejudice', 'author': 'Various', 'copies': 2, 'available': 2, 'catalog_type': 'teacher'},
        ]

        for book in teacher_books:
            _ensure_subject_tag(book)

        return {
            'program_books': build_default_program_books(),
            'teacher_books': teacher_books,
            'collection_catalog': build_collection_catalog(),
        }

    def migrate_program_books(self):
        """Ensure program-specific books structure exists."""
        program_books = self.books.setdefault('program_books', {})

        legacy_students = self.books.pop('student_books', [])
        if legacy_students:
            general = program_books.setdefault('General Library', [])
            for book in legacy_students:
                book.setdefault('copies', book.get('available', 1))
                book.setdefault('available', book['copies'])
                book['programme'] = 'General Library'
                book['program_category'] = 'General'
                book['catalog_type'] = 'program'
                general.append(book)

        for programme in all_programmes():
            program_books.setdefault(programme, [])

    def migrate_user_program_fields(self):
        programmes = set(all_programmes())
        if not programmes:
            return

        updated = False
        default_programme = next(iter(programmes))
        for user in self.users.get('students', []):
            if user.get('programme') not in programmes:
                user['programme'] = default_programme
                updated = True

        if updated:
            self.save_data()

    def seed_program_books(self):
        program_books = self.books.setdefault('program_books', {})
        defaults = build_default_program_books()
        seeded = False

        for programme, default_books in defaults.items():
            existing = program_books.get(programme)
            slug = _slugify_program(programme)
            default_map = {book['id'].split('_')[0]: book for book in default_books}
            if not existing:
                program_books[programme] = [dict(book) for book in default_books]
                seeded = True
            else:
                existing_map = {book['id'].split('_')[0]: book for book in existing}
                needs_refresh = False
                for book in existing:
                    pdf_url = book.get('pdf_url')
                    if isinstance(pdf_url, str):
                        if 'programme=' not in pdf_url:
                            needs_refresh = True
                            break
                    else:
                        needs_refresh = True
                        break
                    title = book.get('title')
                    if not isinstance(title, str) or programme not in title:
                        needs_refresh = True
                        break
                if needs_refresh:
                    program_books[programme] = [dict(book) for book in default_books]
                    seeded = True
                else:
                    for base_id, template in default_map.items():
                        existing_book = existing_map.get(base_id)
                        if existing_book:
                            if template.get('copies') and existing_book.get('copies', 0) < template['copies']:
                                existing_book['copies'] = template['copies']
                                existing_book['available'] = min(existing_book.get('available', template['copies']), template['copies'])
                                seeded = True
                            if template.get('pdf_url') and not existing_book.get('pdf_url'):
                                existing_book['pdf_url'] = template['pdf_url']
                                seeded = True
                        else:
                            new_entry = dict(template)
                            new_entry['available'] = new_entry.get('copies', 1)
                            existing.append(new_entry)
                            seeded = True

        # ensure general library defaults exist
        general_books = program_books.setdefault('General Library', [])
        if len(general_books) < len(GENERAL_LIBRARY_BOOKS):
            existing_ids = {b['id'] for b in general_books}
            for book in GENERAL_LIBRARY_BOOKS:
                if book['id'] not in existing_ids:
                    entry = dict(book)
                    entry['available'] = entry.get('copies', 1)
                    entry['programme'] = 'General Library'
                    entry['program_category'] = 'General'
                    entry['catalog_type'] = 'program'
                    general_books.append(entry)
                    seeded = True
        else:
            general_map = {book['id']: book for book in GENERAL_LIBRARY_BOOKS}
            for book in general_books:
                template = general_map.get(book['id'])
                if not template:
                    continue
                if template.get('pdf_url') and not book.get('pdf_url'):
                    book['pdf_url'] = template['pdf_url']
                if template.get('copies') and book.get('copies', 0) < template['copies']:
                    book['copies'] = template['copies']
                    book['available'] = min(book.get('available', template['copies']), template['copies'])

        if seeded:
            self.save_data()

    def seed_collection_catalog(self):
        catalog = self.books.setdefault('collection_catalog', {})
        defaults = build_collection_catalog()
        updated = False

        for name, default_items in defaults.items():
            existing = catalog.get(name)
            if not existing:
                catalog[name] = [dict(item) for item in default_items]
                updated = True
                continue

            existing_map = {item['id']: item for item in existing}
            for template in default_items:
                entry = existing_map.get(template['id'])
                if entry:
                    if entry.get('borrowable') != template['borrowable']:
                        entry['borrowable'] = template['borrowable']
                        updated = True
                    entry['catalog_type'] = 'collection'
                    entry['collection'] = name
                    if template.get('format') and entry.get('format') != template['format']:
                        entry['format'] = template['format']
                        updated = True
                    if template.get('issue_date') and entry.get('issue_date') != template['issue_date']:
                        entry['issue_date'] = template['issue_date']
                        updated = True
                    copies = template['copies']
                    if entry.get('copies') != copies:
                        entry['copies'] = copies
                        updated = True
                    if template['borrowable']:
                        available = min(entry.get('available', copies), copies)
                    else:
                        available = 0
                    if entry.get('available') != available:
                        entry['available'] = available
                        updated = True
                    if template.get('pdf_url'):
                        if entry.get('pdf_url') != template['pdf_url']:
                            entry['pdf_url'] = template['pdf_url']
                            updated = True
                    else:
                        if entry.get('pdf_url'):
                            entry.pop('pdf_url', None)
                            updated = True
                else:
                    catalog[name].append(dict(template))
                    updated = True

        for name in catalog.keys():
            for item in catalog[name]:
                item['catalog_type'] = 'collection'
                item['collection'] = name

        if updated:
            self.save_data()

    def normalize_book_metadata(self):
        program_books = self.books.get('program_books', {})
        for programme, books in program_books.items():
            category = programme_category(programme) or 'General'
            for book in books:
                book['catalog_type'] = 'program'
                book['programme'] = programme
                book['program_category'] = category
                copies = max(int(book.get('copies', 1)), 1)
                available = book.get('available', copies)
                book['copies'] = copies
                book['available'] = min(max(int(available), 0), copies)
                pdf_url = book.get('pdf_url')
                if isinstance(pdf_url, str):
                    book['pdf_url'] = pdf_url.strip()
                else:
                    book.pop('pdf_url', None)
                if book.get('copies') and book.get('copies', 0) < book.get('copies', 1):
                    book['copies'] = book.get('copies', 1)
                    book['available'] = min(book.get('available', book.get('copies', 1)), book.get('copies', 1))
                _ensure_subject_tag(book)

        catalog = self.books.setdefault('collection_catalog', {})
        for name, items in catalog.items():
            for item in items:
                item['catalog_type'] = 'collection'
                item['collection'] = name
                borrowable = bool(item.get('borrowable', False))
                item['borrowable'] = borrowable
                copies = int(item.get('copies', 0))
                if borrowable and copies <= 0:
                    copies = 1
                elif not borrowable:
                    copies = 0
                item['copies'] = copies
                available = int(item.get('available', copies))
                if borrowable:
                    item['available'] = min(max(available, 0), copies)
                else:
                    item['available'] = 0
                issue_date = item.get('issue_date')
                if isinstance(issue_date, str):
                    item['issue_date'] = issue_date.strip()
                pdf_url = item.get('pdf_url')
                if isinstance(pdf_url, str):
                    item['pdf_url'] = pdf_url.strip()
                else:
                    item.pop('pdf_url', None)
                _ensure_subject_tag(item)

        for book in self.books.get('teacher_books', []):
            book['catalog_type'] = 'teacher'
            book.pop('programme', None)
            copies = max(int(book.get('copies', 1)), 1)
            available = book.get('available', copies)
            book['copies'] = copies
            book['available'] = min(max(int(available), 0), copies)
            _ensure_subject_tag(book)

    def get_program_books(self, programme: str) -> list[dict]:
        return self.books.get('program_books', {}).get(programme, [])

    def iter_program_books(self):
        for programme, books in self.books.get('program_books', {}).items():
            for book in books:
                yield programme, book

    def verify_login(self, username, password, role):
        """Verify user credentials"""
        role_key = 'students' if role == 'student' else 'teachers' if role == 'teacher' else 'admin'
        users = self.users.get(role_key, [])

        
        for user in users:
            if user['username'] == username and verify_password(password, user.get('password_hash'), user.get('password_salt')):
                return user
        return None

# Initialize app
if 'app' not in st.session_state:
    st.session_state.app = BookFlowApp()
elif not (
    hasattr(st.session_state.app, 'get_active_reservation')
    and hasattr(st.session_state.app, 'create_reservation')
):
    st.session_state.app = BookFlowApp()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.selected_program = None

def login_page():
    """Display login page"""
    # Hero section with gradient - compact
    st.markdown("""
        <div style='background: linear-gradient(135deg, #6C0345 0%, #DC143C 100%); 
                    padding: 0.8rem 0.5rem; border-radius: 8px; margin-bottom: 1rem;
                    box-shadow: 0 2px 8px rgba(108, 3, 69, 0.3);'>
            <h1 style='color: white; text-align: center; font-size: 1.5rem; margin: 0; 
                       text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>
                📚 BookFlow LMS
            </h1>
            <p style='color: #F7C566; text-align: center; font-size: 0.8rem; margin: 0.3rem 0 0 0;
                      text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
                Modern Library Management System
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        _login_intro_animation()

        # Login card with shadow - dark theme
        st.markdown("""
            <div style='background: #1e1e1e; padding: 0.8rem; border-radius: 8px; 
                        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                        border: 1px solid #333333;'>
                <h2 style='color: #ffffff; text-align: center; margin: 0; font-size: 1.1rem;'>
                    🔐 Welcome Back!
                </h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        
        role = st.radio("**Select Your Role:**", ["Student", "Teacher"], horizontal=True)
        username = st.text_input("**Username**", placeholder="Enter your username", key="login_username")
        password = st.text_input("**Password**", type="password", placeholder="Enter your password", key="login_password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🚀 Login", use_container_width=True, type="primary"):
                if username and password:
                    user = st.session_state.app.verify_login(username, password, role.lower())
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.role = role.lower()
                        st.session_state.selected_program = (
                            user.get('programme') if st.session_state.role == 'student' else None
                        )
                        st.success(f"✅ Welcome back, {user['name']}!")
                        _celebration_gif()
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials! Please check your username and password.")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        with col_b:
            if st.button("📝 Create Account", use_container_width=True):
                st.session_state.page = 'register'
                st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Admin access moved to dedicated entry point

def register_page():
    """Display registration page"""
    st.markdown('<h1 class="main-header">📝 Register New Account</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        role = st.radio("Select Role:", ["Student", "Teacher"], horizontal=True)
        
        name = st.text_input("Full Name", placeholder="Enter your full name")
        username = st.text_input("Username", placeholder="Choose a username (min 3 chars)")
        password = st.text_input("Password", type="password", placeholder="Choose a password (min 6 chars)")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
        
        if role == "Student":
            st.info("📋 Student ID Format: E25CSEU1187 (Letter + 2digits + 3-4letters + 4digits)")
            user_id = st.text_input("Student ID", placeholder="E25CSEU1187")
        else:
            st.info("📋 Teacher ID Format: T25CSED101 (Letter + 2digits + 4letters + 3digits)")
            user_id = st.text_input("Teacher ID", placeholder="T25CSED101")
        
        contact = st.text_input("Contact Number (Optional)", placeholder="+91 9876543210")
        email = st.text_input("Email (Optional)", placeholder="your.email@example.com")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("✅ Register", use_container_width=True):
                # Validation
                if not all([name, username, password, confirm_password, user_id]):
                    st.error("❌ All required fields must be filled!")
                elif len(username) < 3:
                    st.error("❌ Username must be at least 3 characters!")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters!")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match!")
                else:
                    # Validate ID format
                    user_id = user_id.upper()
                    if role == "Student":
                        if not re.match(r'^[A-Z]\d{2}[A-Z]{3,4}\d{4}$', user_id):
                            st.error("❌ Invalid Student ID format!")
                            st.stop()
                    else:
                        if not re.match(r'^[A-Z]\d{2}[A-Z]{4}\d{3}$', user_id):
                            st.error("❌ Invalid Teacher ID format!")
                            st.stop()
                    
                    # Check if username or ID exists
                    role_key = 'students' if role == 'Student' else 'teachers'
                    existing_users = st.session_state.app.users.get(role_key, [])
                    
                    if any(u['username'].lower() == username.lower() for u in existing_users):
                        st.error("❌ Username already exists!")
                    elif any(u['id'] == user_id for u in existing_users):
                        st.error("❌ ID already exists!")
                    else:
                        # Create new user with hashed password
                        password_hash, password_salt = hash_password(password)
                        new_user = {
                            'id': user_id,
                            'username': username,
                            'password_hash': password_hash,
                            'password_salt': password_salt,
                            'name': name,
                            'contact': contact if contact else 'Not provided',
                            'email': email if email else 'Not provided'
                        }

                        if role_key not in st.session_state.app.users:
                            st.session_state.app.users[role_key] = []
                        
                        st.session_state.app.users[role_key].append(new_user)
                        st.session_state.app.save_data()
                        
                        st.success(f"✅ Account created successfully! You can now login with username: {username}")
                        _celebration_gif()
        
        with col_b:
            if st.button("← Back to Login", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()

def show_books_page():
    """Display books catalog with programme and special collections."""

    def render_flash_banner():
        reserve_info = st.session_state.pop('reserve_confirmation', None)
        if reserve_info:
            book_title = reserve_info.get('book_title', 'selected book')
            reservation_id = reserve_info.get('reservation_id')
            email_address = reserve_info.get('email')
            email_status = reserve_info.get('email_status', 'unknown')
            base_message = f"📬 Reservation confirmed for **{book_title}**"
            if reservation_id:
                base_message += f" (ID: {reservation_id})"

            if email_status == 'sent' and email_address:
                st.success(f"{base_message}. Confirmation email sent to **{email_address}**.")
            elif email_status == 'failed':
                error_detail = reserve_info.get('email_error')
                detail_suffix = f" Reason: {error_detail}" if error_detail else ''
                st.warning(f"{base_message}. Email notification could not be delivered.{detail_suffix}")
            else:
                st.info(base_message)

        if st.session_state.get('show_borrow_success', False):
            show_borrow_celebration()

        if st.session_state.get('show_return_success', False):
            show_return_celebration(st.session_state.get('return_on_time', True))

    def render_header(title: str, subtitle: str):
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #6C0345 0%, #DC143C 100%); 
                        padding: 0.6rem; border-radius: 8px; margin-bottom: 0.8rem;'>
                <h2 style='color: white; text-align: center; margin: 0; font-size: 1.2rem;'>{title}</h2>
                <p style='color: #F7C566; text-align: center; margin: 0.2rem 0 0 0; font-size: 0.75rem;'>
                    {subtitle}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_book_cards(book_list: list[dict]):
        if not book_list:
            st.info("📭 No titles available in this view yet!")
            return

        search = st.text_input(
            "🔍 Search books",
            placeholder="Search by title or author...",
            label_visibility="collapsed",
        )

        if search:
            term = search.lower()
            book_list = [
                b
                for b in book_list
                if term in b.get('title', '').lower() or term in b.get('author', '').lower()
            ]

        subject_filter = st.session_state.get('selected_subject')
        if subject_filter and subject_filter != 'All Subjects':
            book_list = [
                b for b in book_list if (_ensure_subject_tag(b) or '').lower() == subject_filter.lower()
            ]

        if not book_list:
            st.info("📭 No books found matching your search!")
            return

        st.markdown(
            f"<p style='color: #6C0345; font-weight: 600; margin: 1rem 0;'>Found {len(book_list)} item(s)</p>",
            unsafe_allow_html=True,
        )

        for book in book_list:
            is_borrowable = bool(book.get('borrowable', True))
            available = int(book.get('available', 0))
            copies = int(book.get('copies', 0))
            status_color = "#28a745" if available > 0 else "#dc3545"
            status_text = "Available" if available > 0 else "Not Available"
            status_icon = "✅" if available > 0 else "❌"
            if not is_borrowable:
                status_color = "#17a2b8"
                status_text = "Reference Only"
                status_icon = "📖"

            extra_meta = []
            if book.get('program_category'):
                extra_meta.append(f"🎓 {book['program_category']}")
            if book.get('programme'):
                extra_meta.append(f"🏷️ {book['programme']}")
            if book.get('format'):
                extra_meta.append(f"📄 {book['format']}")
            if book.get('issue_date'):
                extra_meta.append(f"🗓️ {book['issue_date']}")
            if book.get('collection'):
                extra_meta.append(f"📚 {book['collection']}")

            meta_html = """<p style='color: #888888; margin: 0; font-size: 0.8rem;'>""" + " • ".join(extra_meta) + "</p>" if extra_meta else ""

            pdf_url = book.get('pdf_url')
            pdf_html = ""
            if isinstance(pdf_url, str) and pdf_url.strip():
                pdf_html = (
                    "<p style='color: #4facfe; margin: 0.4rem 0 0 0; font-size: 0.8rem;'>"
                    "🔗 <a style='color: #4facfe;' href='{url}' target='_blank'>Read / Download</a>"
                    "</p>"
                ).format(url=pdf_url.strip())

            st.markdown(
                f"""
                <div style='background: #1e1e1e; padding: 1rem; border-radius: 10px; 
                            margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                            border-left: 4px solid {status_color};
                            transition: all 0.3s ease;'>
                    <div style='display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem;'>
                        <div style='flex: 1; min-width: 220px;'>
                            <h3 style='color: #ffffff; margin: 0 0 0.3rem 0; font-size: 1.15rem;'>📖 {book.get('title')}</h3>
                            <p style='color: #b0b0b0; margin: 0 0 0.2rem 0; font-size: 0.9rem;'>✍️ {book.get('author', 'Unknown')}</p>
                            <p style='color: #888888; margin: 0; font-size: 0.8rem;'>🆔 {book.get('id')}</p>
                            {meta_html}
                            {pdf_html}
                        </div>
                        <div style='text-align: center; padding: 0 1rem; min-width: 120px;'>
                            <div style='background: {status_color}; color: white; padding: 0.4rem 0.8rem; 
                                        border-radius: 8px; font-weight: 600; font-size: 0.85rem;'>
                                {status_icon} {status_text}
                            </div>
                            <p style='margin: 0.4rem 0 0 0; font-size: 1.1rem; font-weight: 600; color: #ffffff;'>
                                {available}/{copies}
                            </p>
                            <p style='margin: 0; font-size: 0.75rem; color: #888888;'>Copies</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            action_cols = st.columns(3)

            with action_cols[0]:
                if is_borrowable:
                    if st.button(
                        "📥 Borrow",
                        key=f"borrow_{book['id']}",
                        use_container_width=True,
                    ):
                        st.session_state[f"show_borrow_{book['id']}"] = True
                else:
                    st.button(
                        "📖 Read", key=f"read_{book['id']}", use_container_width=True, disabled=not pdf_url
                    )

            with action_cols[1]:
                if st.button(
                    "👥 Who Has?",
                    key=f"who_{book['id']}",
                    use_container_width=True,
                    disabled=not is_borrowable,
                ):
                    st.session_state[f"show_who_{book['id']}"] = True

            with action_cols[2]:
                if st.button(
                    "ℹ️ Details",
                    key=f"details_{book['id']}",
                    use_container_width=True,
                ):
                    st.session_state[f"show_details_{book['id']}"] = True

            if st.session_state.get(f"show_borrow_{book['id']}", False):
                show_borrow_modal(book)
            if st.session_state.get(f"show_who_{book['id']}", False):
                show_who_has_modal(book)
            if st.session_state.get(f"show_details_{book['id']}", False):
                show_details_modal(book)

            st.markdown("<br>", unsafe_allow_html=True)

    def render_programme_view():
        program_books = st.session_state.app.books.get('program_books', {})
        
        # Initialize session state variables if they don't exist
        if 'role' not in st.session_state:
            st.session_state.role = None
        if 'selected_program' not in st.session_state:
            st.session_state.selected_program = None
            
        if st.session_state.role == 'student' and not st.session_state.selected_program:
            st.session_state.selected_program = st.session_state.user.get('programme')

        categories = list(PROGRAM_CATEGORIES.keys())
        active_program = st.session_state.selected_program

        if st.session_state.role == 'student':
            preferred_category = programme_category(active_program) or programme_category(
                st.session_state.user.get('programme')
            )
            if preferred_category not in categories and categories:
                preferred_category = categories[0]
            with st.expander("🎓 Select Your Programme", expanded=active_program is None):
                col_cat, col_prog = st.columns(2)
                with col_cat:
                    selected_category = (
                        st.selectbox(
                            "Faculty / Discipline",
                            categories,
                            index=categories.index(preferred_category) if preferred_category else 0,
                        )
                        if categories
                        else None
                    )
                with col_prog:
                    programmes = PROGRAM_CATEGORIES.get(selected_category, []) if selected_category else []
                    selected_programme = (
                        st.selectbox(
                            "Programme",
                            programmes,
                            index=programmes.index(active_program)
                            if active_program in programmes
                            else 0,
                        )
                        if programmes
                        else None
                    )

                if programmes and st.button("Set Programme", type="primary"):
                    st.session_state.selected_program = selected_programme
                    if selected_programme:
                        st.session_state.user['programme'] = selected_programme
                        st.session_state.app.save_data()
                    st.rerun()

            active_program = st.session_state.selected_program
            if not active_program:
                st.warning("Please select your programme to see the relevant books.")
                return

        if active_program and active_program not in program_books:
            st.info("No books are available for this programme yet.")
            return

        # Check if subject filter is active
        subject_filter = st.session_state.get('selected_subject')
        if subject_filter and subject_filter != 'All Subjects':
            # If subject filter is active, collect books from ALL programmes with that subject
            book_list = []
            for prog_books in st.session_state.app.books.get('program_books', {}).values():
                for book in prog_books:
                    if (_ensure_subject_tag(book) or '').lower() == subject_filter.lower():
                        book_list.append(book)
        else:
            # Otherwise, show books from the active programme
            book_list = programme_books(active_program) if active_program else []

        # Show latest books from the programme
        latest_books = get_latest_programme_books(active_program, limit=6) if active_program else []
        if latest_books:
            slug = _slugify_program(active_program)
            slider_key = f"latest_slider_{slug}"
            st.session_state.setdefault(slider_key, 0)
            total = len(latest_books)
            current_index = st.session_state[slider_key] % total
            current_book = latest_books[current_index]

            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg, #4facfe 0%, #6C0345 100%); border-radius: 12px; padding: 1.2rem; margin-top: 0.5rem;'>
                    <p style='margin: 0; color: rgba(255,255,255,0.8); letter-spacing: 1px; font-size: 0.7rem;'>LATEST FOR YOUR PROGRAMME</p>
                    <h3 style='margin: 0.3rem 0 0 0; color: #ffffff;'>🔥 Fresh Picks for {active_program}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_prev, col_card, col_next = st.columns([1, 6, 1])
            with col_prev:
                st.write("")
                if total > 1 and st.button("◀", key=f"prev_{slider_key}", use_container_width=True):
                    st.session_state[slider_key] = (current_index - 1) % total
                    st.rerun()

            with col_card:
                availability_badge = (
                    "<span style='background: rgba(40,167,69,0.15); color: #28a745; padding: 0.2rem 0.5rem; border-radius: 999px; font-size: 0.7rem;'>"
                    f"{current_book['available']} / {current_book['copies']} Available"
                    "</span>"
                )
                pdf_url = current_book.get('pdf_url')
                pdf_link = (
                    "<a href='{url}' target='_blank' style='color:#ffe066; text-decoration:none;'>📄 Download</a>"
                ).replace('{url}', pdf_url.strip()) if isinstance(pdf_url, str) and pdf_url.strip() else ""

                st.markdown(
                    """
                    <div style='background: #111111; border-radius: 12px; padding: 1.5rem; margin: 0.8rem 0; box-shadow: 0 8px 16px rgba(0,0,0,0.35);'>
                        <div style='display:flex; flex-direction:column; gap:0.6rem;'>
                            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.6rem;'>
                                <span style='color: rgba(255,255,255,0.6); font-size: 0.75rem;'>Slide {current}/{total}</span>
                                {availability}
                            </div>
                            <h2 style='color:#ffffff; margin:0; font-size:1.4rem;'>{title}</h2>
                            <p style='color: rgba(255,255,255,0.7); margin:0; font-size:0.9rem;'>✍️ {author}</p>
                            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;'>
                                <span style='color: rgba(255,255,255,0.5); font-size:0.8rem;'>🆔 {book_id}</span>
                                {pdf}
                            </div>
                        </div>
                    </div>
                    """.format(
                        current=current_index + 1,
                        total=total,
                        availability=availability_badge,
                        title=current_book['title'],
                        author=current_book['author'],
                        book_id=current_book['id'],
                        pdf=pdf_link,
                    ),
                    unsafe_allow_html=True,
                )

            with col_next:
                st.write("")
                if total > 1 and st.button("▶", key=f"next_{slider_key}", use_container_width=True):
                    st.session_state[slider_key] = (current_index + 1) % total
                    st.rerun()

            st.markdown("<hr style='margin: 0.5rem 0 1rem 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

        render_book_cards(book_list)

    def render_collection_view():
        catalog = collection_catalog()
        if not catalog:
            st.info("New collections will be added soon.")
            return

        collection_names = list(catalog.keys())
        default_collection = st.session_state.get('selected_collection', collection_names[0])
        st.session_state['selected_collection'] = st.sidebar.selectbox(
            "📚 Collection",
            collection_names,
            index=collection_names.index(default_collection) if default_collection in collection_names else 0,
        )

        active_collection = st.session_state['selected_collection']
        items = collection_items(active_collection)
        
        # Apply subject filter if active
        subject_filter = st.session_state.get('selected_subject')
        if subject_filter and subject_filter != 'All Subjects':
            items = [
                item for item in items 
                if (_ensure_subject_tag(item) or '').lower() == subject_filter.lower()
            ]
        
        render_header(
            f"{active_collection} Collection",
            "Special resources, magazines, and reference material",
        )
        render_book_cards(items)

    render_flash_banner()

    if 'books_nav' not in st.session_state:
        st.session_state.books_nav = 'Programmes'

    available_subjects = ['All Subjects'] + all_subjects()
    current_subject = st.session_state.get('selected_subject', 'All Subjects')
    if current_subject not in available_subjects:
        current_subject = 'All Subjects'

    with st.sidebar:
        st.markdown("---")
        st.markdown("**Catalog View**")
        st.session_state.books_nav = st.radio(
            "",
            ["Programmes", "Special Collections"],
            index=0 if st.session_state.books_nav == 'Programmes' else 1,
            label_visibility="collapsed",
        )
        st.markdown("**Filter by Subject**")
        st.session_state.selected_subject = st.selectbox(
            "",
            available_subjects,
            index=available_subjects.index(current_subject),
            label_visibility="collapsed",
        )

    if st.session_state.books_nav == 'Programmes':
        render_header(
            "🎓 Programme Library",
            "Browse books tailored to each academic programme",
        )
        render_programme_view()
    else:
        render_collection_view()

@st.dialog("📥 Borrow Book")
def show_borrow_modal(book):
    """Show borrow confirmation modal"""
    # Book details in modal
    st.markdown(f"""
        <div style='background: #1e1e1e; padding: 1.5rem; border-radius: 10px; 
                    border-left: 4px solid #6C0345; margin-bottom: 1rem;'>
            <h3 style='color: #ffffff; margin: 0 0 0.5rem 0;'>📖 {book['title']}</h3>
            <p style='color: #b0b0b0; margin: 0;'>✍️ by {book['author']}</p>
            <p style='color: #888888; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>🆔 {book['id']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check if user already has this book
    already_borrowed = [t for t in st.session_state.app.transactions 
                       if t['user_id'] == st.session_state.user['id'] 
                       and t['book_id'] == book['id'] 
                       and t['status'] == 'borrowed']
    
    if already_borrowed:
        # Show error - already borrowed
        trans = already_borrowed[0]
        st.error(f"""
        ❌ **You Already Have This Book!**
        
        **Current Borrow Details:**
        - 📅 **Borrowed on:** {trans['borrow_date']}
        - ⏰ **Due date:** {trans['due_date']}
        - 📍 **Status:** Active
        
        💡 **Please return this book before borrowing it again!**
        """)
        
        if st.button("Close", use_container_width=True):
            st.session_state[f"show_borrow_{book['id']}"] = False
            st.rerun()
    
    # Availability status
    elif book['available'] > 0:
        st.success(f"✅ **Available:** {book['available']} of {book['copies']} copies")
        
        # Borrow details
        st.info(f"""
        **📅 Borrow Period:** 14 days  
        **📆 Due Date:** {(datetime.now() + timedelta(days=14)).strftime('%d %B %Y')}  
        **⚠️ Late Fee:** ₹10 per day after due date
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm Borrow", use_container_width=True, type="primary"):
                success = borrow_book(book)
                st.session_state[f"show_borrow_{book['id']}"] = False
                if success:
                    st.session_state['show_borrow_success'] = True
                    st.session_state['borrowed_book_title'] = book['title']
                st.rerun()
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state[f"show_borrow_{book['id']}"] = False
                st.rerun()
    else:
        st.error("❌ **Not Available** - All copies are currently borrowed")

        current_user = st.session_state.user
        existing_reservation = st.session_state.app.get_active_reservation(current_user['id'], book['id'])

        if existing_reservation:
            st.info(
                f"📌 You already reserved this title on **{existing_reservation.get('reserved_at')}**. "
                "We'll notify you when it becomes available."
            )
            st.caption(f"Reservation ID: {existing_reservation.get('id')}")
            if st.button("Close", use_container_width=True):
                st.session_state[f"show_borrow_{book['id']}"] = False
                st.rerun()
            return

        st.info("📬 Reserve this book and we'll email you as soon as a copy is available.")

        default_email = current_user.get('email') if isinstance(current_user.get('email'), str) else ''
        if not default_email or default_email.lower() == 'not provided':
            default_email = ''

        email_state_key = f"reserve_email_{book['id']}"
        if email_state_key not in st.session_state:
            st.session_state[email_state_key] = default_email

        form_key = f"reserve_form_{book['id']}"
        with st.form(form_key):
            email_value = st.text_input(
                "Email address for reservation updates",
                key=email_state_key,
            )
            st.caption("We'll send a confirmation now and alert you again when the book returns.")
            submitted = st.form_submit_button("📬 Reserve Book", type="primary")

        if submitted:
            clean_email = email_value.strip()
            if not clean_email:
                st.warning("⚠️ Please enter your email address so we can notify you.")
            elif '@' not in clean_email or '.' not in clean_email:
                st.warning("⚠️ Enter a valid email (e.g., name@example.com).")
            else:
                # Persist email with user profile
                st.session_state.user['email'] = clean_email
                st.session_state.app.update_user_email(current_user['id'], st.session_state.role, clean_email)

                reservation = st.session_state.app.create_reservation(current_user, book)

                email_status = 'sent'
                email_error = None
                sent, error = send_reservation_email(clean_email, current_user['name'], book, reservation)
                if not sent:
                    email_status = 'failed'
                    email_error = error

                st.session_state['reserve_confirmation'] = {
                    'book_title': reservation.get('book_title'),
                    'reservation_id': reservation.get('id'),
                    'email': clean_email,
                    'email_status': email_status,
                    'email_error': email_error,
                }

                st.session_state[f"show_borrow_{book['id']}"] = False
                st.rerun()

        if st.button("Close", use_container_width=True):
            st.session_state[f"show_borrow_{book['id']}"] = False
            st.rerun()

@st.dialog("👥 Who Has This Book?")
def show_who_has_modal(book):
    """Show who has borrowed this book"""
    st.markdown(f"""
        <div style='background: #1e1e1e; padding: 1rem; border-radius: 10px; 
                    border-left: 4px solid #4facfe; margin-bottom: 1rem;'>
            <h4 style='color: #ffffff; margin: 0;'>📖 {book['title']}</h4>
            <p style='color: #b0b0b0; margin: 0.3rem 0 0 0; font-size: 0.9rem;'>by {book['author']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get borrowers
    borrowers = [t for t in st.session_state.app.transactions 
                 if t['book_id'] == book['id'] and t['status'] == 'borrowed']
    
    if borrowers:
        st.markdown(f"**📊 Currently Borrowed:** {len(borrowers)} of {book['copies']} copies")
        st.divider()
        
        for trans in borrowers:
            # Find user details
            user_details = None
            for role in ['students', 'teachers']:
                user_details = next((u for u in st.session_state.app.users.get(role, []) 
                                   if u['id'] == trans['user_id']), None)
                if user_details:
                    break
            
            if user_details:
                st.markdown(f"""
                    <div style='background: #252525; padding: 1rem; border-radius: 8px; 
                                margin: 0.5rem 0; border-left: 3px solid #ffc107;'>
                        <p style='color: #ffffff; margin: 0; font-weight: 600;'>👤 {trans['user_name']}</p>
                        <p style='color: #b0b0b0; margin: 0.3rem 0 0 0; font-size: 0.85rem;'>
                            📧 {user_details.get('email', 'Not provided')} | 
                            📱 {user_details.get('contact', 'Not provided')}
                        </p>
                        <p style='color: #888888; margin: 0.3rem 0 0 0; font-size: 0.8rem;'>
                            📅 Borrowed: {trans['borrow_date']} | Due: {trans['due_date']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("✅ All copies are available - No one has borrowed this book yet!")
    
    if st.button("Close", use_container_width=True):
        st.session_state[f"show_who_{book['id']}"] = False
        st.rerun()

@st.dialog("ℹ️ Book Details")
def show_details_modal(book):
    """Show complete book details"""
    # Book cover placeholder
    st.markdown("""
        <div style='background: linear-gradient(135deg, #6C0345 0%, #DC143C 100%); 
                    padding: 2rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;'>
            <h1 style='color: white; margin: 0; font-size: 3rem;'>📚</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Book information
    st.markdown(f"""
        <div style='background: #1e1e1e; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;'>
            <h2 style='color: #ffffff; margin: 0 0 1rem 0;'>{book['title']}</h2>
            <p style='color: #b0b0b0; margin: 0.5rem 0;'><strong>✍️ Author:</strong> {book['author']}</p>
            <p style='color: #b0b0b0; margin: 0.5rem 0;'><strong>🆔 Book ID:</strong> {book['id']}</p>
            <p style='color: #b0b0b0; margin: 0.5rem 0;'><strong>📚 Total Copies:</strong> {book['copies']}</p>
            <p style='color: #b0b0b0; margin: 0.5rem 0;'><strong>✅ Available:</strong> {book['available']}</p>
            <p style='color: #b0b0b0; margin: 0.5rem 0;'><strong>📖 Borrowed:</strong> {book['copies'] - book['available']}</p>
        </div>
    """, unsafe_allow_html=True)

    # Availability status
    if book['available'] > 0:
        st.success(f"✅ **Available for borrowing** ({book['available']} copies)")
    else:
        st.error("❌ **Currently unavailable** - All copies are borrowed")

    pdf_url = book.get('pdf_url')
    if pdf_url:
        st.link_button("📄 Download PDF", pdf_url, use_container_width=True)
    
    # Borrow info
    st.info("""
    **📋 Borrowing Information:**
    - Borrow period: 14 days
    - Late fee: ₹10 per day
    - Maximum renewals: 2 times
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if book['available'] > 0:
            if st.button("📥 Borrow This Book", use_container_width=True, type="primary"):
                st.session_state[f"show_details_{book['id']}"] = False
                st.session_state[f"show_borrow_{book['id']}"] = True
                st.rerun()
    with col2:
        if st.button("Close", use_container_width=True):
            st.session_state[f"show_details_{book['id']}"] = False
            st.rerun()

def borrow_book(book):
    """Borrow a book"""
    if book['available'] <= 0:
        st.error(f"❌ '{book['title']}' is not available!")
        return False
    
    # Check if user already has this book
    active_borrows = [t for t in st.session_state.app.transactions 
                     if t['user_id'] == st.session_state.user['id'] 
                     and t['book_id'] == book['id'] 
                     and t['status'] == 'borrowed']
    
    if active_borrows:
        # Show detailed error with due date
        trans = active_borrows[0]
        st.error(f"""
        ❌ **Cannot Borrow - Already Borrowed!**
        
        You already have this book:
        - 📚 **Book:** {book['title']}
        - 📅 **Borrowed on:** {trans['borrow_date']}
        - ⏰ **Due date:** {trans['due_date']}
        
        💡 **Tip:** Please return this book before borrowing it again!
        """)
        return False
    
    # Create transaction
    due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    transaction = {
        'id': len(st.session_state.app.transactions) + 1,
        'user_id': st.session_state.user['id'],
        'user_name': st.session_state.user['name'],
        'book_id': book['id'],
        'book_title': book['title'],
        'book_programme': book.get('programme'),
        'borrow_date': datetime.now().strftime('%Y-%m-%d'),
        'due_date': due_date,
        'return_date': None,
        'status': 'borrowed',
        'fine': 0
    }
    
    st.session_state.app.transactions.append(transaction)
    book['available'] -= 1
    st.session_state.app.save_data()
    st.session_state['borrow_due_date'] = due_date
    
    return True

@st.dialog("🎉 Success!")
def show_borrow_celebration():
    """Show celebration for successful borrow"""
    st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <h1 style='font-size: 4rem; margin: 0;'>🎉</h1>
            <h2 style='color: #28a745; margin: 1rem 0;'>Book Borrowed Successfully!</h2>
            <p style='font-size: 1.2rem; color: #ffffff;'>Happy Reading! 📚</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.success(f"""
    ✅ **{st.session_state.get('borrowed_book_title', 'Book')}** is now yours!
    
    📅 **Due Date:** {st.session_state.get('borrow_due_date', 'N/A')}  
    ⏰ **Remember:** Return on time to avoid late fees!
    """)
    
    _celebration_gif()
    
    if st.button("🎊 Awesome!", use_container_width=True, type="primary"):
        st.session_state['show_borrow_success'] = False
        st.rerun()

@st.dialog("🎊 Returned Successfully!")
def show_return_celebration(on_time=True):
    """Show celebration for successful return"""
    if on_time:
        st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <h1 style='font-size: 4rem; margin: 0;'>🎊</h1>
                <h2 style='color: #28a745; margin: 1rem 0;'>Thank You!</h2>
                <p style='font-size: 1.2rem; color: #ffffff;'>Returned on time! 🌟</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.success(f"""
        ✅ **Book returned successfully!**
        
        🌟 **Great job!** You returned the book on time!  
        💚 **No late fees!** Keep up the good work!  
        📚 **Borrow more books** and keep reading!
        """)
        
        _celebration_gif()
    else:
        st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <h1 style='font-size: 4rem; margin: 0;'>📚</h1>
                <h2 style='color: #ffc107; margin: 1rem 0;'>Book Returned</h2>
                <p style='font-size: 1.2rem; color: #ffffff;'>Thank you! ⏰</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.warning(f"""
        ✅ **Book returned successfully!**
        
        ⚠️ **Late Return:** Please check if any fine applies  
        💡 **Next time:** Try to return on time to avoid fees  
        📚 **Keep reading!**
        """)
    
    if st.button("👍 Got it!", use_container_width=True, type="primary"):
        st.session_state['show_return_success'] = False
        st.rerun()

def my_transactions_page():
    """Display user's transactions"""
    # Show celebration modal if triggered
    if st.session_state.get('show_return_success', False):
        show_return_celebration(st.session_state.get('return_on_time', True))
    
    st.markdown("## 📊 My Transactions")
    
    user_trans = [t for t in st.session_state.app.transactions 
                  if t['user_id'] == st.session_state.user['id']]
    
    if not user_trans:
        st.info("📭 No transactions yet!")
        return
    
    # Tabs for active and history
    tab1, tab2 = st.tabs(["📖 Active Borrows", "📜 History"])
    
    with tab1:
        active = [t for t in user_trans if t['status'] == 'borrowed']
        if active:
            for trans in active:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 2])
                    
                    with col1:
                        st.markdown(f"**📚 {trans['book_title']}**")
                        st.caption(f"Book ID: {trans['book_id']}")
                    
                    with col2:
                        st.write(f"**Due:** {trans['due_date']}")
                        if trans['fine'] > 0:
                            st.error(f"Fine: ₹{trans['fine']}")
                    
                    with col3:
                        if st.button("↩️ Return", key=f"return_{trans['id']}"):
                            return_book(trans)
                    
                    st.divider()
        else:
            st.info("No active borrows")
    
    with tab2:
        history = [t for t in user_trans if t['status'] == 'returned']
        if history:
            # Display as table
            st.markdown("**Transaction History**")
            for trans in history:
                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(f"**{trans['book_title']}**")
                    with col2:
                        st.write(f"Borrowed: {trans['borrow_date']}")
                    with col3:
                        st.write(f"Returned: {trans['return_date']}")
                    with col4:
                        if trans['fine'] > 0:
                            st.error(f"Fine: ₹{trans['fine']}")
                        else:
                            st.success("No fine")
                    st.divider()
        else:
            st.info("No history yet")

def return_book(trans):
    """Return a book"""
    trans['status'] = 'returned'
    trans['return_date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Calculate fine
    due_date = datetime.strptime(trans['due_date'], '%Y-%m-%d')
    return_date = datetime.now()
    days_late = (return_date - due_date).days
    
    on_time = days_late <= 0
    
    if days_late > 0:
        trans['fine'] = days_late * 10
    
    # Update book availability
    programme = trans.get('book_programme')
    if programme:
        book = next((b for b in programme_books(programme) if b['id'] == trans['book_id']), None)
    else:
        book = next((b for b in st.session_state.app.books['teacher_books'] if b['id'] == trans['book_id']), None)
    if book:
        book['available'] += 1
    
    st.session_state.app.save_data()
    
    # Trigger celebration modal
    st.session_state['show_return_success'] = True
    st.session_state['return_on_time'] = on_time
    st.rerun()

def logout():
    """Logout user and reset session state"""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.page = 'login'
    st.rerun()

def main():
    """Main application"""
    
    # Check if page state exists
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    
    # Not logged in
    if not st.session_state.logged_in:
        if st.session_state.page == 'register':
            register_page()
        else:
            login_page()
        return
    
    # Logged in - Show sidebar
    with st.sidebar:
        # Compact user info
        st.markdown(f"""
            <div style='background: #1e1e1e; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;
                        border-left: 3px solid #6C0345;'>
                <p style='margin: 0; font-size: 1rem; font-weight: 600; color: #ffffff;'>👤 {st.session_state.user['name']}</p>
                <p style='margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #b0b0b0;'>{st.session_state.role.title()} • {st.session_state.user['id']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Navigation**")
        if st.session_state.role == 'admin':
            menu = st.radio("", ["📊 Dashboard", "📚 Books", "🚪 Logout"], label_visibility="collapsed")
        else:
            menu = st.radio("", ["📚 View Books", "📊 My Transactions", "🚪 Logout"], label_visibility="collapsed")
        
        if menu == "🚪 Logout":
            logout()
    
    # Main content
    if st.session_state.role == 'admin':
        if menu == "📊 Dashboard":
            admin_dashboard()
        elif menu == "📚 Books":
            show_books_page()
    else:
        if menu == "📚 View Books":
            show_books_page()
        elif menu == "📊 My Transactions":
            my_transactions_page()

if __name__ == "__main__":
    main()
