# fitness_cli.py
import sys
from fitness_advisor import FitnessAdvisorAgent, display_recommendation

def interactive_cli():
    """Interactive command-line interface for the fitness advisor"""
    
    print("🤖 AI Fitness Advisor")
    print("-" * 40)
    
    # Get API key
    api_key = input("Enter your DeepSeek API key (or press Enter for fallback mode): ").strip()
    
    if not api_key:
        print("⚠️  Running in fallback mode (rule-based recommendations only)")
        api_key = "dummy-key"
    
    advisor = FitnessAdvisorAgent(api_key=api_key)
    
    while True:
        print("\n" + "="*40)
        print("Enter your health metrics:")
        print("="*40)
        
        try:
            # Get user input
            heart_rate = int(input("❤️  Resting Heart Rate (bpm): "))
            sleep_hours = float(input("😴 Sleep Hours (last night): "))
            stress_level = int(input("🧠 Stress Level (1-10): "))
            previous_workout = input("💪 Previous Workout (optional): ")
            
            if not previous_workout:
                previous_workout = None
            
            print("\n⏳ Analyzing your metrics...")
            
            # Get recommendation
            recommendation = advisor.analyze_health_status(
                heart_rate=heart_rate,
                sleep_hours=sleep_hours,
                stress_level=stress_level,
                previous_workout=previous_workout
            )
            
            # Display results
            display_recommendation(recommendation)
            
            # Ask to continue
            continue_choice = input("\n📋 Another analysis? (y/n): ").lower()
            if continue_choice != 'y':
                print("👋 Stay healthy! Goodbye!")
                break
                
        except ValueError:
            print("❌ Invalid input. Please enter numbers for heart rate, sleep, and stress level.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    interactive_cli()