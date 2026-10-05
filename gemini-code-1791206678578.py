import markdown
from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import database
import models
import ai_service

# Initialize database tables
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="FitBuddy AI")
templates = Jinja2Templates(directory="templates")

# Helper function to parse markdown safely to HTML for templates
def render_markdown(text):
    return markdown.markdown(text)

app.jinja_env.filters['markdown'] = render_markdown

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def create_plan(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(database.get_db)
):
    # 1. Generate Content via Gemini
    workout = ai_service.generate_workout_plan(age, weight, goal, intensity)
    tip = ai_service.generate_nutrition_tip(goal)
    
    # 2. Save to SQLite Database
    db_plan = models.UserPlan(
        name=name, age=age, weight=weight, 
        goal=goal, intensity=intensity,
        workout_plan=workout, nutrition_tip=tip
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    return templates.TemplateResponse("plan.html", {"request": request, "plan": db_plan})

@app.post("/refine/{plan_id}", response_class=HTMLResponse)
async def update_plan(
    request: Request,
    plan_id: int,
    feedback: str = Form(...),
    db: Session = Depends(database.get_db)
):
    db_plan = db.query(models.UserPlan).filter(models.UserPlan.id == plan_id).first()
    if not db_plan:
        return HTMLResponse(content="Plan not found", status_code=404)
        
    # Refine workout plan with user feedback using Gemini Pro
    refined_workout = ai_service.refine_workout_plan(db_plan.workout_plan, feedback)
    
    # Update database record
    db_plan.workout_plan = refined_workout
    db.commit()
    db.refresh(db_plan)
    
    return templates.TemplateResponse("plan.html", {"request": request, "plan": db_plan})