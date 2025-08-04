"""
models.py - Pydantic models for CodeFix MVP

This file defines the BugReport model, which represents a single bug report submitteed by a user.
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BugReport(BaseModel):
    """
    BugReport defines the structure of a bug report submitted to the CodeFix API.

    This Pydantic model helps FastAPI check if incoming bug reports are valid, and auto-generates helpful docs for API.

    Fields:
    - id: Optional auto-generated unique identifier
    - title: Short headline describing the bug
    - description: Main body of the report explaining the issue
    - steps_to_reproduce: Step-by-step guide to trigger the bug (optional)
    - expected_behavior: What the user thought would happen (optional)
    - actual_behavior: What actually happened (optional)
    - code_snippet: Code that might be causing the bug (optional)
    - language: Programming language of the code (optional)
    - created_at: Timestamp auto-filled when the report is created
    - resolved: Whether the bug has been fixed yet
    """

    id: Optional[int] = Field(
        default=None,
        description="Unique identifier for the bug report (usually set by the database)"
    )

    title: str = Field(
        ...,
        example="App crashes on login",
        description="Short summary of the issue"
    )

    description: str = Field(
        ...,
        example="The app crashes when I try to log in with a valid account.",
        description="Detailed description of the bug"
    )

    steps_to_reproduce: Optional[str] = Field(
        default=None,
        example="1. Open the app\n2. Enter credentials\n3. Tap login",
        description="Steps someone else could follow to reproduce the bug"
    )

    expected_behavior: Optional[str] = Field(
        default=None,
        example="App should log in and redirect to dashboard",
        description="What the user expected to happen"
    )

    actual_behavior: Optional[str] = Field(
        default=None,
        example="App crashes with a NullPointerException",
        description="What actually happened instead"
    )

    code_snippet: Optional[str] = Field(
        default=None,
        example="const result = user && user.token;",
        description="The relevant piece of code where the bug might be"
    )

    language: Optional[str] = Field(
        default=None,
        example="JavaScript",
        description="Programming language of the code snippet"
    )

    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the report was created"
    )

    resolved: bool = Field(
        default=False,
        description="True if the bug has been resolved"
    )

    class Config:
        orm_mode = True  # Allows compatibility with ORMs 
