import json
import re
import threading
import time
from typing import Dict, Any, Optional, List
from uuid import uuid4

from loguru import logger
from backend.app.core.config import settings

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
            raise RuntimeError("anthropic SDK not installed. Install it with: pip install anthropic")
        
        api_key = getattr(settings, "ANTHROPIC_API_KEY", None)
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not configured. Please set it in your environment variables or .env file.")
        
        # Validate API key format (should start with 'sk-' and be reasonably long)
        if not api_key.startswith('sk-') or len(api_key) < 20:
            logger.warning(f"ANTHROPIC_API_KEY format looks suspicious (length: {len(api_key)}). Please verify it's correct.")
        
        try:
            self._client = Anthropic(api_key=api_key)
            self._model_name: str = getattr(settings, "ANTHROPIC_MODEL", "claude-3-haiku-20240307")
            logger.info(f"Anthropic client initialized with model: {self._model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise RuntimeError(f"Failed to initialize Anthropic client: {e}. Please check your ANTHROPIC_API_KEY.")

    def _system_instruction(self) -> str:
        """Return the instruction used to constrain the model to a JSON control response."""
        return (
            "You are a database architect. Respond with ONLY valid JSON: {\"next_question\": \"...\", \"done\": false, \"partial_spec\": {}}"
            "\n\n"
            "JSON FORMAT (CRITICAL): "
            "- Start with { and end with }. NO text before or after. "
            "- NO greetings, explanations, or markdown. Just raw JSON. "
            "- Required keys: next_question, done, partial_spec"
            "\n\n"
            "QUESTIONING STRATEGY: "
            "- Ask 2-4 targeted questions about business operations before completing. "
            "- For minimal inputs (e.g., 'boba shop'), ask: menu items, ordering process, customer data, inventory, employees. "
            "- Ask SPECIFIC business questions, NOT confirmations like 'does this look good?' "
            "- Each question: 1-2 sentences max. One question at a time. "
            "\n\n"
            "COMPLETION CRITERIA (done=true): "
            "- You understand business operations and workflows "
            "- You know key entities and relationships "
            "- You can generate 3-5+ entities with proper fields "
            "- Typically requires 3-5 user responses (NOT 1-2) "
            "- When done=true, include COMPLETE entities in partial_spec"
            "\n\n"
            "SCHEMA REQUIREMENTS (when done=true): "
            "- partial_spec must have: app_type, db_type ('postgresql' or 'dynamodb'), entities array "
            "- Each entity: name, fields array "
            "- Each field: name, type, required (boolean), primary_key (if applicable), foreign_key (if applicable) "
            "- Every entity MUST have an 'id' field with primary_key: true "
            "- Email fields MUST have unique: true "
            "- Generate 3-5+ entities, each with 3-5+ fields"
            "\n\n"
            "FOREIGN KEYS: "
            "- Only create FKs for critical business relationships (e.g., orders→order_items, payments→orders) "
            "- Avoid FKs for optional/denormalizable relationships "
            "- Max 2-3 foreign keys per table"
            "\n\n"
            "EXAMPLES: "
            "- Question: {\"next_question\": \"What types of menu items do you offer?\", \"done\": false, \"partial_spec\": {}}"
            "- Complete: {\"next_question\": \"\", \"done\": true, \"partial_spec\": {\"app_type\": \"Boba Shop\", \"db_type\": \"postgresql\", \"entities\": [...]}}"
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
        last_error = None

        system_txt = self._system_instruction()
        
        for attempt in range(max_retries):
            try:
                msgs = self._to_anthropic_messages(history, last_user=user_msg)
                # Increased timeout for more reliability
                logger.debug(f"Calling Claude API (attempt {attempt + 1}/{max_retries}) with model {self._model_name}")
                try:
                    resp = self._client.messages.create(
                        model=self._model_name,
                        system=system_txt,
                        messages=msgs,
                        max_tokens=4000,
                        temperature=0.0,
                        timeout=60.0,  # Increased timeout from 30s to 60s for reliability
                    )
                except Exception as api_error:
                    error_type = type(api_error).__name__
                    error_msg = str(api_error)
                    
                    # Check for Anthropic-specific error types and content policy violations
                    error_lower = error_msg.lower()
                    
                    # Check for content policy violations first (don't retry these)
                    if any(term in error_lower for term in ["content_policy", "content policy", "policy violation", "moderation", "safety", "blocked", "inappropriate"]):
                        logger.error(f"Content policy violation detected: {error_msg}")
                        raise ValueError(f"Your request may violate content policies. Please rephrase your request to describe a legitimate business use case.")
                    
                    # Check status codes if available
                    if hasattr(api_error, 'status_code'):
                        status_code = api_error.status_code
                        logger.warning(f"Claude API call failed with HTTP {status_code}: {error_msg}")
                        
                        # Content policy violations typically return 400
                        if status_code == 400 and ("content" in error_lower or "policy" in error_lower):
                            logger.error(f"Content policy violation (400): {error_msg}")
                            raise ValueError(f"Your request may violate content policies. Please rephrase your request to describe a legitimate business use case.")
                    
                    logger.warning(f"Claude API call raised {error_type}: {error_msg}")
                    raise  # Re-raise to be caught by outer exception handler
                
                # Concatenate text from content blocks
                text_parts: List[str] = []
                for block in getattr(resp, "content", []) or []:
                    t = getattr(block, "text", None)
                    if t:
                        text_parts.append(t)
                text = "".join(text_parts)
                
                # Log the raw response for debugging
                logger.debug(f"Raw AI response: {text[:500]}...")
                
                # Parse JSON from AI response (always returns a dict, even if parsing fails)
                obj = self._parse_json_response(text)
                
                # Ensure required fields exist
                if "next_question" not in obj:
                    obj["next_question"] = text.strip() if text else "Please continue..."
                if "done" not in obj:
                    obj["done"] = False
                if "partial_spec" not in obj:
                    obj["partial_spec"] = {}
                
                return obj
                
            except Exception as e:
                sleep_s = base_sleep * (2 ** attempt)
                error_type = type(e).__name__
                error_details = str(e)
                last_error = f"{error_type}: {error_details}"
                
                # Log detailed error information - use error level for final attempt
                log_level = logger.error if attempt == max_retries - 1 else logger.warning
                log_level(
                    "Claude call failed (attempt={}/{}, error_type={}): {}", 
                    attempt + 1, max_retries, error_type, error_details
                )
                
                # Log full exception traceback for debugging on final attempt
                if attempt == max_retries - 1:
                    logger.error(f"Full exception traceback for final failure:", exc_info=True)
                
                # Check for specific error types that shouldn't be retried
                error_lower = error_details.lower()
                
                # Content policy violations - don't retry
                if any(term in error_lower for term in ["content_policy", "content policy", "policy violation", "moderation", "safety", "blocked"]):
                    logger.error(f"Content policy violation detected: {error_details}")
                    raise ValueError(f"Your request may violate content policies. Please rephrase your request to describe a legitimate business use case.")
                
                # Authentication errors - don't retry
                if any(term in error_lower for term in ["authentication", "api_key", "401", "unauthorized", "invalid api key"]):
                    logger.error(f"Authentication error detected - check ANTHROPIC_API_KEY: {error_details}")
                    raise ValueError(f"Invalid API credentials: {error_details}. Please check your ANTHROPIC_API_KEY environment variable.")
                
                # Rate limit errors - don't retry immediately
                if any(term in error_lower for term in ["rate_limit", "429", "rate limit", "too many requests"]):
                    logger.error(f"Rate limit exceeded: {error_details}")
                    raise RuntimeError(f"Rate limit exceeded. Please wait a moment and try again: {error_details}")
                
                # Check for Anthropic APIError specific attributes
                if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                    status = e.response.status_code
                    if status == 400:
                        logger.warning(f"Bad request (400) - may be content policy violation: {error_details}")
                        if "content" in error_lower or "policy" in error_lower:
                            raise ValueError(f"Request may violate content policies. Please rephrase your request appropriately.")
                
                # Network/timeout errors - these are retryable
                if any(term in error_lower for term in ["timeout", "connection", "network", "socket"]):
                    logger.warning(f"Network/timeout error (will retry): {error_details}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {sleep_s}s...")
                    time.sleep(sleep_s)
                    continue

        # All retries failed - provide more context with actionable message
        error_msg = last_error or "Unknown error"
        logger.error(f"All Claude retries failed after {max_retries} attempts. Last error: {error_msg}")
        logger.error(f"Full error context: {last_error}")
        
        # Create a user-friendly error message based on error type
        error_lower = error_msg.lower()
        if any(term in error_lower for term in ["timeout", "timed out", "connection", "network"]):
            user_msg = f"Connection timeout after {max_retries} retries. The AI service took too long to respond. Please check your internet connection and try again in a moment."
        elif any(term in error_lower for term in ["api", "key", "credential", "authentication", "unauthorized"]):
            user_msg = f"API configuration error: {error_msg}. Please verify your ANTHROPIC_API_KEY environment variable is set correctly and valid."
        elif "rate limit" in error_lower or "429" in error_lower:
            user_msg = f"Rate limit exceeded: {error_msg}. Please wait a few moments before trying again."
        else:
            user_msg = f"AI service unavailable after {max_retries} retries. Error: {error_msg}. Please check your ANTHROPIC_API_KEY configuration and network connection, then try again."
        
        raise RuntimeError(user_msg)
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON from AI response with robust extraction and error handling.
        This method handles cases where the AI returns explanatory text along with JSON.
        Always returns a valid dict structure, never raises exceptions.
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to JSON parser, using default response")
            return {
                "next_question": "Please continue...",
                "partial_spec": {},
                "done": False
            }
        
        import re
        
        # Clean the text first - remove any leading/trailing whitespace
        text = text.strip()
        
        # Strategy 1: Try direct JSON parsing (fastest path)
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                # Validate it has the expected structure
                if "next_question" in obj or "partial_spec" in obj or "done" in obj:
                    logger.debug("Successfully parsed JSON via direct parsing")
                    return self._ensure_required_fields(obj)
        except json.JSONDecodeError as e:
            logger.debug(f"Direct JSON parsing failed: {e}")
        
        # Strategy 2: Extract JSON from markdown code blocks (```json ... ```)
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL | re.IGNORECASE)
        if json_match:
            try:
                json_content = json_match.group(1).strip()
                obj = json.loads(json_content)
                if isinstance(obj, dict):
                    logger.debug("Successfully parsed JSON from markdown code block")
                    return self._ensure_required_fields(obj)
            except json.JSONDecodeError as e:
                logger.debug(f"Markdown code block JSON parsing failed: {e}")
        
        # Strategy 3: Find all JSON objects in the text and try to parse the largest one
        # This handles cases where there's text before/after JSON
        json_candidates = self._find_all_json_objects(text)
        for candidate_json in json_candidates:
            try:
                # Try to fix common JSON issues before parsing
                fixed_json = self._fix_common_json_issues(candidate_json)
                obj = json.loads(fixed_json)
                if isinstance(obj, dict):
                    # Prefer objects that have our expected structure
                    if "next_question" in obj or "partial_spec" in obj or "done" in obj:
                        logger.debug("Successfully parsed JSON from extracted object")
                        return self._ensure_required_fields(obj)
                    # If no expected structure but it's a valid dict, use it as partial_spec
                    elif len(obj) > 0:
                        logger.debug("Found valid JSON object, using as partial_spec")
                        return {
                            "next_question": "Please continue...",
                            "partial_spec": obj,
                            "done": False
                        }
            except json.JSONDecodeError as e:
                logger.debug(f"JSON candidate parsing failed: {e}")
                continue
        
        # Strategy 4: Try to extract partial_spec from text even if outer structure is missing
        # Look for entities, app_type, db_type patterns
        partial_spec = self._extract_partial_spec_from_text(text)
        if partial_spec:
            logger.info("Extracted partial_spec from text, wrapping in response structure")
            return {
                "next_question": self._extract_question_from_text(text) or "Please continue...",
                "partial_spec": partial_spec,
                "done": self._detect_completion_from_text(text)
            }
        
        # Strategy 5: Final fallback - wrap the entire text as next_question
        # This ensures we never fail completely, but log a warning
        logger.warning(
            f"AI returned plain text instead of JSON. Text preview: {text[:300]}... "
            f"Wrapping text in JSON structure."
        )
        return {
            "next_question": text.strip(),
            "partial_spec": {},
            "done": False
        }
    
    def _ensure_required_fields(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure the response dict has all required fields with defaults."""
        result = dict(obj)  # Make a copy
        if "next_question" not in result:
            result["next_question"] = ""
        if "done" not in result:
            result["done"] = False
        if "partial_spec" not in result:
            result["partial_spec"] = {}
        return result
    
    def _find_all_json_objects(self, text: str) -> List[str]:
        """
        Find all potential JSON objects in text by balancing braces.
        Returns candidates sorted by size (largest first).
        """
        candidates = []
        start = 0
        
        while True:
            # Find next opening brace
            start = text.find('{', start)
            if start == -1:
                break
            
            # Extract balanced JSON from this position
            balanced_json = self._extract_json_with_balance(text[start:])
            if balanced_json:
                candidates.append(balanced_json)
                # Move past this JSON object
                start += len(balanced_json)
            else:
                start += 1
        
        # Sort by length (descending) to try largest objects first
        candidates.sort(key=len, reverse=True)
        return candidates
    
    def _fix_common_json_issues(self, json_text: str) -> str:
        """
        Fix common JSON issues that might prevent parsing:
        - Unescaped newlines in strings
        - Unescaped quotes in strings
        - Trailing commas
        - Comments (though JSON doesn't support them)
        """
        import re
        
        # Fix unescaped newlines, carriage returns, and tabs in string values
        fixed = self._fix_unescaped_newlines(json_text)
        
        # Remove trailing commas before } or ]
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        
        # Try to fix common quote issues in string values
        # This is tricky - we need to be careful not to break valid JSON
        # For now, we'll be conservative and only fix obvious issues
        
        return fixed
    
    def _extract_partial_spec_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Try to extract a partial_spec structure from text even if it's not in proper JSON format.
        Looks for patterns like "entities", "app_type", "db_type" etc.
        """
        import re
        
        # Look for JSON-like structures that might contain entities or app_type
        # Try to find the largest JSON object that contains these keywords
        entities_pos = text.rfind('"entities"')
        app_type_pos = text.rfind('"app_type"')
        db_type_pos = text.rfind('"db_type"')
        
        if entities_pos == -1 and app_type_pos == -1 and db_type_pos == -1:
            return None
        
        # Find the start of a JSON object near these keywords
        search_positions = [pos for pos in [entities_pos, app_type_pos, db_type_pos] if pos != -1]
        if not search_positions:
            return None
        
        # Start from the earliest position and work backwards to find opening brace
        start_pos = min(search_positions)
        while start_pos > 0 and text[start_pos] != '{':
            start_pos -= 1
        
        if start_pos == -1 or text[start_pos] != '{':
            return None
        
        # Extract balanced JSON from this position
        balanced_json = self._extract_json_with_balance(text[start_pos:])
        if balanced_json:
            try:
                fixed_json = self._fix_common_json_issues(balanced_json)
                obj = json.loads(fixed_json)
                if isinstance(obj, dict) and ("entities" in obj or "app_type" in obj or "db_type" in obj):
                    logger.info("Extracted partial_spec from text")
                    return obj
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _extract_question_from_text(self, text: str) -> Optional[str]:
        """
        Try to extract a question from text that might be before or after JSON.
        Looks for patterns like "What...", "Please...", etc.
        """
        import re
        
        # Remove any JSON-like structures first
        text_without_json = re.sub(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', text)
        
        # Look for question-like patterns
        question_patterns = [
            r'(?:What|How|Which|When|Where|Why|Can|Could|Would|Should|Do|Does|Is|Are)\s+[^.!?]*[?]',
            r'Please\s+[^.!?]*[?]',
            r'[^.!?]*\?',
        ]
        
        for pattern in question_patterns:
            match = re.search(pattern, text_without_json, re.IGNORECASE)
            if match:
                question = match.group(0).strip()
                if len(question) > 10:  # Filter out very short matches
                    return question
        
        return None
    
    def _detect_completion_from_text(self, text: str) -> bool:
        """
        Detect if the text indicates the conversation is complete.
        Looks for completion phrases.
        """
        completion_phrases = [
            "done",
            "complete",
            "finished",
            "ready to",
            "have enough information",
            "can create",
            "will generate",
        ]
        
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in completion_phrases)
    
    def _fix_embedded_json_in_strings(self, json_text: str) -> str:
        """Fix embedded JSON objects/arrays in JSON string values by escaping quotes and braces."""
        import re
        
        # Strategy: Find string values and escape any unescaped quotes, braces, and newlines inside them
        result = []
        i = 0
        in_string = False
        escape_next = False
        
        while i < len(json_text):
            char = json_text[i]
            
            if escape_next:
                result.append(char)
                escape_next = False
                i += 1
                continue
            
            if char == '\\':
                result.append(char)
                escape_next = True
                i += 1
                continue
            
            if char == '"' and not escape_next:
                # Check if this is the start/end of a string value (not a key)
                # Look backwards to see if we're after a : (value) or , (key)
                if in_string:
                    # Ending a string - check if next char is , or } or ]
                    in_string = False
                    result.append(char)
                else:
                    # Starting a string - check if previous context suggests it's a value
                    # Simple heuristic: if we see : before this quote, it's likely a value
                    in_string = True
                    result.append(char)
                i += 1
                continue
            
            if in_string:
                # Inside a string value - escape problematic characters
                if char == '\n':
                    result.append('\\n')
                elif char == '\r':
                    result.append('\\r')
                elif char == '\t':
                    result.append('\\t')
                elif char == '"':
                    # Unescaped quote inside string - escape it
                    result.append('\\"')
                elif char == '\\':
                    # Already handled above, but just in case
                    result.append(char)
                    escape_next = True
                else:
                    result.append(char)
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    def _fix_unescaped_newlines(self, json_text: str) -> str:
        """Fix unescaped newlines in JSON string values."""
        import re
        # Pattern to match string values: "key": "value with possible \n"
        # We need to escape actual newline characters within string values
        def escape_newlines_in_string(match):
            key_part = match.group(1)  # "key":
            value = match.group(2)  # the string value
            # Escape newlines and other problematic control characters
            escaped_value = value.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            return f'{key_part} "{escaped_value}"'
        
        # Match: "key": "multiline\nvalue"
        # This is complex because we need to handle escaped quotes
        result = []
        in_string = False
        escape_next = False
        i = 0
        while i < len(json_text):
            char = json_text[i]
            
            if escape_next:
                result.append(char)
                escape_next = False
            elif char == '\\':
                result.append(char)
                escape_next = True
            elif char == '"' and not escape_next:
                in_string = not in_string
                result.append(char)
            elif in_string and char == '\n':
                result.append('\\n')
            elif in_string and char == '\r':
                result.append('\\r')
            elif in_string and char == '\t':
                result.append('\\t')
            else:
                result.append(char)
            i += 1
        
        return ''.join(result)
    
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

    def _extract_spec_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract spec JSON from text even if outer JSON is malformed."""
        import re
        
        # Try to find a spec-like JSON structure (has "entities" or "app_type")
        # Look for the largest JSON object that contains "entities" or "app_type"
        # Start from the end and work backwards to find the complete spec
        entities_pos = text.rfind('"entities"')
        app_type_pos = text.rfind('"app_type"')
        
        if entities_pos == -1 and app_type_pos == -1:
            return None
        
        # Find the start of the JSON object containing entities/app_type
        start_pos = max(entities_pos, app_type_pos)
        # Go backwards to find the opening brace
        while start_pos > 0 and text[start_pos] != '{':
            start_pos -= 1
        
        if start_pos == -1:
            return None
        
        # Extract balanced JSON from this position
        balanced_json = self._extract_json_with_balance(text[start_pos:])
        if balanced_json:
            try:
                obj = json.loads(balanced_json)
                if isinstance(obj, dict) and ("entities" in obj or "app_type" in obj):
                    logger.info("Extracted spec from malformed JSON response")
                    return obj
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _parse_suggestions_json(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON for schema suggestions with robust extraction.
        Similar to _parse_json_response but expects a different structure.
        """
        if not text or not text.strip():
            raise ValueError("Empty response from AI")
        
        import re
        
        text = text.strip()
        
        # Strategy 1: Try direct JSON parsing
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and ("option_1" in obj or "option_2" in obj):
                return obj
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL | re.IGNORECASE)
        if json_match:
            try:
                json_content = json_match.group(1).strip()
                obj = json.loads(json_content)
                if isinstance(obj, dict) and ("option_1" in obj or "option_2" in obj):
                    return obj
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Extract JSON by finding first { and balancing braces
        balanced_json = self._extract_json_with_balance(text)
        if balanced_json:
            try:
                fixed_json = self._fix_common_json_issues(balanced_json)
                obj = json.loads(fixed_json)
                if isinstance(obj, dict) and ("option_1" in obj or "option_2" in obj):
                    return obj
            except json.JSONDecodeError:
                pass
        
        # If all parsing fails, raise an error (unlike _parse_json_response which has fallback)
        raise ValueError(f"AI service returned invalid JSON. Response: {text[:500]}...")
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from text, handling markdown code blocks. DEPRECATED: Use _parse_json_response or _parse_suggestions_json instead."""
        if not text:
            return ""
        
        # Try to find JSON in markdown code block
        json_match = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
        
        # Try direct JSON
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return text

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
        
        # No confirmation step needed - AI can go straight to done=true when it has enough info
        
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

    def generate_schema_suggestions(self, postgres_sql: str, schema: Dict[str, Any], rejected_suggestions: list = None, previously_suggested: list = None) -> Dict[str, Any]:
        """Generate two AI suggestions for improving the database schema."""
        if rejected_suggestions is None:
            rejected_suggestions = []
        if previously_suggested is None:
            previously_suggested = []
        
        # Combine rejected and previously suggested for clarity
        all_excluded = list(set(rejected_suggestions + previously_suggested))
        
        excluded_text = ""
        if rejected_suggestions:
            rejected_list = ", ".join(rejected_suggestions)
            excluded_text += f"\n\nCRITICAL: The following tables were EXPLICITLY REJECTED by the user - DO NOT suggest them:\n{rejected_list}"
        
        if previously_suggested:
            prev_list = ", ".join(previously_suggested)
            excluded_text += f"\n\nUNIQUENESS REQUIREMENT: The following tables have already been suggested to the user. Please suggest DIFFERENT tables:\n{prev_list}\n\nIf you need ideas, consider: audit trails, analytics/reporting tables, intermediate junction tables, normalization opportunities, or edge case tables."
        
        prompt = f"""You are analyzing a database schema and providing improvement suggestions.

CURRENT DATABASE SCHEMA:
{postgres_sql}{excluded_text}

TASK: Provide TWO COMPLETELY NEW AND UNIQUE suggestions for how this database could be improved.

OPTION 1 - ADD A NEW TABLE:
Analyze the current schema and identify what new table would add the most value. Consider:
- What entity is missing that would improve the database design?
- What relationships would benefit from explicit table creation?
- What would make the data model more complete or normalized?

Provide your response in this EXACT JSON format:
{{
  "option_1": {{
    "reasoning": "Brief explanation of why this table would improve the database",
    "new_table": {{
      "name": "table_name",
      "fields": [
        {{"name": "id", "type": "uuid", "required": true, "primary_key": true}},
        {{"name": "field_name", "type": "field_type", "required": true}},
        {{"name": "reference_id", "type": "uuid", "required": true, "foreign_key": {{"table": "existing_table", "field": "id"}}}}
      ]
    }},
    "connections": [
      {{"from": "new_table_name", "to": "existing_table_name"}}
    ]
  }},
  "option_2": {{
    "reasoning": "Brief explanation of why merging these tables would improve the database",
    "tables_to_merge": ["table1", "table2"],
    "merged_table": {{
      "name": "merged_table_name",
      "fields": [
        {{"name": "id", "type": "uuid", "required": true, "primary_key": true}},
        {{"name": "field_from_table1", "type": "type", "required": true}},
        {{"name": "field_from_table2", "type": "type", "required": true}}
      ]
    }},
    "connections": [
      {{"from": "merged_table_name", "to": "other_table_name"}}
    ]
  }}
}}

CRITICAL: Respond with ONLY valid JSON. No other text before or after."""
        
        try:
            message = self._client.messages.create(
                model=self._model_name,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text if message.content else ""
            
            # Use robust JSON parsing (similar to _parse_json_response but for suggestions format)
            suggestions = self._parse_suggestions_json(response_text)
            
            # Ensure we have both options
            if not isinstance(suggestions, dict) or "option_1" not in suggestions or "option_2" not in suggestions:
                logger.warning("AI did not return both option_1 and option_2 in suggestions")
                raise ValueError("AI did not return both option_1 and option_2")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            # Return fallback suggestions
            return {
                "option_1": {
                    "reasoning": "Could not generate AI suggestion. Please try again.",
                    "new_table": None,
                    "connections": []
                },
                "option_2": {
                    "reasoning": "Could not generate AI suggestion. Please try again.",
                    "tables_to_merge": [],
                    "merged_table": None,
                    "connections": []
                }
            }


# Lazy initialize the agent to avoid crashing app startup if SDK/env isn't ready
agent_service: AIAgentService | None = None

def get_agent() -> AIAgentService:
    global agent_service
    if agent_service is None:
        agent_service = AIAgentService()
    return agent_service