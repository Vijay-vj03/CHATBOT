import streamlit as st
import requests
import json
from typing import List, Dict, Any
import os
from datetime import datetime
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Multimodal RAG Assistant",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI - Updated Sept 2025
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles - main content only */
    .main {
        padding-top: 2rem;
    }
    
    /* Custom font for the entire app */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e1e8ed;
        margin-bottom: 1rem;
    }
    
    /* Message styles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 5px 18px;
        margin: 1rem 0;
        margin-left: 20%;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2c3e50;
        padding: 1.5rem;
        border-radius: 18px 18px 18px 5px;
        margin: 1rem 0;
        margin-right: 20%;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    /* File upload area */
    .upload-area {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    /* Sidebar styles - keep simple */
    /* No special sidebar styling */
    
    /* Metrics cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e1e8ed;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Source cards */
    .source-card {
        background: #ffffff;
        border: 1px solid #e1e8ed;
        border-left: 4px solid #2196f3;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        color: #2c3e50;
    }
    
    /* Success/Error messages */
    .success-msg {
        background: linear-gradient(135deg, #d4edda 0%, #f8f9fa 100%);
        color: #155724;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .error-msg {
        background: linear-gradient(135deg, #f8d7da 0%, #f8f9fa 100%);
        color: #721c24;
        border: 1px solid #f5c6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Button styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e1e8ed;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Spinner customization */
    .stSpinner > div > div {
        border-color: #667eea;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def upload_file(file) -> Dict[str, Any]:
    """Upload file to backend"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{BACKEND_URL}/upload", files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None

def query_chatbot(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Query the chatbot"""
    try:
        payload = {
            "query": query,
            "max_results": max_results
        }
        response = requests.post(f"{BACKEND_URL}/query", json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Query failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return None

# Add caching to prevent excessive API calls
@st.cache_data(ttl=5)  # Cache for 5 seconds
def get_documents_cached():
    """Get list of uploaded documents with caching"""
    try:
        response = requests.get(f"{BACKEND_URL}/documents")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching documents: {str(e)}")
        return []

def get_documents() -> List[Dict[str, Any]]:
    """Get list of uploaded documents"""
    try:
        response = requests.get(f"{BACKEND_URL}/documents")
        if response.status_code == 200:
            return response.json().get("documents", [])
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching documents: {str(e)}")
        return []

def delete_document(document_id: str) -> bool:
    """Delete a document"""
def delete_document(document_id: str):
    """Delete a specific document"""
    try:
        response = requests.delete(f"{BACKEND_URL}/documents/{document_id}")
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to delete document: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")
        return False

def clear_all_documents():
    """Clear all documents"""
    try:
        response = requests.delete(f"{BACKEND_URL}/documents")
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to clear documents: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error clearing documents: {str(e)}")
        return False

def display_modern_header():
    """Display modern header with branding"""
    st.markdown("""
    <div class="main-header">
        <h1>� Multimodal RAG Assistant</h1>
        <p>Intelligent document analysis with AI-powered insights • Upload • Chat • Discover</p>
    </div>
    """, unsafe_allow_html=True)

def display_metrics(documents):
    """Display metrics in modern cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(documents)}</div>
            <div class="metric-label">📄 Documents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{sum(1 for doc in documents if doc.get('file_type', '').startswith('application/pdf'))}</div>
            <div class="metric-label">📑 PDFs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{sum(1 for doc in documents if doc.get('file_type', '').startswith('audio/'))}</div>
            <div class="metric-label">🎵 Audio</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{sum(1 for doc in documents if doc.get('file_type', '').startswith('video/'))}</div>
            <div class="metric-label">🎬 Video</div>
        </div>
        """, unsafe_allow_html=True)

def display_chat_message(message, is_user=True):
    """Display chat message with modern styling"""
    if is_user:
        st.markdown(f"""
        <div class="user-message">
            <strong>👤 You:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <strong>🤖 Assistant:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)

def display_sources(sources):
    """Display sources with modern card styling"""
    if sources:
        st.markdown("### 📚 Sources")
        for i, source in enumerate(sources, 1):
            filename = source.get('filename', 'Unknown')
            content = source.get('content', '')[:200] + "..." if len(source.get('content', '')) > 200 else source.get('content', '')
            
            st.markdown(f"""
            <div class="source-card">
                <strong>📄 Source {i}: {filename}</strong><br>
                <em>{content}</em>
            </div>
            """, unsafe_allow_html=True)

def main():
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "documents" not in st.session_state:
        st.session_state.documents = []
    
    # Prevent file re-upload loops by tracking processed files
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = set()
    
    # Prevent duplicate processing on page refresh
    if 'page_loaded' not in st.session_state:
        st.session_state.page_loaded = True
        st.session_state.processed_files = set()

    # Display modern header
    display_modern_header()
    
    # Get documents and update session state
    documents = get_documents()
    st.session_state.documents = documents
    
    # Display metrics
    display_metrics(documents)
    
    # Sidebar for file upload and document management  
    with st.sidebar:
        st.header("📁 Document Management")
        
        # File upload section
        uploaded_files = st.file_uploader(
            "Upload Document",
            type=['pdf', 'wav', 'mp3', 'mp4', 'avi', 'mov', 'mkv', 'm4a', 'flac'],
            help="Supported formats: PDF, Audio files, Video files",
            accept_multiple_files=True  # Allow multiple file uploads
        )
        
        # Add file upload prevention logic
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_key = f"{uploaded_file.name}_{uploaded_file.size}"
                
                if file_key not in st.session_state.processed_files:
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        success = upload_file(uploaded_file)
                        if success:
                            st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                            st.session_state.processed_files.add(file_key)
                            # Force refresh of documents list without rerun
                            if 'documents' in st.session_state:
                                del st.session_state['documents']
                        else:
                            st.error(f"❌ Failed to upload {uploaded_file.name}")
        
        st.subheader("📚 Uploaded Documents")
        if documents:
            for idx, doc in enumerate(documents):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {doc.get('filename', 'Unknown')}")
                    st.caption(f"Type: {doc.get('file_type', 'Unknown')}")
                with col2:
                    # Create unique key using index and filename
                    unique_key = f"delete_{idx}_{doc.get('filename', 'unknown').replace(' ', '_').replace('.', '_')}"
                    if st.button("🗑️", key=unique_key, help=f"Delete {doc.get('filename', 'Unknown')}", use_container_width=True):
                        doc_id = doc.get('id', doc.get('filename', ''))  # Use filename as fallback if no ID
                        if delete_document(doc_id):
                            st.success(f"Deleted {doc.get('filename', 'Unknown')}")
                            st.rerun()
                        else:
                            st.error("Failed to delete document")
        else:
            st.info("No documents uploaded yet.")
        
        # Clear all documents button
        if documents:
            st.markdown("---")
            # Fix the clear all documents button handler
            if st.button("🗑️ Clear All Documents", use_container_width=True, type="secondary"):
                        if clear_all_documents():
                            st.success("All documents cleared successfully!")
                            # Clear cache instead of rerun
                            if 'documents' in st.session_state:
                                del st.session_state['documents']
                            st.cache_data.clear()
                        else:
                            st.error("Failed to clear documents")        # Add manual refresh button
        if st.button("🔄 Refresh Documents", help="Manually refresh document list"):
            # Clear cache and refresh
            if 'documents' in st.session_state:
                del st.session_state['documents']
            if 'documents_timestamp' in st.session_state:
                del st.session_state['documents_timestamp']
            st.cache_data.clear()  # Clear all cached data
            st.rerun()
    
    # Main chat interface
    st.markdown("### 💬 Chat with Your Documents")
    
    # Display chat messages
    if st.session_state.messages:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            if message["role"] == "user":
                display_chat_message(message["content"], is_user=True)
            else:
                display_chat_message(message["content"], is_user=False)
                # Display sources if available
                if "sources" in message:
                    display_sources(message["sources"])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="chat-container">
            <div class="assistant-message">
                <strong>🤖 Assistant:</strong><br>
                Hello! I'm your multimodal RAG assistant. Upload some documents and ask me anything about their content. 
                I can analyze PDFs, transcribe audio, and extract information from videos!
                <br><br>
                <strong>Try asking:</strong>
                <ul>
                    <li>"What are the main topics in my documents?"</li>
                    <li>"Summarize the key points from my uploaded files"</li>
                    <li>"What did the speaker mention about [topic]?"</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick action buttons
    if documents:
        st.markdown("### 🎯 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Summarize All", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Please provide a comprehensive summary of all my uploaded documents."})
                st.rerun()
        
        with col2:
            if st.button("🔍 Key Topics", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "What are the main topics and themes across all my documents?"})
                st.rerun()
        
        with col3:
            if st.button("❓ Q&A Insights", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Generate some interesting questions and answers based on my document content."})
                st.rerun()
    
    # Chat input section - moved to bottom
    st.markdown("### ✍️ Ask a Question")
    user_input = st.text_area(
        "Type your question here...",
        placeholder="Ask me anything about your uploaded documents...",
        height=100,
        key="user_input"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Send Message", type="primary", use_container_width=True):
            if user_input.strip():
                if not documents:
                    st.warning("⚠️ Please upload some documents first before asking questions!")
                else:
                    # Add user message to chat
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    
                    # Query the backend
                    with st.spinner("🤔 Thinking..."):
                        response = query_chatbot(user_input)
                    
                    if response:
                        answer = response.get('answer', 'No answer received')
                        sources = response.get('sources', [])
                        
                        # Add assistant message to chat
                        message_data = {"role": "assistant", "content": answer}
                        if sources:
                            message_data["sources"] = sources
                        st.session_state.messages.append(message_data)
                    else:
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "❌ Sorry, I couldn't process your question. Please try again."
                        })
                    
                    # Clear input and rerun
                    st.rerun()
            else:
                st.warning("⚠️ Please enter a question before sending!")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7; margin-top: 2rem;">
        <small>🚀 Powered by FastAPI • Streamlit • ChromaDB • Google Gemini</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
