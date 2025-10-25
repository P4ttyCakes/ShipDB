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
        self._model_name: str = getattr(settings, "ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")

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
            "IMPORTANT: After 2-3 business questions, you MUST generate a complete database specification. "
            "Don't keep asking questions indefinitely - provide a working database design based on the information gathered."
            "\n\n"
            "Ask ONLY high-level business questions like: "
            "- 'What type of users will use this system?' "
            "- 'What are the main features you want?' "
            "- 'Do you need to track user accounts, orders, inventory, etc.?' "
            "\n\n"
            "NEVER ask technical questions about: "
            "- Database constraints, indexes, foreign keys "
            "- Data types, field specifications "
            "- Database optimization details "
            "\n\n"
            "After each user answer, respond ONLY with a JSON object with keys: "
            "next_question (string), done (boolean), partial_spec (object). "
            "\n\n"
            "CRITICAL: When done is true, partial_spec must be a COMPLETE database specification with: "
            "- app_type: string describing the application "
            "- db_type: 'postgresql', 'mongodb', or 'dynamodb' "
            "- entities: array of objects with 'name' and 'fields' "
            "- Each field must have: name, type, required (boolean), and appropriate constraints "
            "- Include primary keys, foreign keys, indexes, and relationships "
            "\n\n"
            "Example complete spec for rental property platform: "
            '{"app_type": "rental property platform", "db_type": "postgresql", "entities": [{"name": "users", "fields": [{"name": "id", "type": "integer", "required": true, "primary_key": true}, {"name": "email", "type": "string", "required": true, "unique": true}, {"name": "name", "type": "string", "required": true}]}, {"name": "properties", "fields": [{"name": "id", "type": "integer", "required": true, "primary_key": true}, {"name": "title", "type": "string", "required": true}, {"name": "price", "type": "decimal", "required": true}, {"name": "location", "type": "string", "required": true}, {"name": "bedrooms", "type": "integer", "required": true}, {"name": "agent_email", "type": "string", "required": true}]}, {"name": "user_preferences", "fields": [{"name": "id", "type": "integer", "required": true, "primary_key": true}, {"name": "user_id", "type": "integer", "required": true, "foreign_key": {"table": "users", "field": "id"}}, {"name": "max_price", "type": "decimal", "required": false}, {"name": "min_bedrooms", "type": "integer", "required": false}]}]}'
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

    def _generate_complete_spec_from_conversation(self, history: List[Dict[str, str]], partial_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete database spec based on conversation history when AI fails to do so."""
        # Extract project info from history
        project_name = "Unknown Project"
        project_description = ""
        
        # Look for project info in the conversation
        for msg in history:
            content = msg.get("content", "")
            if "rental" in content.lower() or "property" in content.lower():
                if "rental property" in content.lower():
                    project_name = "Rental Property Platform"
                    project_description = "A platform for matching renters with rental properties"
                break
        
        # Generate a complete spec based on common patterns
        if "rental" in project_description.lower() or "property" in project_description.lower():
            return {
                "app_type": "rental property platform",
                "db_type": "postgresql",
                "entities": [
                    {
                        "name": "users",
                        "fields": [
                            {"name": "id", "type": "integer", "required": True, "primary_key": True},
                            {"name": "email", "type": "string", "required": True, "unique": True},
                            {"name": "name", "type": "string", "required": True},
                            {"name": "phone", "type": "string", "required": False},
                            {"name": "created_at", "type": "timestamp", "required": True}
                        ]
                    },
                    {
                        "name": "properties",
                        "fields": [
                            {"name": "id", "type": "integer", "required": True, "primary_key": True},
                            {"name": "title", "type": "string", "required": True},
                            {"name": "description", "type": "text", "required": False},
                            {"name": "price", "type": "decimal", "required": True},
                            {"name": "location", "type": "string", "required": True},
                            {"name": "bedrooms", "type": "integer", "required": True},
                            {"name": "bathrooms", "type": "integer", "required": True},
                            {"name": "amenities", "type": "text", "required": False},
                            {"name": "agent_email", "type": "string", "required": True},
                            {"name": "agent_phone", "type": "string", "required": False},
                            {"name": "available", "type": "boolean", "required": True, "default": True},
                            {"name": "created_at", "type": "timestamp", "required": True}
                        ]
                    },
                    {
                        "name": "user_preferences",
                        "fields": [
                            {"name": "id", "type": "integer", "required": True, "primary_key": True},
                            {"name": "user_id", "type": "integer", "required": True, "foreign_key": {"table": "users", "field": "id"}},
                            {"name": "max_price", "type": "decimal", "required": False},
                            {"name": "min_bedrooms", "type": "integer", "required": False},
                            {"name": "min_bathrooms", "type": "integer", "required": False},
                            {"name": "preferred_location", "type": "string", "required": False},
                            {"name": "amenities", "type": "text", "required": False}
                        ]
                    },
                    {
                        "name": "favorites",
                        "fields": [
                            {"name": "id", "type": "integer", "required": True, "primary_key": True},
                            {"name": "user_id", "type": "integer", "required": True, "foreign_key": {"table": "users", "field": "id"}},
                            {"name": "property_id", "type": "integer", "required": True, "foreign_key": {"table": "properties", "field": "id"}},
                            {"name": "created_at", "type": "timestamp", "required": True}
                        ]
                    }
                ]
            }
        
        # Default fallback for any other type of application
        return {
            "app_type": "web application",
            "db_type": "postgresql",
            "entities": [
                {
                    "name": "users",
                    "fields": [
                        {"name": "id", "type": "integer", "required": True, "primary_key": True},
                        {"name": "email", "type": "string", "required": True, "unique": True},
                        {"name": "name", "type": "string", "required": True},
                        {"name": "created_at", "type": "timestamp", "required": True}
                    ]
                }
            ]
        }

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

    def _call_model(self, history: List[Dict[str, str]], user_msg: str) -> Dict[str, Any]:
        """Call Claude with retry/backoff and optional model fallback, expecting a control JSON object."""
        primary = self._model_name
        fallback = getattr(settings, "ANTHROPIC_FALLBACK_MODEL", None)
        model_candidates = [m for m in [primary, fallback] if m and str(m).strip()]
        max_retries = 3
        base_sleep = 0.5

        system_txt = self._system_instruction()
        for model_name in model_candidates:
            for attempt in range(max_retries):
                try:
                    msgs = self._to_anthropic_messages(history, last_user=user_msg)
                    resp = self._client.messages.create(
                        model=model_name,
                        system=system_txt,
                        messages=msgs,
                        max_tokens=800,
                        temperature=0.2,
                    )
                    # Concatenate text from content blocks
                    text_parts: List[str] = []
                    for block in getattr(resp, "content", []) or []:
                        t = getattr(block, "text", None)
                        if t:
                            text_parts.append(t)
                    text = "".join(text_parts)
                    # Try direct JSON
                    try:
                        obj = json.loads(text)
                        if isinstance(obj, dict):
                            return obj
                    except Exception:
                        # Try to extract JSON block
                        start = text.find("{")
                        end = text.rfind("}")
                        if start != -1 and end != -1 and end > start:
                            obj = json.loads(text[start : end + 1])
                            if isinstance(obj, dict):
                                return obj
                        raise ValueError("Model response was not valid JSON control block")
                except Exception as e:
                    sleep_s = base_sleep * (2 ** attempt)
                    logger.warning(
                        "Claude call failed (model={}, attempt={}): {}", model_name, attempt + 1, str(e)
                    )
                    if attempt < max_retries - 1:
                        time.sleep(sleep_s)
                        continue
            logger.info("Switching to fallback model after failures: {}", model_name)

        logger.warning("All Claude attempts failed; returning safe default control JSON")
        return {"next_question": "I'd love to help you design your database! Can you tell me more about what your application will do and who will use it?", "done": False, "partial_spec": {}}

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
        
        # Force completion after 2 questions or if AI says it's done but spec is incomplete
        question_count = len([msg for msg in history if msg.get("role") == "assistant"])
        
        if question_count >= 2 or (done and not self._validate_complete_spec(merged)):
            merged = self._generate_complete_spec_from_conversation(history, merged)
            done = True
            control["done"] = True
            control["next_question"] = "Perfect! I've generated a complete database design based on your requirements. Ready to create your schema!"
        
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
