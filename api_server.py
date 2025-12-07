# api_server_fixed.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import datetime
import json

app = FastAPI(title="AI Fitness Advisor API", 
              description="API for personalized workout recommendations",
              version="1.0.0")

# Import the simple advisor (no API key needed)
try:
    from fitness_advisor import SimpleFitnessAdvisor
    advisor = SimpleFitnessAdvisor()
    print("✅ Using SimpleFitnessAdvisor (no API key needed)")
except ImportError:
    # Create a fallback advisimple_fitness_advisor.py doesn't exist
    print("⚠️  Creating fallback advisor...")
    
    class FallbackAdvisor:
        def analyze_health_status(self, heart_rate, sleep_hours, stress_level, previous_workout=None):
            # Simple rule-based logic
            if heart_rate > 100 or sleep_hours < 4 or stress_level >= 8:
                return {
                    "alert_level": "high",
                    "should_train": False,
                    "workout": "Rest day",
                    "intensity": "very low",
                    "duration": 0,
                    "message": "Rest recommended based on your metrics",
                    "modifications": "Focus on recovery",
                    "recovery_tips": "Hydrate and get good sleep"
                }
            elif heart_rate > 85 or sleep_hours < 6 or stress_level >= 6:
                return {
                    "alert_level": "medium",
                    "should_train": True,
                    "workout": "Light cardio (walking, cycling)",
                    "intensity": "low",
                    "duration": 30,
                    "message": "Light activity recommended",
                    "modifications": "Reduce intensity if needed",
                    "recovery_tips": "Listen to your body"
                }
            else:
                return {
                    "alert_level": "low",
                    "should_train": True,
                    "workout": "Moderate workout",
                    "intensity": "moderate",
                    "duration": 45,
                    "message": "Good condition for training",
                    "modifications": "None needed",
                    "recovery_tips": "Stay hydrated"
                }
    
    advisor = FallbackAdvisor()

# Request models
class HealthMetrics(BaseModel):
    heart_rate: int
    sleep_hours: float
    stress_level: int
    previous_workout: Optional[str] = None
    user_id: Optional[str] = None
    age: Optional[int] = None
    fitness_level: Optional[str] = "intermediate"

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Fitness Advisor API - Simple Version",
        "status": "active",
        "advisor_type": "SimpleFitnessAdvisor (No API Key Needed)",
        "endpoints": {
            "health_check": "/health",
            "get_recommendation": "/recommend",
            "batch_recommendations": "/batch"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "advisor": "SimpleFitnessAdvisor",
        "version": "1.0.0"
    }

# Main recommendation endpoint
@app.post("/recommend")
async def get_recommendation(metrics: HealthMetrics):
    """
    Get workout recommendation based on health metrics
    
    Example request body:
    {
        "heart_rate": 72,
        "sleep_hours": 7.5,
        "stress_level": 4,
        "previous_workout": "weight training",
        "age": 30
    }
    """
    try:
        print(f"📊 Received metrics: HR={metrics.heart_rate}, Sleep={metrics.sleep_hours}, Stress={metrics.stress_level}")
        
        result = advisor.analyze_health_status(
            heart_rate=metrics.heart_rate,
            sleep_hours=metrics.sleep_hours,
            stress_level=metrics.stress_level,
            previous_workout=metrics.previous_workout
        )
        
        # Ensure all required fields exist
        required_fields = ["alert_level", "should_train", "workout", "intensity", "duration"]
        for field in required_fields:
            if field not in result:
                result[field] = "N/A"
        
        # Add metadata
        result["api_version"] = "1.0"
        result["timestamp"] = datetime.datetime.now().isoformat()
        result["request_id"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        result["user_id"] = metrics.user_id
        result["input_metrics"] = {
            "heart_rate": metrics.heart_rate,
            "sleep_hours": metrics.sleep_hours,
            "stress_level": metrics.stress_level,
            "previous_workout": metrics.previous_workout,
            "age": metrics.age,
            "fitness_level": metrics.fitness_level
        }
        
        print(f"✅ Generated recommendation: {result['alert_level']} alert, Train: {result['should_train']}")
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch processing endpoint
@app.post("/batch")
async def batch_recommendations(metrics_list: list[HealthMetrics]):
    """
    Process multiple recommendations at once
    """
    results = []
    for metrics in metrics_list:
        try:
            result = advisor.analyze_health_status(
                heart_rate=metrics.heart_rate,
                sleep_hours=metrics.sleep_hours,
                stress_level=metrics.stress_level,
                previous_workout=metrics.previous_workout
            )
            
            # Add metadata
            result["user_id"] = metrics.user_id
            result["request_timestamp"] = datetime.datetime.now().isoformat()
            results.append(result)
            
        except Exception as e:
            results.append({
                "error": str(e),
                "user_id": metrics.user_id,
                "heart_rate": metrics.heart_rate,
                "sleep_hours": metrics.sleep_hours,
                "stress_level": metrics.stress_level
            })
    
    return {
        "batch_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "total_requests": len(metrics_list),
        "successful": len([r for r in results if "error" not in r]),
        "failed": len([r for r in results if "error" in r]),
        "results": results
    }

# Test endpoint
@app.get("/test")
async def test_endpoint():
    """Test endpoint with sample data"""
    test_metrics = HealthMetrics(
        heart_rate=72,
        sleep_hours=7.5,
        stress_level=4,
        previous_workout="running",
        user_id="test_user"
    )
    
    result = advisor.analyze_health_status(
        heart_rate=test_metrics.heart_rate,
        sleep_hours=test_metrics.sleep_hours,
        stress_level=test_metrics.stress_level,
        previous_workout=test_metrics.previous_workout
    )
    
    return {
        "test": "successful",
        "sample_data": test_metrics.dict(),
        "recommendation": result
    }

# Simple history storage (in memory for demo)
workout_history = []

@app.post("/history")
async def save_to_history(metrics: HealthMetrics, recommendation: dict):
    """Save recommendation to history"""
    entry = {
        "id": len(workout_history) + 1,
        "timestamp": datetime.datetime.now().isoformat(),
        "user_id": metrics.user_id or "anonymous",
        "metrics": metrics.dict(),
        "recommendation": recommendation
    }
    workout_history.append(entry)
    return {"status": "saved", "entry_id": entry["id"]}

@app.get("/history")
async def get_history(user_id: Optional[str] = None):
    """Get workout history"""
    if user_id:
        user_history = [h for h in workout_history if h.get("user_id") == user_id]
        return {"user_id": user_id, "entries": user_history}
    return {"total_entries": len(workout_history), "entries": workout_history}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("🚀 STARTING FITNESS ADVISOR API")
    print("="*50)
    print("Version: Simple (No API Key Needed)")
    print("Port: 8000")
    print("\n📚 API Documentation:")
    print("  • Swagger UI: http://localhost:8000/docs")
    print("  • ReDoc:      http://localhost:8000/redoc")
    print("\n🌐 Test Endpoints:")
    print("  • Health:     http://localhost:8000/health")
    print("  • Test:       http://localhost:8000/test")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)