"""
Journey System Enums

This module contains all enumeration types used throughout the Journey System.
"""

from enum import Enum


class CategoryType(str, Enum):
    """Categories for reflection sources and insights"""
    PERSONAL_GROWTH = "personal_growth"
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    HEALTH_WELLNESS = "health_wellness"
    SPIRITUALITY = "spirituality"
    CREATIVITY = "creativity"
    LEARNING = "learning"
    LEADERSHIP = "leadership"
    COMMUNICATION = "communication"
    GOALS_ACHIEVEMENT = "goals_achievement"
    MINDSET = "mindset"
    HABITS = "habits"
    VALUES = "values"
    PURPOSE = "purpose"
    CHALLENGES = "challenges"
    CELEBRATIONS = "celebrations"
    OTHER = "other"


class DocumentType(str, Enum):
    """Types of documents that can be processed"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    RTF = "rtf"
    ODT = "odt"
    MD = "md"
    HTML = "html"


class ProcessingStatus(str, Enum):
    """Status of document or reflection processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReviewStatus(str, Enum):
    """Review status for insights and reflections"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"