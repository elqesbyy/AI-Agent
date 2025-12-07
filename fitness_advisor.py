import json
from typing import Dict, List, Optional
import datetime

class FitnessAdvisorAgent:
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        """
        Initialize the AI Fitness Advisor Agent
        
        Args:
            api_key: Your DeepSeek API key
            model: Model to use (default: deepseek-chat)
        """
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            self.model = model
        except ImportError:
            raise ImportError("Please install openai package: pip install openai")
    
    def analyze_health_status(self, heart_rate: int, sleep_hours: float, 
                            stress_level: int, previous_workout: str = None) -> Dict:
        """
        Analyze health metrics and provide workout recommendations
        
        Args:
            heart_rate: Resting heart rate (bpm)
            sleep_hours: Hours slept last night
            stress_level: Stress level (1-10 scale)
            previous_workout: Previous workout type (optional)
        
        Returns:
            Dictionary with analysis and recommendations
        """
        
        # Prepare the prompt for the AI
        prompt = self._create_prompt(heart_rate, sleep_hours, stress_level, previous_workout)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse the AI response
            return self._parse_response(ai_response, heart_rate, sleep_hours, stress_level)
            
        except Exception as e:
            print(f"Error calling DeepSeek API: {e}")
            return self._get_fallback_recommendation(heart_rate, sleep_hours, stress_level)
    
    def _get_system_prompt(self) -> str:
        """System prompt to guide the AI's behavior"""
        return """You are an expert fitness and health advisor AI. Your role is to analyze 
        user's health metrics (heart rate, sleep, stress) and provide personalized workout 
        recommendations and safety alerts.
        
        Always follow these guidelines:
        1. Prioritize user safety and health
        2. Consider all metrics together, not individually
        3. Provide specific, actionable recommendations
        4. Explain your reasoning clearly
        5. Suggest modifications for different fitness levels
        
        Format your response as JSON with these keys:
        - alert_level: "high", "medium", "low", or "rest"
        - should_train: true or false
        - alert_message: Brief explanation of the alert
        - recommended_workout: Specific workout plan
        - intensity_level: "low", "moderate", or "high"
        - duration_minutes: Recommended workout duration
        - modifications: Optional modifications or alternatives
        - recovery_tips: Tips for recovery if needed
        
        Base your recommendations on medical guidelines:
        - Resting HR > 100 bpm: Consider rest
        - Sleep < 6 hours: Reduce intensity
        - Stress > 7/10: Prefer light activity or rest
        """
    
    def _create_prompt(self, heart_rate: int, sleep_hours: float, 
                      stress_level: int, previous_workout: str) -> str:
        """Create the user prompt with health metrics"""
        
        prompt = f"""Analyze these health metrics and provide workout recommendations:
        
        Current Health Status:
        - Resting Heart Rate: {heart_rate} bpm
        - Sleep Duration: {sleep_hours} hours
        - Stress Level: {stress_level}/10
        
        Additional Context:
        - Previous Workout: {previous_workout if previous_workout else 'No recent workout data'}
        - Current Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        Please provide your analysis and recommendations in the specified JSON format."""
        
        return prompt
    
    def _parse_response(self, ai_response: str, heart_rate: int, 
                       sleep_hours: float, stress_level: int) -> Dict:
        """Parse the AI response and add basic metrics"""
        
        try:
            # Extract JSON from the response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                response_json = json.loads(ai_response[json_start:json_end])
            else:
                # If no JSON found, create a structured response
                response_json = {
                    "alert_level": "medium",
                    "should_train": True,
                    "alert_message": "AI response format issue, using default recommendation",
                    "recommended_workout": "Light cardio (30 min walk/jog)",
                    "intensity_level": "low",
                    "duration_minutes": 30,
                    "modifications": "Reduce intensity if feeling tired",
                    "recovery_tips": "Stay hydrated and monitor how you feel"
                }
            
            # Add the original metrics to the response
            response_json["input_metrics"] = {
                "heart_rate_bpm": heart_rate,
                "sleep_hours": sleep_hours,
                "stress_level": stress_level,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            return response_json
            
        except json.JSONDecodeError:
            return self._get_fallback_recommendation(heart_rate, sleep_hours, stress_level)
    
    def _get_fallback_recommendation(self, heart_rate: int, sleep_hours: float, 
                                   stress_level: int) -> Dict:
        """Provide fallback recommendations if AI fails"""
        
        # Basic rule-based recommendations
        if heart_rate > 100 or sleep_hours < 4 or stress_level >= 8:
            alert_level = "high"
            should_train = False
            workout = "Rest day or gentle stretching"
            intensity = "very low"
            duration = 15
        elif heart_rate > 85 or sleep_hours < 6 or stress_level >= 6:
            alert_level = "medium"
            should_train = True
            workout = "Light cardio (walking, cycling)"
            intensity = "low"
            duration = 30
        else:
            alert_level = "low"
            should_train = True
            workout = "Moderate workout (running, weight training)"
            intensity = "moderate"
            duration = 45
        
        return {
            "alert_level": alert_level,
            "should_train": should_train,
            "alert_message": f"Based on your metrics: HR={heart_rate}bpm, Sleep={sleep_hours}h, Stress={stress_level}/10",
            "recommended_workout": workout,
            "intensity_level": intensity,
            "duration_minutes": duration,
            "modifications": "Listen to your body and adjust as needed",
            "recovery_tips": "Hydrate well and ensure proper nutrition",
            "input_metrics": {
                "heart_rate_bpm": heart_rate,
                "sleep_hours": sleep_hours,
                "stress_level": stress_level,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    
    def get_workout_suggestions(self, health_condition: str) -> List[str]:
        """Get specific workout suggestions based on health conditions"""
        
        prompt = f"""Based on this health condition: {health_condition}
        Provide 3 safe workout suggestions in JSON format with:
        - workout_type
        - duration_minutes
        - intensity
        - precautions"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a fitness expert providing safe workout suggestions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except:
            return ["Light walking for 20-30 minutes", "Gentle stretching for 15-20 minutes", "Rest day with light mobility work"]


def display_recommendation(recommendation: Dict):
    """Display the recommendation in a user-friendly format"""
    
    print("\n" + "="*50)
    print("🏋️‍♂️ FITNESS ADVISOR RECOMMENDATION")
    print("="*50)
    
    # Display alert with emoji
    alert_emojis = {
        "high": "🚨",
        "medium": "⚠️",
        "low": "✅",
        "rest": "💤"
    }
    
    alert_emoji = alert_emojis.get(recommendation.get("alert_level", "medium"), "⚠️")
    
    print(f"\n{alert_emoji} ALERT LEVEL: {recommendation.get('alert_level', 'medium').upper()}")
    print(f"📊 Should Train: {'YES' if recommendation.get('should_train') else 'NO'}")
    
    print(f"\n📋 Recommendation:")
    print(f"   Workout: {recommendation.get('recommended_workout', 'Not specified')}")
    print(f"   Intensity: {recommendation.get('intensity_level', 'Not specified').upper()}")
    print(f"   Duration: {recommendation.get('duration_minutes', 'Not specified')} minutes")
    
    print(f"\n💡 Alert Message:")
    print(f"   {recommendation.get('alert_message', 'No specific message')}")
    
    if recommendation.get('modifications'):
        print(f"\n🔄 Modifications:")
        print(f"   {recommendation.get('modifications')}")
    
    if recommendation.get('recovery_tips'):
        print(f"\n💪 Recovery Tips:")
        print(f"   {recommendation.get('recovery_tips')}")
    
    print(f"\n📈 Your Metrics:")
    metrics = recommendation.get('input_metrics', {})
    print(f"   ❤️  Heart Rate: {metrics.get('heart_rate_bpm', 'N/A')} bpm")
    print(f"   😴 Sleep: {metrics.get('sleep_hours', 'N/A')} hours")
    print(f"   🧠 Stress: {metrics.get('stress_level', 'N/A')}/10")
    
    print("\n" + "="*50)


# Example usage function
def main():
    """Example of how to use the Fitness Advisor Agent"""
    
    # Replace with your DeepSeek API key
    DEEPSEEK_API_KEY = "your-deepseek-api-key-here"
    
    # Initialize the agent
    advisor = FitnessAdvisorAgent(api_key=DEEPSEEK_API_KEY)
    
    # Example 1: Normal conditions
    print("Example 1: Normal Health Metrics")
    result1 = advisor.analyze_health_status(
        heart_rate=65,
        sleep_hours=7.5,
        stress_level=3,
        previous_workout="Weight training"
    )
    display_recommendation(result1)
    
    # Example 2: High stress, low sleep
    print("\n\nExample 2: Stressed with Poor Sleep")
    result2 = advisor.analyze_health_status(
        heart_rate=78,
        sleep_hours=4.5,
        stress_level=8,
        previous_workout="Intense cardio"
    )
    display_recommendation(result2)
    
    # Example 3: Very high heart rate
    print("\n\nExample 3: Elevated Heart Rate")
    result3 = advisor.analyze_health_status(
        heart_rate=105,
        sleep_hours=6.0,
        stress_level=5,
        previous_workout=None
    )
    display_recommendation(result3)


if __name__ == "__main__":
    # For testing without an API key, use mock data
    print("Note: Replace 'your-deepseek-api-key-here' with your actual API key")
    
    # Uncomment to run with your API key
    # main()
    
    # Quick test with fallback
    print("\nTesting with fallback recommendations:")
    test_advisor = FitnessAdvisorAgent(api_key="test")
    test_result = test_advisor._get_fallback_recommendation(72, 6.5, 4)
    display_recommendation(test_result)