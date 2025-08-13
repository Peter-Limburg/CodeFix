"""
CodeFix Demo Interface - Streamlit App

A simple interface for testing the CodeFix AI bug analysis system.
"""

import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    "analyze_bug": f"{API_BASE_URL}/analyze-bug",
    "health": f"{API_BASE_URL}/health",
    "metrics": f"{API_BASE_URL}/metrics"
}

def check_api_health():
    """Check if the CodeFix API is running."""
    try:
        response = requests.get(API_ENDPOINTS["health"], timeout=5)
        return response.status_code == 200, response.json()
    except requests.exceptions.RequestException:
        return False, None

def analyze_bug(bug_data):
    """Send bug report to the API for analysis."""
    try:
        response = requests.post(
            API_ENDPOINTS["analyze_bug"],
            json=bug_data,
            timeout=30
        )
        return response.status_code == 200, response.json()
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

def get_api_metrics():
    """Get API performance metrics."""
    try:
        response = requests.get(API_ENDPOINTS["metrics"], timeout=5)
        return response.status_code == 200, response.json()
    except requests.exceptions.RequestException:
        return False, None

def main():
    st.set_page_config(
        page_title="CodeFix AI Demo",
        page_icon="🐛",
        layout="wide"
    )
    
    st.title("🐛 CodeFix AI - Bug Analysis Demo")
    st.markdown("AI-powered bug analysis using semantic similarity search")
    
    # Check API health
    st.header("🔍 System Status")
    health_ok, health_data = check_api_health()
    
    if health_ok:
        st.success("✅ CodeFix API is running!")
        
        # Display health metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", health_data.get("status", "Unknown"))
        with col2:
            uptime = health_data.get("uptime_seconds", 0)
            st.metric("Uptime", f"{uptime:.1f}s")
        with col3:
            st.metric("Total Requests", health_data.get("api", {}).get("total_requests", 0))
            
    else:
        st.error("❌ CodeFix API is not running!")
        st.info("Please start the API with: `python main.py`")
        st.stop()
    
    # Main demo interface
    st.header("🚀 Try the AI Bug Analysis")
    
    # Bug report form
    with st.form("bug_report_form"):
        st.subheader("Submit a Bug Report")
        
        title = st.text_input(
            "Bug Title",
            placeholder="e.g., React component not updating when state changes",
            help="Brief description of the issue"
        )
        
        description = st.text_area(
            "Detailed Description",
            placeholder="Describe what's happening, what you expected, and any error messages...",
            help="Provide as much detail as possible for better AI analysis",
            height=120
        )
        
        code_snippet = st.text_area(
            "Code Snippet (Optional)",
            placeholder="Paste the relevant code that's causing the issue...",
            help="Code snippets help the AI understand the context better",
            height=100
        )
        
        tech_stack = st.selectbox(
            "Technology Stack",
            ["react", "javascript", "python", "java", "other"],
            help="Select the primary technology involved"
        )
        
        submitted = st.form_submit_button("🔍 Analyze Bug", type="primary")
    
    # Process form submission
    if submitted:
        if not title or not description:
            st.error("Please provide both a title and description for the bug.")
        else:
            # Prepare bug report
            bug_data = {
                "title": title,
                "description": description,
                "code_snippet": code_snippet if code_snippet else None,
                "language": tech_stack,
                "tech_stack": tech_stack
            }
            
            # Show loading state
            with st.spinner("🤖 AI is analyzing your bug..."):
                success, result = analyze_bug(bug_data)
            
            if success:
                st.success("✅ AI Analysis Complete!")
                
                # Display the solution
                st.subheader("🎯 AI Solution")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**{result['title']}**")
                    st.markdown(result['solution'])
                    
                    # Code example
                    if result.get('code_example'):
                        st.subheader("💻 Code Example")
                        st.code(result['code_example'], language='javascript')
                
                with col2:
                    # Confidence and metadata
                    confidence_color = "green" if result['confidence'] > 0.7 else "orange" if result['confidence'] > 0.5 else "red"
                    st.metric("AI Confidence", f"{result['confidence']:.1%}")
                    
                    if result.get('similarity_score'):
                        st.metric("Similarity Score", f"{result['similarity_score']:.3f}")
                    
                    st.markdown("**Tags:**")
                    for tag in result.get('tags', []):
                        st.markdown(f"- `{tag}`")
                    
                    st.markdown(f"**Source:** {result.get('source', 'Unknown')}")
                
                # Show raw response for debugging
                with st.expander("🔍 Raw AI Response"):
                    st.json(result)
                    
            else:
                st.error("❌ Failed to analyze bug")
                if isinstance(result, dict) and "detail" in result:
                    st.error(f"Error: {result['detail']}")
                else:
                    st.error("Unknown error occurred. Check the API logs.")
    
    # API Metrics
    st.header("📊 API Performance")
    metrics_ok, metrics_data = get_api_metrics()
    
    if metrics_ok:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Requests", metrics_data.get("api", {}).get("total_requests", 0))
        with col2:
            st.metric("Error Rate", f"{metrics_data.get('api', {}).get('error_count', 0)}")
        with col3:
            st.metric("AI Requests", metrics_data.get("api", {}).get("analyze_requests", 0))
        with col4:
            avg_time = metrics_data.get("performance", {}).get("avg_response_time_ms", 0)
            st.metric("Avg Response Time", f"{avg_time:.0f}ms")
    else:
        st.warning("Unable to fetch metrics")
    
    # Example bug reports
    st.header("💡 Example Bug Reports to Try")
    
    examples = [
        {
            "title": "React State Mutation",
            "description": "My React component won't update when I add items to the todo list. I'm using useState but the screen doesn't refresh.",
            "code": "const addTodo = () => { todos.push(newItem); setTodos(todos); }"
        },
        {
            "title": "useEffect Infinite Loop", 
            "description": "My useEffect hook is running infinitely and causing the app to crash with 'Maximum call stack size exceeded' error.",
            "code": "useEffect(() => { setCount(count + 1); }, []);"
        },
        {
            "title": "Event Handler Binding",
            "description": "My button click handler isn't working. The function is defined but nothing happens when I click the button.",
            "code": "<button onClick={this.handleClick}>Click me</button>"
        }
    ]
    
    for i, example in enumerate(examples):
        with st.expander(f"Example {i+1}: {example['title']}"):
            st.markdown(f"**Description:** {example['description']}")
            if example['code']:
                st.code(example['code'], language='javascript')
            
            # Quick test button
            if st.button(f"Test Example {i+1}", key=f"test_{i}"):
                test_data = {
                    "title": example["title"],
                    "description": example["description"],
                    "code_snippet": example["code"],
                    "language": "javascript",
                    "tech_stack": "react"
                }
                
                with st.spinner("Testing example..."):
                    success, result = analyze_bug(test_data)
                
                if success:
                    st.success(f"✅ AI found solution with {result['confidence']:.1%} confidence!")
                    st.markdown(f"**Solution:** {result['title']}")
                else:
                    st.error("❌ Failed to analyze example")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**CodeFix AI** - Built with real AI/ML engineering practices. "
        "This demo showcases semantic similarity search for bug analysis."
    )

if __name__ == "__main__":
    main()
