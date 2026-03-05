import os
import json
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Akrabi Groups AI Platform")
templates = Jinja2Templates(directory="templates")

# Load mock data
def load_json(filename):
    try:
        with open(f"data/{filename}", "r") as f:
            return json.load(f)
    except:
        return []

students = load_json("students.json")
opportunities = load_json("opportunities.json")
seo_keywords = load_json("seo_keywords.json")
voice_conversations = load_json("voice_conversations.json")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/students")
async def get_students():
    return {"students": students}

@app.get("/api/opportunities")
async def get_opportunities():
    return {"opportunities": opportunities}

@app.get("/api/matches")
async def get_matches():
    """Generate AI-powered student-opportunity matches"""
    matches = []
    
    for student in students[:10]:  # Show top 10 students
        best_opportunity = None
        best_score = 0
        
        for opp in opportunities:
            # Calculate match score based on skills, interests, experience
            score = 0
            
            # Skill matching
            student_skills = [skill.lower() for skill in student.get("skills", [])]
            required_skills = [skill.lower() for skill in opp.get("required_skills", [])]
            
            skill_matches = len(set(student_skills) & set(required_skills))
            score += skill_matches * 20
            
            # Interest matching
            if student.get("career_interests", "").lower() in opp.get("industry", "").lower():
                score += 25
            
            # Experience level matching
            if student.get("experience_level", "").lower() in opp.get("level", "").lower():
                score += 15
            
            # Random factor for demo variety
            score += random.randint(5, 20)
            
            if score > best_score:
                best_score = score
                best_opportunity = opp
        
        if best_opportunity:
            matches.append({
                "student": student,
                "opportunity": best_opportunity,
                "match_score": min(best_score, 95),  # Cap at 95%
                "reasoning": generate_match_reasoning(student, best_opportunity, best_score)
            })
    
    # Sort by match score
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return {"matches": matches}

def generate_match_reasoning(student, opportunity, score):
    """Generate AI reasoning for the match"""
    reasons = []
    
    student_skills = [skill.lower() for skill in student.get("skills", [])]
    required_skills = [skill.lower() for skill in opportunity.get("required_skills", [])]
    skill_matches = list(set(student_skills) & set(required_skills))
    
    if skill_matches:
        reasons.append(f"Strong skill alignment: {', '.join(skill_matches)}")
    
    if student.get("career_interests", "").lower() in opportunity.get("industry", "").lower():
        reasons.append(f"Career interest matches {opportunity.get('industry')} industry")
    
    if student.get("experience_level") == opportunity.get("level"):
        reasons.append(f"Experience level perfectly matches ({student.get('experience_level')})")
    
    if not reasons:
        reasons.append("Good foundational match based on profile analysis")
    
    return " • ".join(reasons)

@app.post("/api/voice-demo")
async def voice_demo(student_name: str = Form(...)):
    """Simulate voice agent conversation"""
    
    # Find or create student record
    existing_student = next((s for s in students if s["name"].lower() == student_name.lower()), None)
    
    if existing_student:
        conversation = f"""
Voice Agent: Hi {student_name}! I see you're already in our system. Let me pull up your profile...

I have you down as a {existing_student['major']} student at {existing_student['university']} with skills in {', '.join(existing_student['skills'][:3])}. 

Voice Agent: What specific type of opportunity are you looking for today?

{student_name}: I'm interested in {existing_student['career_interests'].lower()} roles, preferably something part-time.

Voice Agent: Perfect! Based on your profile, I have {random.randint(3, 7)} relevant opportunities. I'll send you a detailed match report within the next hour. Is your email {student_name.lower().replace(' ', '.')}@{existing_student['university'].lower().replace(' ', '')}.edu?

{student_name}: Yes, that's correct.

Voice Agent: Excellent! I've scheduled a follow-up call for next week to discuss your top matches. Thank you for using Akrabi Groups!
"""
    else:
        # New student intake conversation
        conversation = random.choice(voice_conversations)["transcript"].format(name=student_name)
    
    return {
        "transcript": conversation,
        "status": "completed",
        "next_steps": [
            "Student profile updated in database",
            "AI matching algorithm triggered",
            "Match report will be generated",
            "Follow-up call scheduled"
        ]
    }

@app.post("/api/generate-content")
async def generate_content(content_type: str = Form(...), topic: str = Form(...)):
    """Generate SEO-optimized social media content"""
    
    # Select relevant keywords
    relevant_keywords = [kw for kw in seo_keywords if topic.lower() in kw["keyword"].lower()][:3]
    
    if content_type == "instagram":
        content = generate_instagram_post(topic, relevant_keywords)
    elif content_type == "linkedin":
        content = generate_linkedin_post(topic, relevant_keywords)
    else:
        content = generate_generic_post(topic, relevant_keywords)
    
    return {
        "content": content,
        "keywords_used": [kw["keyword"] for kw in relevant_keywords],
        "seo_score": random.randint(78, 95),
        "estimated_reach": f"{random.randint(1200, 5000):,} people"
    }

def generate_instagram_post(topic, keywords):
    templates_dict = {
        "networking": """🚀 Building connections that launch careers! 

At Akrabi Groups, we're not just about networking—we're about creating meaningful partnerships between ambitious students and forward-thinking entrepreneurs.

✨ This week's success stories:
• 3 students matched with fintech startups
• 2 new consulting projects launched
• 15+ meaningful connections made

Ready to accelerate your career journey? 

#StudentNetworking #EntrepreneurLife #CareerGrowth #BusinessConsulting #TorontoStudents #NetworkingEvents #StartupCommunity #ProfessionalDevelopment""",
        
        "opportunities": """📢 EXCITING OPPORTUNITIES ALERT! 

We've just added 5 new partnership opportunities perfect for ambitious students:

🏢 Fintech Startup - Marketing Intern
💻 E-commerce Scale-up - Business Analyst  
🎯 Consulting Firm - Project Coordinator
🚀 Tech Company - Growth Associate
📊 Investment Firm - Research Assistant

All positions offer:
✅ Flexible schedules
✅ Real-world experience  
✅ Mentorship from industry leaders
✅ Potential for full-time conversion

Applications close Friday! Link in bio 👆

#JobOpportunities #StudentJobs #Internships #CareerOpportunities #BusinessCareers #TorontoJobs #StudentSuccess""",
        
        "success": """🎉 STUDENT SUCCESS SPOTLIGHT!

Meet Sarah Chen, Business student at UofT who landed her dream role at a fintech startup through our matching platform!

"Akrabi Groups didn't just connect me with an opportunity—they connected me with my future. The personalized matching process understood exactly what I was looking for."

Sarah's journey:
📝 Joined our platform in September  
🤝 Matched with 3 relevant startups
💼 Interviewed with top choice
🎯 Started her role in October
⭐ Now mentoring other students!

Your success story could be next! 

#SuccessStory #StudentAchievement #CareerSuccess #NetworkingWorks #StartupCareers #UofTStudents #DreamJob"""
    }
    
    # Select template based on topic
    if "network" in topic.lower():
        return templates_dict["networking"]
    elif "opportunity" in topic.lower() or "job" in topic.lower():
        return templates_dict["opportunities"]
    else:
        return templates_dict["success"]

def generate_linkedin_post(topic, keywords):
    return f"""The future of student-professional networking is here.

At Akrabi Groups, we're revolutionizing how students connect with entrepreneurs and business opportunities. Our AI-powered matching system has facilitated over 200+ successful partnerships this year.

Key insights from our platform:
→ 89% of matched students report improved career clarity
→ 76% secure opportunities within 3 months
→ 94% of entrepreneurs want to continue partnerships

The traditional approach of mass networking events is evolving. Today's students need targeted, meaningful connections that align with their specific goals and skills.

Interested in learning more about our approach? Let's connect.

#StudentNetworking #EntrepreneurshipEducation #CareerDevelopment #BusinessConsulting"""

def generate_generic_post(topic, keywords):
    return f"""🌟 Transforming student careers through strategic partnerships

{topic} is more than just an opportunity—it's a pathway to professional growth. At Akrabi Groups, we specialize in creating these transformative connections.

Our process:
1️⃣ Deep student profile analysis
2️⃣ AI-powered opportunity matching  
3️⃣ Personalized introductions
4️⃣ Ongoing mentorship support

The result? Students who are career-ready and entrepreneurs who find exceptional talent.

Ready to discover your potential?

#CareerGrowth #StudentOpportunities #BusinessNetworking #ProfessionalDevelopment"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)