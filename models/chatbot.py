"""
AI Chatbot/Assistant for Vehicle Damage Assessment System
Provides real-time assistance for users during image upload and damage assessment
"""

import json
import random
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DamageAssessmentChatbot:
    def __init__(self):
        self.responses = self.load_responses()
        self.context = {}
        self.conversation_history = []
    
    def load_responses(self) -> Dict[str, Any]:
        """Load predefined responses and conversation patterns"""
        return {
            "greetings": [
                "Hello! I'm here to help you with vehicle damage assessment. How can I assist you today?",
                "Hi there! I can help you upload images and understand your damage assessment results. What do you need help with?",
                "Welcome! I'm your AI assistant for damage assessment. Feel free to ask me anything!"
            ],
            "image_upload_help": [
                "To get the best results, please upload clear, well-lit images of the damaged area from multiple angles.",
                "Make sure the images show the damage clearly. Good lighting and multiple angles help our AI analyze better.",
                "For best results, take photos during daylight and ensure the damaged area is clearly visible in the frame."
            ],
            "image_quality": [
                "The image quality looks good! Our AI should be able to analyze this effectively.",
                "The image is a bit blurry. Try taking another photo with better focus for more accurate results.",
                "The lighting could be better. Try taking the photo in better lighting conditions."
            ],
            "damage_types": {
                "dent": "A dent is a depression in the vehicle's surface, usually caused by impact. It can range from minor to severe.",
                "scratch": "A scratch is a mark or groove on the surface, often caused by contact with rough objects or surfaces.",
                "broken_part": "This refers to any component that has been damaged or separated from the vehicle structure.",
                "crack": "A crack is a line of separation in the material, which can spread and cause further damage.",
                "rust": "Rust is corrosion that occurs when metal is exposed to moisture and oxygen over time.",
                "paint_damage": "Damage to the paint surface, including chips, fading, or peeling.",
                "structural_damage": "Damage to the vehicle's structural components that affects its integrity.",
                "glass_damage": "Damage to windows, windshields, or other glass components.",
                "light_damage": "Damage to headlights, taillights, or other lighting components.",
                "bumper_damage": "Damage specifically to the front or rear bumper of the vehicle."
            },
            "severity_explanations": {
                "minor": "Minor damage typically involves cosmetic issues that can be repaired quickly and inexpensively.",
                "moderate": "Moderate damage may require professional repair and could affect vehicle performance.",
                "severe": "Severe damage requires immediate attention and may involve structural components.",
                "critical": "Critical damage poses safety risks and requires immediate professional intervention."
            },
            "cost_estimation": [
                "Our cost estimation is based on current market rates for parts and labor in your area.",
                "The estimated cost includes parts, labor, and additional materials needed for repair.",
                "Keep in mind that actual repair costs may vary depending on the specific repair shop and additional damage discovered."
            ],
            "next_steps": [
                "Based on your assessment, I recommend contacting a certified repair shop for a detailed inspection.",
                "You should consider filing an insurance claim if the estimated cost exceeds your deductible.",
                "For minor damage, you might be able to handle some repairs yourself with the right tools and materials."
            ],
            "error_handling": [
                "I'm sorry, I didn't understand that. Could you please rephrase your question?",
                "I'm having trouble processing that request. Can you try asking in a different way?",
                "I'm not sure about that. Let me connect you with a human support agent for more specific help."
            ],
            "farewell": [
                "You're welcome! Feel free to ask if you have any other questions about your damage assessment.",
                "Glad I could help! Don't hesitate to reach out if you need assistance with anything else.",
                "Happy to assist! Let me know if you need help with your damage assessment or any other questions."
            ]
        }
    
    def process_message(self, message: str, user_id: str = None, context: Dict = None) -> Dict[str, Any]:
        """Process user message and generate appropriate response"""
        try:
            # Update context
            if context:
                self.context.update(context)
            
            # Add to conversation history
            self.conversation_history.append({
                "user": message,
                "timestamp": self.get_timestamp()
            })
            
            # Analyze message intent
            intent = self.analyze_intent(message)
            
            # Generate response based on intent
            response = self.generate_response(intent, message, user_id)
            
            # Add response to history
            self.conversation_history.append({
                "bot": response["message"],
                "timestamp": self.get_timestamp()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "message": "I'm sorry, I encountered an error. Please try again.",
                "type": "error",
                "suggestions": ["Try rephrasing your question", "Contact support if the issue persists"]
            }
    
    def analyze_intent(self, message: str) -> str:
        """Analyze user message to determine intent"""
        message_lower = message.lower()
        
        # Greeting patterns
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return "greeting"
        
        # Image upload help
        if any(word in message_lower for word in ["upload", "image", "photo", "picture", "camera"]):
            return "image_upload_help"
        
        # Damage type questions
        if any(word in message_lower for word in ["dent", "scratch", "broken", "crack", "rust", "paint"]):
            return "damage_type_question"
        
        # Severity questions
        if any(word in message_lower for word in ["severity", "severe", "minor", "moderate", "critical"]):
            return "severity_question"
        
        # Cost questions
        if any(word in message_lower for word in ["cost", "price", "expensive", "cheap", "estimate"]):
            return "cost_question"
        
        # Next steps
        if any(word in message_lower for word in ["next", "what should", "recommend", "advice"]):
            return "next_steps"
        
        # Help requests
        if any(word in message_lower for word in ["help", "assist", "support", "how to"]):
            return "help"
        
        # Farewell
        if any(word in message_lower for word in ["bye", "goodbye", "thanks", "thank you"]):
            return "farewell"
        
        return "general"
    
    def generate_response(self, intent: str, message: str, user_id: str = None) -> Dict[str, Any]:
        """Generate response based on intent and context"""
        try:
            if intent == "greeting":
                return {
                    "message": random.choice(self.responses["greetings"]),
                    "type": "greeting",
                    "suggestions": [
                        "How do I upload images?",
                        "What types of damage can you detect?",
                        "How accurate is the cost estimation?"
                    ]
                }
            
            elif intent == "image_upload_help":
                return {
                    "message": random.choice(self.responses["image_upload_help"]),
                    "type": "help",
                    "suggestions": [
                        "What image quality is best?",
                        "How many images should I upload?",
                        "Can I use my phone camera?"
                    ]
                }
            
            elif intent == "damage_type_question":
                damage_type = self.extract_damage_type(message)
                if damage_type and damage_type in self.responses["damage_types"]:
                    return {
                        "message": self.responses["damage_types"][damage_type],
                        "type": "information",
                        "suggestions": [
                            "How is severity determined?",
                            "What's the typical cost for this damage?",
                            "Should I get this repaired immediately?"
                        ]
                    }
                else:
                    return {
                        "message": "I can help explain different types of vehicle damage. Which specific type are you asking about?",
                        "type": "clarification",
                        "suggestions": [
                            "Dent", "Scratch", "Broken Part", "Crack", "Rust", "Paint Damage"
                        ]
                    }
            
            elif intent == "severity_question":
                severity = self.extract_severity(message)
                if severity and severity in self.responses["severity_explanations"]:
                    return {
                        "message": self.responses["severity_explanations"][severity],
                        "type": "information",
                        "suggestions": [
                            "What should I do for this severity?",
                            "How does severity affect cost?",
                            "Is this safe to drive?"
                        ]
                    }
                else:
                    return {
                        "message": "Damage severity ranges from Minor to Critical. Minor damage is cosmetic, while Critical damage poses safety risks.",
                        "type": "information",
                        "suggestions": [
                            "Explain Minor damage",
                            "Explain Moderate damage", 
                            "Explain Severe damage",
                            "Explain Critical damage"
                        ]
                    }
            
            elif intent == "cost_question":
                return {
                    "message": random.choice(self.responses["cost_estimation"]),
                    "type": "information",
                    "suggestions": [
                        "How accurate is the cost estimate?",
                        "What factors affect the cost?",
                        "Should I get multiple estimates?"
                    ]
                }
            
            elif intent == "next_steps":
                return {
                    "message": random.choice(self.responses["next_steps"]),
                    "type": "advice",
                    "suggestions": [
                        "Find nearby repair shops",
                        "Contact insurance company",
                        "Schedule inspection"
                    ]
                }
            
            elif intent == "help":
                return {
                    "message": "I can help you with image upload, damage analysis, cost estimation, and repair recommendations. What specific area do you need help with?",
                    "type": "help",
                    "suggestions": [
                        "How to upload images",
                        "Understanding damage types",
                        "Cost estimation process",
                        "Finding repair shops"
                    ]
                }
            
            elif intent == "farewell":
                return {
                    "message": random.choice(self.responses["farewell"]),
                    "type": "farewell",
                    "suggestions": []
                }
            
            else:
                return {
                    "message": "I'm here to help with vehicle damage assessment. You can ask me about uploading images, understanding damage types, cost estimation, or repair recommendations.",
                    "type": "general",
                    "suggestions": [
                        "How do I upload images?",
                        "What damage types can you detect?",
                        "How does cost estimation work?",
                        "Find repair shops near me"
                    ]
                }
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "message": random.choice(self.responses["error_handling"]),
                "type": "error",
                "suggestions": ["Try rephrasing your question", "Contact support"]
            }
    
    def extract_damage_type(self, message: str) -> str:
        """Extract damage type from message"""
        message_lower = message.lower()
        
        damage_mapping = {
            "dent": "dent",
            "dents": "dent",
            "dented": "dent",
            "scratch": "scratch",
            "scratches": "scratch",
            "scratched": "scratch",
            "broken": "broken_part",
            "break": "broken_part",
            "crack": "crack",
            "cracks": "crack",
            "cracked": "crack",
            "rust": "rust",
            "rusty": "rust",
            "paint": "paint_damage",
            "painted": "paint_damage",
            "structural": "structural_damage",
            "glass": "glass_damage",
            "windshield": "glass_damage",
            "light": "light_damage",
            "headlight": "light_damage",
            "bumper": "bumper_damage"
        }
        
        for keyword, damage_type in damage_mapping.items():
            if keyword in message_lower:
                return damage_type
        
        return None
    
    def extract_severity(self, message: str) -> str:
        """Extract severity level from message"""
        message_lower = message.lower()
        
        severity_mapping = {
            "minor": "minor",
            "small": "minor",
            "light": "minor",
            "moderate": "moderate",
            "medium": "moderate",
            "severe": "severe",
            "serious": "severe",
            "bad": "severe",
            "critical": "critical",
            "dangerous": "critical",
            "urgent": "critical"
        }
        
        for keyword, severity in severity_mapping.items():
            if keyword in message_lower:
                return severity
        
        return None
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_history(self, user_id: str = None) -> List[Dict]:
        """Get conversation history for user"""
        if user_id:
            # Filter history by user_id if needed
            return self.conversation_history
        return self.conversation_history
    
    def clear_history(self, user_id: str = None):
        """Clear conversation history"""
        self.conversation_history = []
        self.context = {}
    
    def get_suggestions(self, context: Dict = None) -> List[str]:
        """Get contextual suggestions based on current state"""
        if not context:
            return [
                "How do I upload images?",
                "What damage types can you detect?",
                "How accurate is the cost estimation?",
                "Find repair shops near me"
            ]
        
        # Context-based suggestions
        if context.get("has_images"):
            return [
                "Analyze my images",
                "What damage do you see?",
                "Estimate repair cost",
                "Find repair shops"
            ]
        
        if context.get("has_results"):
            return [
                "Explain the damage type",
                "Why is the cost so high?",
                "Find repair shops",
                "Download report"
            ]
        
        return [
            "Upload images for analysis",
            "Learn about damage types",
            "Understand cost estimation",
            "Get repair recommendations"
        ]
