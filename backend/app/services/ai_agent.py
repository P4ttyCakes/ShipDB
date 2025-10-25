import json
import threading
import time
from typing import Dict, Any, Optional, List
from uuid import uuid4

from loguru import logger
from app.core.config import settings

try:
    # Anthropic SDK for Claude
    from anthropic import Anthropic
except Exception:  # pragma: no cover 
    Anthropic = None  # type: ignore


class AIAgentService:
    def __init__(self) -> None:
        """Initialize the in-memory session store and configure the Anthropic client."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        if Anthropic is None:
            raise RuntimeError("anthropic SDK not installed")
        if not getattr(settings, "ANTHROPIC_API_KEY", None):
            raise RuntimeError("ANTHROPIC_API_KEY not configured")
        self._client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self._model_name: str = getattr(settings, "ANTHROPIC_MODEL", "claude-3-haiku-20240307")

    def _system_instruction(self) -> str:
        """Return the instruction used to constrain the model to a JSON control response."""
        return (
            "You are an expert database architect helping non-technical users create database schemas. "
            "Your goal is to suggest appropriate database designs based on their project description, NOT ask technical questions. "
            "You should intelligently infer database requirements from business needs and suggest complete schemas. "
            "\n\n"
            "Process: "
            "1. Analyze the project description to understand the business domain "
            "2. Suggest appropriate database type (postgresql for relational data, mongodb for flexible documents, dynamodb for high-scale) "
            "3. Propose entities/tables based on the business domain "
            "4. Suggest fields with appropriate data types "
            "5. Add sensible constraints, indexes, and relationships automatically "
            "\n\n"
            "IMPORTANT: After gathering sufficient business information, you MUST generate a complete database specification. "
            "Don't keep asking questions indefinitely - provide a working database design based on the information gathered."
            "\n\n"
            "Ask ONLY high-level business questions like: "
            "- 'What type of users will use this system?' "
            "- 'What are the main features you want?' "
            "- 'Do you need to track user accounts, orders, inventory, etc.?' "
            "- 'What are the key data points you need to store?' "
            "\n\n"
            "NEVER ask technical questions about: "
            "- Database constraints, indexes, foreign keys "
            "- Data types, field specifications "
            "- Database optimization details "
            "\n\n"
            "CRITICAL JSON FORMAT REQUIREMENT: "
            "You MUST respond with ONLY a valid JSON object. No other text, explanations, or formatting. "
            "The JSON must have exactly these keys: next_question, done, partial_spec "
            "\n\n"
            "Example response format: "
            '{"next_question": "What type of users will use this system?", "done": false, "partial_spec": {}}'
            "\n\n"
            "When done=true, partial_spec must be a COMPLETE database specification with: "
            "- app_type: string describing the application "
            "- db_type: 'postgresql', 'mongodb', or 'dynamodb' "
            "- entities: array of objects with 'name' and 'fields' "
            "- Each field must have: name, type, required (boolean), and appropriate constraints "
            "- Include primary keys, foreign keys, indexes, and relationships "
            "\n\n"
            "CONVERSATION COMPLETION DETECTION: "
            "Set done=true when you have enough information to create a complete database design. "
            "This typically happens when: "
            "- You understand the business domain and core entities "
            "- You know the main data fields and relationships needed "
            "- You have sufficient context to make intelligent database choices "
            "- The user has provided 2-4 substantial answers about their business "
            "\n\n"
            "When you conclude the conversation, use phrases like: "
            "- 'Perfect! I have enough information to create your database design.' "
            "- 'Great! I now have everything I need to design your database.' "
            "- 'Excellent! Based on what you've told me, I can create your database schema.' "
            "\n\n"
            "ALWAYS set done=true when you use completion phrases like the above. "
            "The system will detect these phrases and automatically finalize the conversation."
        )

    def _merge_partial(self, base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge an incoming partial spec into the accumulated base spec."""
        for k, v in incoming.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                base[k] = self._merge_partial(base[k], v)
            else:
                base[k] = v
        return base

    def _validate_complete_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate that a spec is complete enough for schema generation."""
        if not isinstance(spec, dict):
            return False
        
        # Must have app_type
        if not spec.get("app_type"):
            return False
            
        # Must have db_type
        if spec.get("db_type") not in ["postgresql", "mongodb", "dynamodb"]:
            return False
            
        # Must have entities
        entities = spec.get("entities", [])
        if not isinstance(entities, list) or len(entities) == 0:
            return False
            
        # Each entity must have name and fields
        for entity in entities:
            if not isinstance(entity, dict):
                return False
            if not entity.get("name"):
                return False
            fields = entity.get("fields", [])
            if not isinstance(fields, list) or len(fields) == 0:
                return False
            # Each field must have name and type
            for field in fields:
                if not isinstance(field, dict):
                    return False
                if not field.get("name") or not field.get("type"):
                    return False
        
        return True

    def _to_anthropic_messages(self, history: List[Dict[str, str]], last_user: Optional[str] = None) -> List[Dict[str, Any]]:
        """Convert internal history into Anthropic messages format, optionally appending a user turn."""
        msgs: List[Dict[str, Any]] = []
        for m in history:
            role = m.get("role")
            if role not in ("user", "assistant"):
                continue
            msgs.append({"role": role, "content": m.get("content", "")})
        if last_user is not None:
            msgs.append({"role": "user", "content": last_user})
        return msgs
    
    def _generate_basic_entities_from_context(self, history: List[Dict], answer: str) -> List[Dict]:
        """Generate basic entities based on conversation context when user wants to proceed"""
        entities = []
        
        # Extract business context from conversation
        full_conversation = " ".join([msg.get("content", "") for msg in history + [{"content": answer}]])
        full_conversation_lower = full_conversation.lower()
        
        # Real Estate Platform entities
        if any(word in full_conversation_lower for word in ["property", "real estate", "rent", "buy", "apartment", "house", "condo"]):
            entities.extend([
                {
                    "name": "properties",
                    "fields": [
                        {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                        {"name": "title", "type": "string", "required": True},
                        {"name": "description", "type": "text", "required": False},
                        {"name": "property_type", "type": "string", "required": True},
                        {"name": "bedrooms", "type": "integer", "required": True},
                        {"name": "bathrooms", "type": "integer", "required": True},
                        {"name": "square_footage", "type": "integer", "required": False},
                        {"name": "price", "type": "decimal", "required": True},
                        {"name": "location", "type": "string", "required": True},
                        {"name": "owner_contact", "type": "string", "required": True},
                        {"name": "created_at", "type": "timestamp", "required": True},
                        {"name": "updated_at", "type": "timestamp", "required": True}
                    ]
                },
                {
                    "name": "users",
                    "fields": [
                        {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                        {"name": "email", "type": "string", "required": True, "unique": True},
                        {"name": "name", "type": "string", "required": True},
                        {"name": "role", "type": "string", "required": True},
                        {"name": "created_at", "type": "timestamp", "required": True}
                    ]
                }
            ])
        
        # E-commerce entities
        elif any(word in full_conversation_lower for word in ["product", "ecommerce", "store", "inventory", "order"]):
            entities.extend([
                {
                    "name": "products",
                    "fields": [
                        {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                        {"name": "name", "type": "string", "required": True},
                        {"name": "description", "type": "text", "required": False},
                        {"name": "price", "type": "decimal", "required": True},
                        {"name": "inventory_count", "type": "integer", "required": True},
                        {"name": "category", "type": "string", "required": True},
                        {"name": "created_at", "type": "timestamp", "required": True}
                    ]
                },
                {
                    "name": "users",
                    "fields": [
                        {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                        {"name": "email", "type": "string", "required": True, "unique": True},
                        {"name": "name", "type": "string", "required": True},
                        {"name": "created_at", "type": "timestamp", "required": True}
                    ]
                }
            ])
        
        # Default generic entities if no specific business detected
        else:
            entities.extend([
                {
                    "name": "users",
                    "fields": [
                        {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                        {"name": "email", "type": "string", "required": True, "unique": True},
                        {"name": "name", "type": "string", "required": True},
                        {"name": "created_at", "type": "timestamp", "required": True}
                    ]
                },
                {
                    "name": "items",
                    "fields": [
                        {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                        {"name": "name", "type": "string", "required": True},
                        {"name": "description", "type": "text", "required": False},
                        {"name": "created_at", "type": "timestamp", "required": True}
                    ]
                }
            ])
        
        return entities

    def _call_model(self, history: List[Dict[str, str]], user_msg: str) -> Dict[str, Any]:
        """Call Claude with retry/backoff, expecting a control JSON object."""
        max_retries = 3
        base_sleep = 0.5

        system_txt = self._system_instruction()
        
        for attempt in range(max_retries):
            try:
                msgs = self._to_anthropic_messages(history, last_user=user_msg)
                resp = self._client.messages.create(
                    model=self._model_name,
                    system=system_txt,
                    messages=msgs,
                    max_tokens=800,  # Increased to allow for complete JSON responses
                    temperature=0.1,
                    timeout=30.0,  # 30 second timeout
                )
                
                # Concatenate text from content blocks
                text_parts: List[str] = []
                for block in getattr(resp, "content", []) or []:
                    t = getattr(block, "text", None)
                    if t:
                        text_parts.append(t)
                text = "".join(text_parts)
                
                # Log the raw response for debugging
                logger.debug(f"Raw AI response: {text[:200]}...")
                
                # Try direct JSON parsing
                try:
                    obj = json.loads(text.strip())
                    if isinstance(obj, dict) and "next_question" in obj:
                        return obj
                except json.JSONDecodeError as e:
                    logger.debug(f"Direct JSON parsing failed: {e}")
                
                # Try to extract JSON block from text
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1 and end > start:
                    json_text = text[start : end + 1]
                    try:
                        obj = json.loads(json_text)
                        if isinstance(obj, dict) and "next_question" in obj:
                            return obj
                    except json.JSONDecodeError as e:
                        logger.debug(f"Extracted JSON parsing failed: {e}")
                
                # Try to fix common JSON issues
                try:
                    # Remove any text before/after JSON
                    lines = text.split('\n')
                    json_lines = []
                    in_json = False
                    for line in lines:
                        if line.strip().startswith('{'):
                            in_json = True
                        if in_json:
                            json_lines.append(line)
                        if line.strip().endswith('}') and in_json:
                            break
                    
                    if json_lines:
                        json_text = '\n'.join(json_lines)
                        obj = json.loads(json_text)
                        if isinstance(obj, dict) and "next_question" in obj:
                            return obj
                except json.JSONDecodeError as e:
                    logger.debug(f"Fixed JSON parsing failed: {e}")
                
                # If all JSON parsing fails, create a fallback response
                logger.warning(f"Could not parse AI response as JSON, creating fallback. Response: {text[:100]}...")
                
                # Create a fallback response based on conversation context
                conversation_rounds = len([msg for msg in history if msg.get("role") == "user"])
                
                if conversation_rounds >= 3:
                    # If we've had enough conversation, try to complete
                    return {
                        "next_question": "Perfect! I have enough information to create your database design.",
                        "done": True,
                        "partial_spec": {
                            "app_type": "Database application",
                            "db_type": "postgresql",
                            "entities": []
                        }
                    }
                else:
                    # Continue the conversation
                    return {
                        "next_question": "What are the main features you want this system to have?",
                        "done": False,
                        "partial_spec": {}
                    }
                
            except Exception as e:
                sleep_s = base_sleep * (2 ** attempt)
                logger.warning(
                    "Claude call failed (attempt={}): {}", attempt + 1, str(e)
                )
                if attempt < max_retries - 1:
                    time.sleep(sleep_s)
                    continue

        # Final fallback if all retries fail
        logger.error("All Claude retries failed, using emergency fallback")
        conversation_rounds = len([msg for msg in history if msg.get("role") == "user"])
        
        if conversation_rounds >= 2:
            return {
                "next_question": "Perfect! I have enough information to create your database design.",
                "done": True,
                "partial_spec": {
                    "app_type": "Database application",
                    "db_type": "postgresql",
                    "entities": []
                }
            }
        else:
            return {
                "next_question": "What are the main features you want this system to have?",
                "done": False,
                "partial_spec": {}
            }

    def start_session(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new chat session and return the first question to ask the user."""
        if not name or not str(name).strip():
            raise ValueError("name is required")
        session_id = str(uuid4())
        # For Anthropic, we keep history empty and rely on system prompt
        history: List[Dict[str, str]] = []
        kickoff = (
            f"Project name: {name}. "
            + (f"Description: {description}. " if description else "")
            + "Based on this project description, I'll help you design the perfect database. Let me ask a few questions about your business needs to suggest the best database structure for you."
        )
        control = self._call_model(history, kickoff)
        with self._lock:
            self._sessions[session_id] = {
                "name": name,
                "description": description,
                "history": history + [{"role": "assistant", "content": json.dumps(control)}],
                "partial_spec": control.get("partial_spec") or {},
                "done": bool(control.get("done", False)),
                "project_id": None,
            }
        return {"session_id": session_id, "prompt": control.get("next_question") or "Describe your application type."}

    def _detect_completion_phrases(self, text: str) -> bool:
        """Detect if the AI agent is using completion phrases that indicate conversation should end."""
        completion_phrases = [
            "perfect! i have enough information",
            "great! i now have everything i need",
            "excellent! based on what you've told me",
            "i have enough information to create",
            "i can create your database schema",
            "ready to design your database",
            "i have everything i need to design"
        ]
        
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in completion_phrases)

    def next_turn(self, session_id: str, answer: str) -> Dict[str, Any]:
        """Advance the conversation with the user's answer and return the next question and merged spec."""
        with self._lock:
            state = self._sessions.get(session_id)
        if not state:
            raise ValueError("invalid session_id")
        if not answer or not str(answer).strip():
            raise ValueError("answer is required")
        history = state["history"] + [{"role": "user", "content": answer}]
        control = self._call_model(history, answer)
        partial = control.get("partial_spec") or {}
        merged = self._merge_partial(dict(state.get("partial_spec") or {}), partial)
        done = bool(control.get("done", False))
        
        # Check if AI is using completion phrases
        next_question = control.get("next_question", "")
        if self._detect_completion_phrases(next_question):
            logger.info("Detected completion phrase in AI response, marking conversation as done")
            control["done"] = True
            done = True
        
        # If AI says it's done but doesn't have complete entities, generate them
        if done and (not merged.get("entities") or len(merged.get("entities", [])) == 0):
            logger.info("Conversation marked as done but no entities found, generating basic entities")
            basic_entities = self._generate_basic_entities_from_context(history, answer)
            merged["entities"] = basic_entities
            control["partial_spec"] = merged
        
        # Ensure we have a valid database type if done
        if done and not merged.get("db_type"):
            merged["db_type"] = "postgresql"  # Default to postgresql
            control["partial_spec"] = merged
        
        with self._lock:
            state["history"] = history + [{"role": "assistant", "content": json.dumps(control)}]
            state["partial_spec"] = merged
            state["done"] = done
        return {
            "prompt": control.get("next_question") or ("Ok. Anything else?" if not done else "Ready to finalize."),
            "done": done,
            "partial_spec": merged,
        }

    def finalize(self, session_id: str) -> Dict[str, Any]:
        """Finalize the session and return a generated project_id with the accumulated spec."""
        with self._lock:
            state = self._sessions.get(session_id)
        if not state:
            raise ValueError("invalid session_id")
        spec = dict(state.get("partial_spec") or {})
        if not state.get("project_id"):
            state["project_id"] = str(uuid4())
        return {"project_id": state["project_id"], "spec": spec}


agent_service = AIAgentService()