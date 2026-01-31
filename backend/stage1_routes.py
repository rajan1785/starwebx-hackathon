from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
import json

from database import get_db
from models import (
    User, MCQQuestion, ProgrammingProblem, MCQAttempt, 
    ProgrammingQuestionAttempt, Stage1Result, Notification, ActivityLog
)
from schemas import (
    MCQQuestionResponse, MCQAnswerSubmit, ProgrammingProblemResponse,
    CodeSubmission, Stage1ResultResponse
)
from main import get_current_user, log_activity
from ai_evaluator import evaluate_code_with_ai

router = APIRouter(prefix="/api/stage1", tags=["Stage 1"])


# ============== MCQ ROUTES ==============

@router.get("/mcq/questions", response_model=List[MCQQuestionResponse])
async def get_mcq_questions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all MCQ questions for Stage 1"""
    # Check if user has already completed Stage 1
    result = db.query(Stage1Result).filter(
        Stage1Result.user_id == current_user.id,
        Stage1Result.completed_at.isnot(None)
    ).first()
    
    if result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already completed Stage 1"
        )
    
    # Get 10 random MCQ questions
    questions = db.query(MCQQuestion).order_by(func.rand()).limit(10).all()
    
    return questions


@router.post("/mcq/submit")
async def submit_mcq_answer(
    answer: MCQAnswerSubmit,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit answer for an MCQ question"""
    # Get the question
    question = db.query(MCQQuestion).filter(
        MCQQuestion.id == answer.question_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if already answered
    existing = db.query(MCQAttempt).filter(
        MCQAttempt.user_id == current_user.id,
        MCQAttempt.question_id == answer.question_id
    ).first()
    
    is_correct = question.correct_option == answer.selected_option
    
    if existing:
        # Update existing attempt
        existing.selected_option = answer.selected_option
        existing.is_correct = is_correct
        existing.time_taken = answer.time_taken
        existing.attempted_at = datetime.utcnow()
    else:
        # Create new attempt
        attempt = MCQAttempt(
            user_id=current_user.id,
            question_id=answer.question_id,
            selected_option=answer.selected_option,
            is_correct=is_correct,
            time_taken=answer.time_taken
        )
        db.add(attempt)
    
    db.commit()
    
    # Log activity
    log_activity(db, current_user.id, "mcq_answer", {
        "question_id": answer.question_id,
        "is_correct": is_correct
    }, request)
    
    return {
        "status": "success",
        "is_correct": is_correct,
        "correct_option": question.correct_option if is_correct else None
    }


@router.get("/mcq/attempts")
async def get_mcq_attempts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's MCQ attempts"""
    attempts = db.query(MCQAttempt).filter(
        MCQAttempt.user_id == current_user.id
    ).all()
    
    return [{
        "question_id": attempt.question_id,
        "selected_option": attempt.selected_option,
        "is_correct": attempt.is_correct,
        "time_taken": attempt.time_taken
    } for attempt in attempts]


# ============== PROGRAMMING QUESTIONS ROUTES ==============

@router.get("/programming/problems", response_model=List[ProgrammingProblemResponse])
async def get_programming_problems(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get programming problems for Stage 1"""
    # Check if user has already completed Stage 1
    result = db.query(Stage1Result).filter(
        Stage1Result.user_id == current_user.id,
        Stage1Result.completed_at.isnot(None)
    ).first()
    
    if result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already completed Stage 1"
        )
    
    # Get 2 programming problems
    problems = db.query(ProgrammingProblem).order_by(func.rand()).limit(2).all()
    
    return problems


@router.post("/programming/submit")
async def submit_code(
    submission: CodeSubmission,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit code for a programming problem"""
    # Get the problem
    problem = db.query(ProgrammingProblem).filter(
        ProgrammingProblem.id == submission.problem_id
    ).first()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Check for existing attempt
    attempt = db.query(ProgrammingQuestionAttempt).filter(
        ProgrammingQuestionAttempt.user_id == current_user.id,
        ProgrammingQuestionAttempt.problem_id == submission.problem_id
    ).first()
    
    # Evaluate code using AI
    evaluation = await evaluate_code_with_ai(
        code=submission.code,
        language=submission.language,
        problem_description=problem.description,
        sample_input=problem.sample_input,
        sample_output=problem.sample_output,
        constraints=problem.constraints
    )
    
    if attempt:
        # Update existing attempt
        attempt.code = submission.code
        attempt.language = submission.language
        attempt.status = evaluation['status']
        attempt.score = evaluation['score']
        attempt.ai_feedback = evaluation['feedback']
        attempt.updated_at = datetime.utcnow()
    else:
        # Create new attempt
        attempt = ProgrammingQuestionAttempt(
            user_id=current_user.id,
            problem_id=submission.problem_id,
            code=submission.code,
            language=submission.language,
            status=evaluation['status'],
            score=evaluation['score'],
            ai_feedback=evaluation['feedback']
        )
        db.add(attempt)
    
    db.commit()
    db.refresh(attempt)
    
    # Log activity
    log_activity(db, current_user.id, "code_submission", {
        "problem_id": submission.problem_id,
        "language": submission.language,
        "score": evaluation['score']
    }, request)
    
    return {
        "status": "success",
        "attempt_id": attempt.id,
        "evaluation": evaluation
    }


@router.get("/programming/attempts")
async def get_programming_attempts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's programming attempts"""
    attempts = db.query(ProgrammingQuestionAttempt).filter(
        ProgrammingQuestionAttempt.user_id == current_user.id
    ).all()
    
    return [{
        "problem_id": attempt.problem_id,
        "language": attempt.language,
        "status": attempt.status,
        "score": float(attempt.score),
        "ai_feedback": attempt.ai_feedback,
        "submitted_at": attempt.submitted_at
    } for attempt in attempts]


@router.post("/programming/track-tab")
async def track_tab_activity(
    problem_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track when user leaves fullscreen/tab"""
    attempt = db.query(ProgrammingQuestionAttempt).filter(
        ProgrammingQuestionAttempt.user_id == current_user.id,
        ProgrammingQuestionAttempt.problem_id == problem_id
    ).first()
    
    if attempt:
        attempt.tab_inactivity_count += 1
    else:
        # Create initial attempt record
        attempt = ProgrammingQuestionAttempt(
            user_id=current_user.id,
            problem_id=problem_id,
            code="",
            language="python",
            tab_inactivity_count=1
        )
        db.add(attempt)
    
    db.commit()
    
    # Log activity
    log_activity(db, current_user.id, "tab_switch", {
        "problem_id": problem_id,
        "count": attempt.tab_inactivity_count
    }, request)
    
    return {"tab_activity_count": attempt.tab_inactivity_count}


# ============== COMPLETE STAGE 1 ==============

@router.post("/complete", response_model=Stage1ResultResponse)
async def complete_stage1(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete Stage 1 and calculate results"""
    # Check if already completed
    existing_result = db.query(Stage1Result).filter(
        Stage1Result.user_id == current_user.id,
        Stage1Result.completed_at.isnot(None)
    ).first()
    
    if existing_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already completed Stage 1"
        )
    
    # Calculate MCQ score
    mcq_attempts = db.query(MCQAttempt).filter(
        MCQAttempt.user_id == current_user.id
    ).all()
    
    mcq_correct = sum(1 for attempt in mcq_attempts if attempt.is_correct)
    mcq_score = mcq_correct  # Each MCQ is 1 mark
    
    # Calculate Programming score
    programming_attempts = db.query(ProgrammingQuestionAttempt).filter(
        ProgrammingQuestionAttempt.user_id == current_user.id
    ).all()
    
    programming_score = sum(float(attempt.score) for attempt in programming_attempts)
    
    total_score = mcq_score + programming_score
    
    # Create or update result
    result = db.query(Stage1Result).filter(
        Stage1Result.user_id == current_user.id
    ).first()
    
    if result:
        result.mcq_score = mcq_score
        result.programming_score = programming_score
        result.total_score = total_score
        result.completed_at = datetime.utcnow()
    else:
        result = Stage1Result(
            user_id=current_user.id,
            mcq_score=mcq_score,
            programming_score=programming_score,
            total_score=total_score,
            completed_at=datetime.utcnow()
        )
        db.add(result)
    
    db.commit()
    db.refresh(result)
    
    # Calculate ranks (after all submissions)
    all_results = db.query(Stage1Result).filter(
        Stage1Result.completed_at.isnot(None)
    ).order_by(Stage1Result.total_score.desc()).all()
    
    for idx, r in enumerate(all_results, 1):
        r.rank = idx
        # Top 50% qualify for Stage 2 (adjust as needed)
        r.is_qualified = idx <= len(all_results) // 2
    
    db.commit()
    db.refresh(result)
    
    # Create notification
    if result.is_qualified:
        notification = Notification(
            user_id=current_user.id,
            title="🎉 Congratulations!",
            message=f"You've qualified for Round 2! Your score: {total_score}/35, Rank: #{result.rank}",
            type="qualification"
        )
    else:
        notification = Notification(
            user_id=current_user.id,
            title="Stage 1 Completed",
            message=f"Thank you for participating! Your score: {total_score}/35, Rank: #{result.rank}",
            type="result"
        )
    
    db.add(notification)
    db.commit()
    
    # Log activity
    log_activity(db, current_user.id, "stage1_complete", {
        "total_score": float(total_score),
        "rank": result.rank,
        "qualified": result.is_qualified
    }, request)
    
    return Stage1ResultResponse.from_orm(result)


@router.get("/result", response_model=Stage1ResultResponse)
async def get_stage1_result(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Stage 1 result"""
    result = db.query(Stage1Result).filter(
        Stage1Result.user_id == current_user.id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="No result found")
    
    return Stage1ResultResponse.from_orm(result)


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get Stage 1 leaderboard"""
    results = db.query(Stage1Result, User).join(User).filter(
        Stage1Result.completed_at.isnot(None)
    ).order_by(Stage1Result.total_score.desc()).limit(limit).all()
    
    return [{
        "rank": result.Stage1Result.rank,
        "user_name": result.User.full_name,
        "college": result.User.college_name,
        "total_score": float(result.Stage1Result.total_score),
        "mcq_score": float(result.Stage1Result.mcq_score),
        "programming_score": float(result.Stage1Result.programming_score)
    } for result in results]