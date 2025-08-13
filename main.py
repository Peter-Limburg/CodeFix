"""
CodeFix API - AI-powered bug analysis and solution suggestions

This FastAPI application provides endpoints for analyzing code bugs and suggesting solutions.
It's designed to be a lean MVP that can be extended with more advanced AI features.

Key Learning Concepts for me in this file (7):
- FastAPI application structure and configuration
- RESTful API design patterns
- Error handling and validation
- Health monitoring and metrics collection
- CORS configuration for frontend integration
- Pydantic models for request/response validation
- Global state management for simple metrics

Author: Peter L.
Version: 1.0.0
"""

# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import uvicorn
import time
import psutil  # For system monitoring (CPU, memory, etc.)
from datetime import datetime
from typing import Dict, Any

# Import our custom data models (these define the structure of our API requests/responses)
from models import BugReport, BugSolution

# Import AI engine for bug analysis
from ai_engine import BugSolutionAI

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================

# Create the FastAPI application instance with metadata
# This metadata appears in the automatically generated API documentation
app = FastAPI(
    title="CodeFix API",
    description="AI-powered bug analysis and solution suggestions",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI documentation endpoint
    redoc_url="/redoc"     # Alternative ReDoc documentation endpoint
)

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

# CORS (Cross-Origin Resource Sharing) middleware
# This allows my frontend (running on a different port/domain) to call this API
# IMPORTANT: In production, replace "*" with specific allowed origins for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow requests from any origin (CHANGE IN PRODUCTION!)
    allow_credentials=True,       # Allow cookies/auth headers
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)

# =============================================================================
# GLOBAL VARIABLES FOR METRICS TRACKING
# =============================================================================

# Simple in-memory metrics (in production, I'd use a proper metrics system like Prometheus)
app_start_time = time.time()    # When the app started (for uptime calculation)
request_count = 0               # Total number of requests received
error_count = 0                 # Total number of errors encountered
analyze_bug_count = 0           # Number of bug analysis requests specifically

# =============================================================================
# AI ENGINE INITIALIZATION
# =============================================================================

# Initialize the AI engine (this will load the model and examples)
print("🚀 Initializing CodeFix AI Engine...")
ai_engine = BugSolutionAI()
print("✅ AI Engine initialized successfully!")

# =============================================================================
# ROOT ENDPOINT
# =============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - provides API overview and navigation
    
    This is the first endpoint users hit when they visit my API.
    It should provide helpful information about what my API does
    and how to use it.
    
    Returns:
        dict: API information and available endpoints
        
    Learning Notes:
    - The @app.get() decorator creates a GET endpoint
    - async/await allows the server to handle multiple requests efficiently
    - Return dictionaries are automatically converted to JSON responses
    """
    return {
        "message": "CodeFix API is running! 🐛→✅",
        "version": "1.0.0",
        "docs": "/docs",           # Link to interactive API documentation
        "health": "/health",       # Link to health check endpoint
        "metrics": "/metrics",     # Link to metrics endpoint
        "endpoints": {
            "analyze_bug": "POST /analyze-bug",    # Main functionality
            "health_check": "GET /health",         # System health status
            "metrics": "GET /metrics"              # Performance metrics
        }
    }

# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    
    This endpoint tells you if your API is running properly and provides
    system information. Load balancers and monitoring systems use this
    to determine if they should send traffic to this instance.
    
    Returns:
        dict: Health status including system metrics and API statistics
        
    Raises:
        HTTPException: 500 error if health check fails
        
    Learning Notes:
    - Health checks are crucial for production deployments
    - psutil library provides cross-platform system information
    - Global variables track simple metrics across requests
    - Exception handling prevents the health check itself from breaking
    """
    global request_count, error_count
    request_count += 1
    
    try:
        # Calculate how long the API has been running
        current_time = datetime.now()
        uptime = time.time() - app_start_time
        
        # Get current system resource usage
        memory_usage = psutil.virtual_memory()  # RAM usage information
        cpu_usage = psutil.cpu_percent()        # Current CPU usage percentage
        
        # Build the health status response
        health_status = {
            "status": "healthy",                           # Overall health status
            "timestamp": current_time.isoformat(),         # When this check was performed
            "uptime_seconds": round(uptime, 2),           # How long the API has been running
            "version": "1.0.0",                           # API version
            "system": {
                "memory_usage_percent": memory_usage.percent,                    # % of RAM used
                "memory_available_mb": round(memory_usage.available / (1024 * 1024), 2),  # Available RAM in MB
                "cpu_usage_percent": cpu_usage                                   # % of CPU used
            },
            "api": {
                "total_requests": request_count,        # Total requests since startup
                "error_count": error_count,             # Total errors since startup
                "analyze_requests": analyze_bug_count   # Bug analysis requests specifically
            }
        }
        
        # Check if system resources are getting low (simple alerting)
        if memory_usage.percent > 90 or cpu_usage > 95:
            health_status["status"] = "degraded"
            health_status["warnings"] = []
            
            if memory_usage.percent > 90:
                health_status["warnings"].append("High memory usage")
            if cpu_usage > 95:
                health_status["warnings"].append("High CPU usage")
        
        return health_status
        
    except Exception as e:
        # If the health check itself fails, that's a serious problem
        error_count += 1
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# =============================================================================
# METRICS ENDPOINT
# =============================================================================

@app.get("/metrics")
async def get_metrics():
    """
    Metrics endpoint for monitoring and analytics
    
    Provides detailed performance and usage statistics about the API.
    This is useful for monitoring, alerting, and understanding usage patterns.
    
    Returns:
        dict: Comprehensive metrics including performance and system stats
        
    Learning Notes:
    - Metrics help you understand how your API is performing
    - Success rate calculation shows reliability
    - Performance metrics help identify bottlenecks
    - In production, you'd typically use dedicated monitoring tools
    """
    global request_count, error_count, analyze_bug_count
    request_count += 1
    
    uptime = time.time() - app_start_time
    
    metrics = {
        "service": "codefix-api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        
        # Uptime information in different units for convenience
        "uptime": {
            "seconds": round(uptime, 2),
            "minutes": round(uptime / 60, 2),
            "hours": round(uptime / 3600, 2)
        },
        
        # Request statistics and reliability metrics
        "requests": {
            "total": request_count,
            "analyze_bug": analyze_bug_count,
            "errors": error_count,
            # Success rate = (successful requests / total requests) * 100
            "success_rate": round((request_count - error_count) / max(request_count, 1) * 100, 2)
        },
        
        # Current system resource usage
        "system": {
            "memory_usage_percent": psutil.virtual_memory().percent,
            "cpu_usage_percent": psutil.cpu_percent(),
            "disk_usage_percent": psutil.disk_usage('/').percent
        },
        
        # Performance calculations
        "performance": {
            # Average requests per minute since startup
            "avg_requests_per_minute": round(request_count / max(uptime / 60, 1), 2),
            # Percentage of requests that resulted in errors
            "error_rate_percent": round(error_count / max(request_count, 1) * 100, 2)
        }
    }
    
    return metrics

# =============================================================================
# MAIN BUSINESS LOGIC ENDPOINT
# =============================================================================

@app.post("/analyze-bug", response_model=BugSolution)
async def analyze_bug(bug_report: BugReport):
    """
    Analyze a bug report and return suggested solutions
    
    This is the core functionality of the API. It receives a bug report,
    analyzes it, and returns potential solutions with confidence scores.
    
    Args:
        bug_report (BugReport): The bug report data from the client
        
    Returns:
        BugSolution: A solution object with code examples and confidence score
        
    Raises:
        HTTPException: 422 for validation errors, 404 if no solution found, 500 for server errors
        
    Process Flow:
    1. Validate the incoming bug report using Pydantic
    2. Search for similar known bugs (TODO: implement in mock_rag.py)
    3. Generate or retrieve the best matching solution
    4. Return the solution with metadata
    
    Learning Notes:
    - @app.post() creates a POST endpoint (for sending data TO the server)
    - response_model automatically validates the response and generates API docs
    - FastAPI automatically parses JSON into Pydantic models
    - Global variables track metrics across all requests
    - Try-except blocks handle different types of errors appropriately
    """
    global request_count, analyze_bug_count, error_count
    request_count += 1
    analyze_bug_count += 1
    
    # Track how long this request takes to process
    start_time = time.time()
    
    try:
        # Log the incoming request (in production, use proper logging framework)
        print(f"[{datetime.now()}] Analyzing bug: {bug_report.title[:50]}...")
        
        # =================================================================
        # AI-POWERED BUG ANALYSIS
        # =================================================================
        # Use the AI engine to find the best matching solution
        
        # Find solution using semantic similarity search
        solution = ai_engine.find_solution(bug_report)
        
        if not solution:
            # No confident match found
            raise HTTPException(
                status_code=404, 
                detail="No confident solution found for this bug type. Try providing more details about the issue."
            )
        
        # Calculate and log processing time
        processing_time = round(time.time() - start_time, 3)
        print(f"[{datetime.now()}] Solution found in {processing_time}s with confidence: {solution.confidence}")
        
        return solution
        
    except ValidationError as e:
        # Pydantic validation failed - the request data is malformed
        error_count += 1
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    
    except Exception as e:
        # Unexpected error occurred during processing
        error_count += 1
        print(f"[{datetime.now()}] Error analyzing bug: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while analyzing the bug report"
        )

# =============================================================================
# FUTURE ENDPOINTS (TODO)
# =============================================================================

# Uncomment and implement these as you add more features:

# @app.get("/examples")
# async def get_examples():
#     """
#     Get available bug examples for development/testing
#     
#     This endpoint could return sample bug reports that developers
#     can use to test the API without creating their own data.
#     """
#     pass

# @app.post("/feedback")
# async def submit_feedback(feedback: UserFeedback):
#     """
#     Submit user feedback for solution improvement
#     
#     Allow users to rate solutions and provide feedback to improve
#     the AI's recommendations over time.
#     """
#     pass

# @app.get("/stats")
# async def get_solution_stats():
#     """
#     Get statistics about solution effectiveness
#     
#     Show which types of bugs are most common, which solutions
#     are most helpful, etc.
#     """
#     pass

# =============================================================================
# APPLICATION STARTUP
# =============================================================================

if __name__ == "__main__":
    """
    Application entry point
    
    This code runs when you execute the script directly (python main.py).
    It starts the FastAPI server with uvicorn.
    
    Learning Notes:
    - uvicorn is an ASGI server that runs FastAPI applications
    - reload=True automatically restarts the server when code changes (development only!)
    - host="0.0.0.0" allows connections from other machines (use "127.0.0.1" for localhost only)
    - The server will be accessible at http://localhost:8000
    """
    print("🚀 Starting CodeFix API...")
    print("📚 API documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("\nNext steps:")
    print("1. Visit http://localhost:8000/docs to see the interactive API documentation")
    print("2. Test the endpoints using the built-in interface")
    print("3. Implement mock_rag.py for actual bug solution matching")
    print("4. Create prompts.py for AI prompt generation")
    print("5. Replace placeholder logic in analyze_bug() with real implementation")
    
    uvicorn.run(
        "main:app",           # Module and app instance to run
        host="0.0.0.0",       # Listen on all network interfaces
        port=8000,            # Port to listen on
        reload=True,          # Auto-reload on code changes (REMOVE IN PRODUCTION!)
        log_level="info"      # Logging level
    )