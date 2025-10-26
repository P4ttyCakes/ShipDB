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
            "CRITICAL: You must respond with ONLY valid JSON. Start with { and end with }. No other text. "
            "You are a senior database architect and domain expert with deep business intelligence. "
            "When given ANY request to build a database system, you must: "
            "\n\n"
            "🔍 DEEP DOMAIN ANALYSIS PROCESS: "
            "1. ANALYZE THE BUSINESS MODEL: Understand the core business, revenue streams, user types, and value propositions "
            "2. IDENTIFY STAKEHOLDERS: Who are the users, admins, partners, regulators, and third-party integrations? "
            "3. MAP USER JOURNEYS: Trace complete user workflows from onboarding to core operations to offboarding "
            "4. IDENTIFY BUSINESS PROCESSES: What are the key operations, transactions, and business rules? "
            "5. CONSIDER REGULATORY REQUIREMENTS: What compliance, audit, and legal requirements exist? "
            "6. ANALYZE DATA RELATIONSHIPS: How do entities connect? What are the cardinalities and dependencies? "
            "7. IDENTIFY PERFORMANCE PATTERNS: What are the common queries, search patterns, and analytics needs? "
            "\n\n"
            "🏗️ COMPREHENSIVE SCHEMA DESIGN: "
            "- Design for REAL BUSINESS OPERATIONS, not just basic CRUD "
            "- Include ALL necessary tables for a production system "
            "- Consider edge cases, error handling, and data integrity "
            "- Design for scalability, performance, and maintainability "
            "- Include proper indexes for common query patterns "
            "- Consider data archival, backup, and recovery needs "
            "\n\n"
            "🎯 DOMAIN-SPECIFIC INTELLIGENCE: "
            "For ANY domain, think deeply about: "
            "- User management (roles, permissions, authentication, profiles) "
            "- Core business entities and their lifecycle "
            "- Transaction processing and financial flows "
            "- Communication and notification systems "
            "- Analytics, reporting, and business intelligence "
            "- Audit trails and compliance tracking "
            "- Integration points with external systems "
            "- Performance optimization and caching needs "
            "- Security, privacy, and data protection "
            "- Error handling and system monitoring "
            "\n\n"
            "QUESTIONING STRATEGY - KEEP IT MINIMAL: "
            "Your goal is to COMPLETE the conversation as quickly as possible with minimal questions. "
            "INFER DETAILS based on industry best practices and common patterns. "
            "\n"
            "RULES: "
            "- Ask MAXIMUM 2 follow-up questions after understanding the business "
            "- Each question should be SHORT (1-2 sentences maximum) "
            "- NEVER bombard the user with numbered lists of questions "
            "- NEVER ask 4+ questions at once "
            "- INFER standard features automatically: "
            "  * User authentication and profiles for any system "
            "  * Payment processing for e-commerce "
            "  * Inventory tracking for product businesses "
            "  * Scheduling for service businesses "
            "  * Audit trails for financial systems "
            "  * Notifications and messaging "
            "  * Admin and role management "
            "\n"
            "Ask ONLY what is absolutely necessary to distinguish between fundamentally different designs. "
            "For example, if you already know it's 'a soda company', don't ask about: "
            "- Pricing tiers, discounts, contracts (INFER standard e-commerce pricing) "
            "- Inventory locations (INFER multi-warehouse support) "
            "- Order tracking (INFER full order lifecycle) "
            "- Manufacturing details (INFER batch tracking and quality control) "
            "\n"
            "COMPLETE EARLY: After 1-2 user responses describing their business, you should set done=true. "
            "It's BETTER to generate a complete database with inferred features than to ask more questions."
            "\n\n"
            "NEVER ask technical questions about: "
            "- Database constraints, indexes, foreign keys "
            "- Data types, field specifications "
            "- Database optimization details "
            "\n\n"
            "CRITICAL JSON FORMAT REQUIREMENT: "
            "You MUST respond with ONLY a valid JSON object. No other text, explanations, or formatting. "
            "ABSOLUTE REQUIREMENT: Your response must start with the character { and end with }. "
            "Any text before { or after } will cause the system to fail. "
            "Do not include any explanatory text, greetings, or phrases. "
            "The JSON must have exactly these keys: next_question, done, partial_spec "
            "\n\n"
            "Example response format: "
            '{"next_question": "What type of users will use this system?", "done": false, "partial_spec": {}}'
            "\n\n"
            "Example COMPLETE response when done=true: "
            '{"next_question": "Perfect! I have enough information to create your database design.", "done": true, "partial_spec": {"app_type": "E-commerce Platform", "db_type": "postgresql", "entities": [{"name": "products", "fields": [{"name": "id", "type": "uuid", "required": true, "primary_key": true}, {"name": "name", "type": "string", "required": true}, {"name": "price", "type": "decimal", "required": true}, {"name": "inventory_count", "type": "integer", "required": true}, {"name": "created_at", "type": "timestamp", "required": true}]}, {"name": "customers", "fields": [{"name": "id", "type": "uuid", "required": true, "primary_key": true}, {"name": "name", "type": "string", "required": true}, {"name": "email", "type": "string", "required": true, "unique": true}, {"name": "phone", "type": "string", "required": false}, {"name": "created_at", "type": "timestamp", "required": true}]}, {"name": "orders", "fields": [{"name": "id", "type": "uuid", "required": true, "primary_key": true}, {"name": "customer_id", "type": "uuid", "required": true, "foreign_key": {"table": "customers", "field": "id"}}, {"name": "order_date", "type": "timestamp", "required": true}, {"name": "status", "type": "string", "required": true}, {"name": "created_at", "type": "timestamp", "required": true}]}, {"name": "order_items", "fields": [{"name": "id", "type": "uuid", "required": true, "primary_key": true}, {"name": "order_id", "type": "uuid", "required": true, "foreign_key": {"table": "orders", "field": "id"}}, {"name": "product_id", "type": "uuid", "required": true, "foreign_key": {"table": "products", "field": "id"}}, {"name": "quantity", "type": "integer", "required": true}, {"name": "unit_price", "type": "decimal", "required": true}]}, {"name": "payments", "fields": [{"name": "id", "type": "uuid", "required": true, "primary_key": true}, {"name": "order_id", "type": "uuid", "required": true, "foreign_key": {"table": "orders", "field": "id"}}, {"name": "amount", "type": "decimal", "required": true}, {"name": "payment_method", "type": "string", "required": true}, {"name": "status", "type": "string", "required": true}, {"name": "created_at", "type": "timestamp", "required": true}]}]}}'
            "\n\n"
            "JSON VALIDATION RULES: "
            "- Start response with { and end with } "
            "- Use double quotes for all strings "
            "- Use true/false for booleans (not True/False) "
            "- Ensure all brackets and braces are properly closed "
            "- No trailing commas "
            "- Escape any quotes inside strings "
            "\n\n"
            "When done=true, partial_spec must be a COMPLETE database specification with: "
            "- app_type: string describing the application "
            "- db_type: 'postgresql' or 'dynamodb' "
            "- entities: array of objects with 'name' and 'fields' "
            "- Each field must have: name, type, required (boolean), and appropriate constraints "
            "- MANDATORY: Each entity MUST have an 'id' field with primary_key: true "
            "- MANDATORY: Email fields MUST have unique: true "
            "- MANDATORY: Foreign key fields MUST have foreign_key: {table: 'entity_name', field: 'id'} "
            "- Include primary keys, foreign keys, indexes, and relationships "
            "- CRITICAL: Generate at least 3-5 entities for a complete system "
            "- CRITICAL: Each entity must have at least 3-5 fields "
            "\n\n"
            "SCHEMA UPDATE RULES (when continuing conversations): "
            "- When user requests changes AFTER you've marked done=true, provide UPDATED entities "
            "- Include ALL existing entities PLUS any new/modified entities "
            "- If adding new features (e.g., 'stories' to social media), add new entities "
            "- If modifying existing entities, include the updated version "
            "- NEVER provide empty entities array - always include complete schema "
            "- Example: If user says 'add stories feature', include stories entity + all existing entities "
            "- Example: If user says 'add admin role to users', update users entity with admin fields "
            "\n\n"
            "RELATIONSHIP DESIGN RULES - MINIMIZE FOREIGN KEYS: "
            "- ONLY create foreign keys when absolutely necessary for data integrity "
            "- AVOID creating foreign keys for optional or lightweight relationships "
            "- ONE-TO-MANY relationships: Use foreign keys ONLY when the relationship is core to the business logic "
            "- EXAMPLE GOOD USAGE: "
            "  * Orders → order_items (order MUST have items) "
            "  * Payments → orders (payment MUST reference order) "
            "- EXAMPLE BAD USAGE (AVOID): "
            "  * Products → suppliers (just store supplier name as string, not FK) "
            "  * Users → addresses (just store address fields directly) "
            "  * Materials → suppliers (not critical to core functionality) "
            "- MANY-TO-MANY: Create junction tables ONLY when absolutely necessary "
            "- DO NOT create foreign keys for: "
            "  * Optional lookups that can be denormalized "
            "  * Cross-references that don't enforce critical business rules "
            "  * Relationships that can be inferred from other data "
            "- EVERY foreign key should enforce a critical business constraint "
            "- PREFER storing denormalized data over creating unnecessary foreign keys "
            "- MAXIMUM 2-3 foreign keys per table - if you need more, the design is too normalized "
            "- NEVER create circular foreign key references "
            "\n\n"
            "MANY-TO-MANY RELATIONSHIP DETECTION: "
            "When you see these patterns, create junction tables: "
            "- 'orders with multiple products' → order_items table "
            "- 'users can have multiple roles' → user_roles table "
            "- 'students enrolled in multiple courses' → enrollments table "
            "- 'patients can see multiple doctors' → appointments table "
            "- 'properties favorited by multiple users' → favorites table "
            "- 'products belong to multiple categories' → product_categories table "
            "- 'users follow multiple users' → follows table "
            "- 'posts have multiple tags' → post_tags table "
            "- 'events have multiple attendees' → event_attendees table "
            "\n\n"
            "ENTITY GENERATION REQUIREMENTS: "
            "When you set done=true, you MUST generate complete entities in the JSON response. "
            "Do NOT rely on fallback logic. Generate appropriate entities based on the business domain: "
            "- Healthcare: patients, doctors, appointments, medical_records, prescriptions "
            "- E-commerce: products, customers, orders, order_items, payments, categories "
            "- Real Estate: users, properties, favorites, property_views, agents "
            "- Stock Trading: users, stocks, transactions, portfolios, watchlists "
            "- Education: students, courses, enrollments, assignments, grades "
            "- Social: users, posts, comments, likes, follows "
            "\n\n"
            "QUESTION STRATEGY - ASK SMART QUESTIONS: "
            "After the first business description, ask 1-2 targeted questions to clarify the scope. "
            "If the user gives specific information, INFER obvious details instead of asking about them. "
            "For example: "
            "- If they say 'rental properties with filters' → You can INFER: users need to browse/search properties, properties have attributes (price, location, bedrooms), users need authentication. Don't ask if users need accounts - it's obvious. "
            "- If they say 'e-commerce platform' → You can INFER: products, orders, customers, payments, cart. Don't ask if users need to buy things - it's obvious. "
            "Only ask questions about things that are genuinely ambiguous or could go multiple ways. "
            "Don't ask follow-up questions to confirm things you already know or can reasonably infer. "
            "\n\n"
            "INTELLIGENT COMPLETION: "
            "When you have enough information to create a complete database design, set done=true. "
            "You have enough information when you understand the business domain and can generate "
            "appropriate entities with proper fields. Don't rush to complete - gather sufficient details first. "
            "\n\n"
            "CRITICAL: When done=true, you MUST include complete entities in the partial_spec. "
            "Do NOT set done=true with empty entities. Generate at least 3-5 entities with "
            "proper fields for each entity. This is MANDATORY for successful schema generation."
            "\n\n"
            "CONVERSATION COMPLETION DETECTION: "
            "Set done=true when you have enough information to create a complete database design. "
            "You have enough information when: "
            "- You understand the business domain and core entities "
            "- You know the main data fields and relationships needed "
            "- You have sufficient context to make intelligent database choices "
            "\n\n"
            "COMPLETION STRATEGY - BALANCE BETWEEN GATHERING INFO AND NOT OVER-ASKING: "
            "Gather enough information to build a complete database, but don't ask for obvious details. "
            "You can complete when you have: "
            "- Clear understanding of the main business domain and entities "
            "- Knowledge of key operations users will perform "
            "- Sufficient detail to generate logical schema with 3-5+ entities "
            "Complete after 2-4 user responses IF you have clear information. "
            "Don't force yourself to ask more questions if you can already generate a good schema. "
            "\n\n"
            "SMART COMPLETION: "
            "If the user gives specific, detailed information about their business and needs, "
            "you can complete after fewer questions. For example: "
            "- User: 'Rental property search with filters by price, bedrooms, location' "
            "- You already know enough: users, properties, search/filter functionality "
            "- Don't ask if they need user accounts, authentication, or properties - it's obvious "
            "- Complete and generate the schema "
            "Be confident in your inferences - you don't need to confirm every obvious detail. "
            "\n\n"
            "COMPLETION TRIGGERS: "
            "Set done=true when you see explicit completion signals: "
            "- 'that covers all', 'that's everything', 'no other requirements' etc. "
            "OR when you have enough information to generate a complete schema: "
            "- After 2-4 meaningful exchanges where you understand the domain "
            "- When the user gives specific details about their business needs "
            "- When you can confidently infer the main entities and relationships "
            "TRUST YOUR JUDGMENT: If you understand the business well enough to generate "
            "a logical database schema with multiple entities, complete the conversation. "
            "You don't need to confirm every detail - some things are obviously needed. "
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
            if k == "entities" and isinstance(v, list) and isinstance(base.get(k), list):
                # Special handling for entities - merge intelligently
                base[k] = self._merge_entities(base[k], v)
            elif isinstance(v, dict) and isinstance(base.get(k), dict):
                base[k] = self._merge_partial(base[k], v)
            else:
                base[k] = v
        return base
    
    def _merge_entities(self, base_entities: List[Dict[str, Any]], incoming_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Intelligently merge entity lists, updating existing entities and adding new ones."""
        # Create a map of existing entities by name
        entity_map = {entity["name"]: entity for entity in base_entities}
        
        # Process incoming entities
        for incoming_entity in incoming_entities:
            entity_name = incoming_entity.get("name")
            if entity_name in entity_map:
                # Update existing entity - merge fields intelligently
                existing_entity = entity_map[entity_name]
                existing_entity.update(incoming_entity)  # Update all fields
                
                # Merge fields if both have fields
                if "fields" in incoming_entity and "fields" in existing_entity:
                    existing_entity["fields"] = self._merge_fields(existing_entity["fields"], incoming_entity["fields"])
            else:
                # Add new entity
                entity_map[entity_name] = incoming_entity
        
        return list(entity_map.values())
    
    def _merge_fields(self, base_fields: List[Dict[str, Any]], incoming_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Intelligently merge field lists, updating existing fields and adding new ones."""
        # Create a map of existing fields by name
        field_map = {field["name"]: field for field in base_fields}
        
        # Process incoming fields
        for incoming_field in incoming_fields:
            field_name = incoming_field.get("name")
            if field_name in field_map:
                # Update existing field
                field_map[field_name].update(incoming_field)
            else:
                # Add new field
                field_map[field_name] = incoming_field
        
        return list(field_map.values())

    def _validate_complete_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate that a spec is complete enough for schema generation."""
        if not isinstance(spec, dict):
            return False
        
        # Must have app_type
        if not spec.get("app_type"):
            return False
            
        # Must have db_type
        if spec.get("db_type") not in ["postgresql", "dynamodb"]:
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
    
    # Removed hard-coded entity generation - AI should generate appropriate entities based on business analysis

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
                    max_tokens=4000,
                    temperature=0.0,
                    timeout=30.0,
                )
                
                # Concatenate text from content blocks
                text_parts: List[str] = []
                for block in getattr(resp, "content", []) or []:
                    t = getattr(block, "text", None)
                    if t:
                        text_parts.append(t)
                text = "".join(text_parts)
                
                # Log the raw response for debugging
                logger.debug(f"Raw AI response: {text[:500]}...")
                
                # Parse JSON from AI response
                obj = self._parse_json_response(text)
                if obj is None:
                    logger.error(f"Failed to parse AI response. Raw text: {text[:1000]}")
                    raise ValueError(f"AI service returned invalid JSON. Response: {text[:200]}...")
                
                if not isinstance(obj, dict):
                    logger.error(f"AI response is not a dict: {type(obj)} - {obj}")
                    raise ValueError(f"AI service returned invalid response type: {type(obj)}")
                
                if "next_question" not in obj:
                    logger.error(f"AI response missing 'next_question' field. Response: {obj}")
                    raise ValueError("AI service returned response without 'next_question' field")
                
                return obj
                
            except Exception as e:
                sleep_s = base_sleep * (2 ** attempt)
                logger.warning(
                    "Claude call failed (attempt={}): {}", attempt + 1, str(e)
                )
                if attempt < max_retries - 1:
                    time.sleep(sleep_s)
                    continue

        # All retries failed
        logger.error("All Claude retries failed")
        raise RuntimeError("AI service unavailable after multiple retries. Please try again later.")
    
    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from AI response with robust error handling."""
        if not text or not text.strip():
            logger.error("Empty text provided to JSON parser")
            return None
        
        import re
        
        # Strategy 1: Try direct JSON parsing
        try:
            obj = json.loads(text.strip())
            if isinstance(obj, dict) and "next_question" in obj:
                logger.debug("Direct JSON parsing succeeded")
                return obj
        except json.JSONDecodeError as e:
            logger.debug(f"Direct JSON parsing failed: {e}")
        
        # Strategy 2: Remove markdown code blocks if present
        cleaned_text = text
        # Remove ```json ... ``` blocks
        cleaned_text = re.sub(r'```json\s*\n?', '', cleaned_text)
        cleaned_text = re.sub(r'```\s*\n?', '', cleaned_text)
        
        try:
            obj = json.loads(cleaned_text.strip())
            if isinstance(obj, dict) and "next_question" in obj:
                logger.debug("JSON parsing after markdown removal succeeded")
                return obj
        except json.JSONDecodeError as e:
            logger.debug(f"JSON parsing after markdown removal failed: {e}")
        
        # Strategy 3: Extract JSON block (content between first { and last })
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                json_text = text[start : end + 1]
                obj = json.loads(json_text)
                if isinstance(obj, dict) and "next_question" in obj:
                    logger.debug("Extracted JSON block parsing succeeded")
                    return obj
            except json.JSONDecodeError as e:
                logger.debug(f"Extracted JSON block parsing failed: {e}")
        
        # Strategy 4: Try line by line to find JSON object
        lines = text.split('\n')
        json_lines = []
        in_json = False
        brace_count = 0
        
        for line in lines:
            stripped = line.strip()
            if '{' in stripped and not in_json:
                in_json = True
                json_lines.append(line)
                brace_count += stripped.count('{') - stripped.count('}')
            elif in_json:
                json_lines.append(line)
                brace_count += stripped.count('{') - stripped.count('}')
                if brace_count == 0:
                    break
        
        if json_lines:
            try:
                json_text = '\n'.join(json_lines)
                obj = json.loads(json_text)
                if isinstance(obj, dict) and "next_question" in obj:
                    logger.debug("Line-by-line JSON extraction succeeded")
                    return obj
            except json.JSONDecodeError as e:
                logger.debug(f"Line-by-line JSON extraction failed: {e}")
        
        # Strategy 5: Try with character-level balancing
        result = self._extract_json_with_balance(text)
        if result:
            try:
                obj = json.loads(result)
                if isinstance(obj, dict) and "next_question" in obj:
                    logger.debug("Character-level balanced JSON extraction succeeded")
                    return obj
            except json.JSONDecodeError as e:
                logger.debug(f"Character-level balanced JSON parsing failed: {e}")
        
        # All strategies failed - log the actual error
        logger.error(f"Could not parse AI response as valid JSON. Response preview: {text[:500]}")
        logger.error(f"Full response length: {len(text)} characters")
        return None
    
    def _extract_json_with_balance(self, text: str) -> str:
        """Extract JSON by balancing braces and brackets."""
        start = text.find('{')
        if start == -1:
            return ""
        
        depth = 0
        end = start
        
        for i, char in enumerate(text[start:], start):
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    end = i
                    break
        
        if depth == 0:
            return text[start:end + 1]
        return ""

    def start_session(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new chat session and return the first question to ask the user."""
        if not name or not str(name).strip():
            raise ValueError("name is required")
        session_id = str(uuid4())
        
        # The first question is always "Describe and explain your business"
        # No need to call the AI model - just return the standard first question
        first_question = "Describe and explain your business. What does your business do? What are the main products or services you offer? What are your core operations?"
        
        # Initialize session with the first question
        with self._lock:
            self._sessions[session_id] = {
                "name": name,
                "description": description,
                "history": [{"role": "assistant", "content": first_question}],
                "partial_spec": {},
                "done": False,
                "project_id": None,
            }
        
        return {"session_id": session_id, "prompt": first_question}

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
        
        # _call_model guarantees control is valid dict with required fields
        partial = control.get("partial_spec") or {}
        merged = self._merge_partial(dict(state.get("partial_spec") or {}), partial)
        done = bool(control.get("done", False))
        
        # Check if AI is using completion phrases
        next_question = control.get("next_question", "")
        if self._detect_completion_phrases(next_question):
            logger.info("Detected completion phrase in AI response, marking conversation as done")
            control["done"] = True
            done = True
        
        # If AI says it's done but doesn't have complete entities, let the AI handle it
        # Don't fall back to hard-coded entities - let the AI generate appropriate ones
        if done and (not merged.get("entities") or len(merged.get("entities", [])) == 0):
            logger.info("Conversation marked as done but no entities found - AI should generate appropriate entities")
            # Don't override with hard-coded entities - trust the AI's business analysis
        
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