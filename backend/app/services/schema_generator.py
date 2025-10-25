from typing import Dict, Any, List, Tuple
from loguru import logger

BASIC_TYPE_MAP_PG = {
    "string": "TEXT",
    "text": "TEXT",
    "varchar": "VARCHAR",
    "int": "INTEGER",
    "integer": "INTEGER",
    "bigint": "BIGINT",
    "smallint": "SMALLINT",
    "float": "DOUBLE PRECISION",
    "double": "DOUBLE PRECISION",
    "number": "DOUBLE PRECISION",
    "decimal": "DECIMAL",
    "numeric": "NUMERIC",
    "bool": "BOOLEAN",
    "boolean": "BOOLEAN",
    "date": "DATE",
    "datetime": "TIMESTAMP",
    "timestamp": "TIMESTAMP",
    "time": "TIME",
    "json": "JSONB",
    "jsonb": "JSONB",
    "uuid": "UUID",
    "inet": "INET",
    "cidr": "CIDR",
    "macaddr": "MACADDR",
    "point": "POINT",
    "polygon": "POLYGON",
    "bytea": "BYTEA",
    "array": "TEXT[]",
    "enum": "TEXT",
}


def _normalize_type(t: str) -> str:
    t = (t or "").lower().strip()
    return t if t in BASIC_TYPE_MAP_PG else "string"


def validate_spec(spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if not isinstance(spec, dict):
        return False, ["spec must be a dict"]
    entities = spec.get("entities") or []
    if not isinstance(entities, list) or not entities:
        errors.append("spec.entities must be a non-empty list")
    for ent in entities:
        name = ent.get("name") if isinstance(ent, dict) else None
        if not name:
            errors.append("entity.name is required")
            continue
        fields = ent.get("fields") or []
        if not isinstance(fields, list) or not fields:
            errors.append(f"{name}: fields must be a non-empty list")
            continue
        for f in fields:
            if not f.get("name"):
                errors.append(f"{name}: field.name is required")
            if not f.get("type"):
                errors.append(f"{name}.{f.get('name','?')}: field.type is required")
    return len(errors) == 0, errors


def to_json_schema(spec: Dict[str, Any]) -> Dict[str, Any]:
    entities = spec.get("entities", [])
    definitions = {}
    for ent in entities:
        props = {}
        required = []
        for f in ent.get("fields", []):
            ftype = _normalize_type(f.get("type"))
            json_type = {
                "string": "string",
                "int": "integer",
                "integer": "integer",
                "float": "number",
                "number": "number",
                "bool": "boolean",
                "boolean": "boolean",
                "date": "string",
                "datetime": "string",
                "json": "object",
                "uuid": "string",
            }.get(ftype, "string")
            props[f["name"]] = {"type": json_type}
            if f.get("required"):
                required.append(f["name"])
        definitions[ent["name"]] = {
            "type": "object",
            "properties": props,
            "required": required,
        }
    return {"$schema": "http://json-schema.org/draft-07/schema#", "definitions": definitions}


def to_mongo_scripts(spec: Dict[str, Any]) -> List[str]:
    scripts: List[str] = []
    dbname = spec.get("name", "shipdb")
    scripts.append(f"use {dbname}")
    for ent in spec.get("entities", []):
        cname = ent["name"]
        scripts.append(f"db.createCollection('{cname}')")
        
        # Create indexes for primary key fields
        pk_fields = [f for f in ent.get("fields", []) if f.get("primary_key")]
        if pk_fields:
            pk_index = {f["name"]: 1 for f in pk_fields}
            scripts.append(f"db.{cname}.createIndex({pk_index}, {{unique: true}})")
        
        # Create indexes for unique fields
        unique_fields = [f for f in ent.get("fields", []) if f.get("unique")]
        for field in unique_fields:
            if not field.get("primary_key"):  # Don't duplicate primary key indexes
                unique_index = {field["name"]: 1}
                scripts.append(f"db.{cname}.createIndex({unique_index}, {{unique: true}})")
        
        # Create indexes for foreign key fields (for better query performance)
        fk_fields = [f for f in ent.get("fields", []) if f.get("foreign_key")]
        for field in fk_fields:
            fk_index = {field["name"]: 1}
            scripts.append(f"db.{cname}.createIndex({fk_index})")
        
        # Create indexes from explicit indexes array (if any)
        for idx in ent.get("indexes", []) or []:
            fields = idx.get("fields") or []
            if not fields:
                continue
            key_obj = {f.get("field"): (1 if f.get("order", "asc") == "asc" else -1) for f in fields}
            unique = "true" if idx.get("unique") else "false"
            scripts.append(
                f"db.{cname}.createIndex({key_obj}, {{unique: {unique}}})".replace("'", '"')
            )
    return scripts


def to_postgres_sql(spec: Dict[str, Any]) -> str:
    stmts: List[str] = []
    
    # Create custom types/enums first
    for ent in spec.get("entities", []):
        for f in ent.get("fields", []):
            if f.get("type") == "enum" and f.get("values"):
                enum_name = f"{ent['name']}_{f['name']}_enum"
                values = ", ".join([f"'{v}'" for v in f["values"]])
                stmts.append(f"CREATE TYPE IF NOT EXISTS {enum_name} AS ENUM ({values});")
    
    # Create tables
    for ent in spec.get("entities", []):
        cols: List[str] = []
        pks: List[str] = []
        uniques: List[str] = []
        fks: List[str] = []
        checks: List[str] = []
        
        for f in ent.get("fields", []):
            col = f['name']
            field_type = _normalize_type(f.get('type'))
            
            # Handle enum types
            if field_type == "enum" and f.get("values"):
                pg_type = f"{ent['name']}_{f['name']}_enum"
            else:
                pg_type = BASIC_TYPE_MAP_PG.get(field_type, 'TEXT')
            
            # Handle precision and scale for decimal/numeric
            if field_type in ["decimal", "numeric"] and f.get("precision"):
                scale = f.get("scale", 0)
                pg_type = f"{pg_type}({f['precision']},{scale})"
            elif field_type == "varchar" and f.get("length"):
                pg_type = f"VARCHAR({f['length']})"
            
            nullable = "NOT NULL" if f.get("required") else ""
            default = f.get("default")
            
            # Handle default values properly
            if default is not None:
                if isinstance(default, str) and field_type not in ["enum"]:
                    default_sql = f" DEFAULT '{default}'"
                else:
                    default_sql = f" DEFAULT {default}"
            else:
                default_sql = ""
            
            # Handle auto-increment
            if f.get("auto_increment"):
                if field_type in ["int", "integer"]:
                    pg_type = "SERIAL"
                elif field_type == "bigint":
                    pg_type = "BIGSERIAL"
                nullable = "NOT NULL"
                default_sql = ""
            
            col_def = f"\"{col}\" {pg_type} {nullable}{default_sql}".strip()
            cols.append(col_def)
            
            # Collect primary keys
            if f.get("primary_key"):
                pks.append(f'"{col}"')
            
            # Collect unique constraints
            if f.get("unique") and not f.get("primary_key"):
                uniques.append(f"UNIQUE (\"{col}\")")
            
            # Collect foreign keys
            if f.get("foreign_key"):
                fk_info = f["foreign_key"]
                ref_table = fk_info.get("table")
                ref_field = fk_info.get("field")
                if ref_table and ref_field:
                    fks.append(f"FOREIGN KEY (\"{col}\") REFERENCES \"{ref_table}\"(\"{ref_field}\")")
            
            # Collect check constraints
            if f.get("min_value") is not None:
                checks.append(f"CHECK (\"{col}\" >= {f['min_value']})")
            if f.get("max_value") is not None:
                checks.append(f"CHECK (\"{col}\" <= {f['max_value']})")
            if f.get("min_length") is not None:
                checks.append(f"CHECK (LENGTH(\"{col}\") >= {f['min_length']})")
            if f.get("max_length") is not None:
                checks.append(f"CHECK (LENGTH(\"{col}\") <= {f['max_length']})")
        
        # Handle composite primary keys
        if not pks:
            # Look for primary_key at entity level
            pk_fields = ent.get("primary_key", [])
            if isinstance(pk_fields, list):
                pks = [f'"{c}"' for c in pk_fields]
        
        # Handle composite unique constraints
        for uq in ent.get("unique", []) or []:
            if isinstance(uq, list) and uq:
                uniques.append(f"UNIQUE ({', '.join([f'\"{c}\"' for c in uq])})")
        
        # Handle foreign keys at entity level
        for fk in ent.get("foreign_keys", []) or []:
            cols_local = fk.get("columns") or []
            ref_table = fk.get("ref_table")
            ref_cols = fk.get("ref_columns") or []
            if cols_local and ref_table and ref_cols:
                fks.append(
                    "FOREIGN KEY (" + ", ".join([f'\"{c}\"' for c in cols_local]) + ") REFERENCES "
                    + f'"{ref_table}"(' + ", ".join([f'\"{c}\"' for c in ref_cols]) + ")"
                )
        
        table = ent["name"]
        body = [*cols]
        
        if pks:
            body.append(f"PRIMARY KEY ({', '.join(pks)})")
        body.extend(uniques)
        body.extend(fks)
        body.extend(checks)
        
        stmts.append(f"CREATE TABLE IF NOT EXISTS \"{table}\" (\n  " + ",\n  ".join(body) + "\n);")
        
        # Create indexes
        for i, idx in enumerate(ent.get("indexes", []) or []):
            fields = idx.get("fields") or []
            if not fields:
                continue
            
            idx_name = idx.get("name") or f"{table}_idx_{i}"
            cols_idx = ", ".join([f'"{f.get("field")}" {("DESC" if f.get("order")=="desc" else "ASC")}' for f in fields])
            unique_kw = "UNIQUE " if idx.get("unique") else ""
            index_type = idx.get("type", "btree")
            
            if index_type == "gin":
                stmts.append(f"CREATE {unique_kw}INDEX IF NOT EXISTS \"{idx_name}\" ON \"{table}\" USING GIN ({cols_idx});")
            elif index_type == "gist":
                stmts.append(f"CREATE {unique_kw}INDEX IF NOT EXISTS \"{idx_name}\" ON \"{table}\" USING GIST ({cols_idx});")
            elif index_type == "hash":
                stmts.append(f"CREATE {unique_kw}INDEX IF NOT EXISTS \"{idx_name}\" ON \"{table}\" USING HASH ({cols_idx});")
            else:
                stmts.append(f"CREATE {unique_kw}INDEX IF NOT EXISTS \"{idx_name}\" ON \"{table}\" ({cols_idx});")
    
    # Add triggers for audit trails if specified
    if spec.get("audit_trail"):
        for ent in spec.get("entities", []):
            table = ent["name"]
            stmts.append(f"""
-- Audit trigger for {table}
CREATE OR REPLACE FUNCTION audit_{table}_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_values, created_at)
        VALUES ('{table}', OLD.id, 'delete', row_to_json(OLD), NOW());
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, created_at)
        VALUES ('{table}', NEW.id, 'update', row_to_json(OLD), row_to_json(NEW), NOW());
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, record_id, action, new_values, created_at)
        VALUES ('{table}', NEW.id, 'insert', row_to_json(NEW), NOW());
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER {table}_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON "{table}"
    FOR EACH ROW EXECUTE FUNCTION audit_{table}_changes();
""")
    
    return "\n".join(stmts)


def to_dynamodb_defs(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    tables: List[Dict[str, Any]] = []
    for ent in spec.get("entities", []):
        # Find primary key fields from the fields array
        pk_fields = [f for f in ent.get("fields", []) if f.get("primary_key")]
        if not pk_fields:
            logger.warning("DynamoDB: entity %s missing primary_key fields; skipping", ent.get("name"))
            continue
        
        key_schema = []
        attr_defs = []
        attr_set = set()
        
        # Use the first primary key field as HASH key
        if len(pk_fields) >= 1:
            pk_name = pk_fields[0]["name"]
            key_schema.append({"AttributeName": pk_name, "KeyType": "HASH"})
            attr_set.add(pk_name)
        
        # Use second primary key field as RANGE key (if exists)
        if len(pk_fields) >= 2:
            pk_name = pk_fields[1]["name"]
            key_schema.append({"AttributeName": pk_name, "KeyType": "RANGE"})
            attr_set.add(pk_name)
        for f in ent.get("fields", []):
            if f["name"] in attr_set:
                t = _normalize_type(f.get("type"))
                dynamo_t = "S" if t in ["string", "date", "datetime", "uuid"] else ("N" if t in ["int", "integer", "float", "number"] else "S")
                attr_defs.append({"AttributeName": f["name"], "AttributeType": dynamo_t})
        provisioned = {
            "ReadCapacityUnits": (ent.get("read_capacity") or spec.get("aws", {}).get("read_capacity") or 5),
            "WriteCapacityUnits": (ent.get("write_capacity") or spec.get("aws", {}).get("write_capacity") or 5),
        }
        table_def = {
            "TableName": ent["name"],
            "KeySchema": key_schema,
            "AttributeDefinitions": attr_defs,
            "BillingMode": "PROVISIONED",
            "ProvisionedThroughput": provisioned,
        }
        # GSIs (optional)
        gsis = []
        for idx in ent.get("indexes", []) or []:
            fields = idx.get("fields") or []
            if not fields:
                continue
            # Simple single-attr GSI from first field
            gname = idx.get("name") or f"{ent['name']}_gsi_{len(gsis)}"
            attr = fields[0].get("field")
            if not attr:
                continue
            if attr not in [a["AttributeName"] for a in attr_defs]:
                # Add attribute def if missing
                t = "S"
                for f in ent.get("fields", []):
                    if f["name"] == attr:
                        tnorm = _normalize_type(f.get("type"))
                        t = "S" if tnorm in ["string", "date", "datetime", "uuid"] else ("N" if tnorm in ["int", "integer", "float", "number"] else "S")
                        break
                attr_defs.append({"AttributeName": attr, "AttributeType": t})
            gsis.append({
                "IndexName": gname,
                "KeySchema": [{"AttributeName": attr, "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": provisioned,
            })
        if gsis:
            table_def["GlobalSecondaryIndexes"] = gsis
        tables.append(table_def)
    return tables


def generate_all(spec: Dict[str, Any]) -> Dict[str, Any]:
    ok, errors = validate_spec(spec)
    if not ok:
        raise ValueError("Invalid spec: " + "; ".join(errors))
    
    result = {
        "json_schema": to_json_schema(spec),
        "mongo_scripts": to_mongo_scripts(spec),
        "postgres_sql": to_postgres_sql(spec),
        "dynamodb_tables": to_dynamodb_defs(spec),
    }
    
    # Add enterprise features if present
    if "hybrid_architecture" in spec:
        result["hybrid_architecture"] = spec["hybrid_architecture"]
    
    if "caching_strategy" in spec:
        result["caching_strategy"] = spec["caching_strategy"]
    
    if "search_strategy" in spec:
        result["search_strategy"] = spec["search_strategy"]
    
    if "monitoring" in spec:
        result["monitoring"] = spec["monitoring"]
    
    if "backup_strategy" in spec:
        result["backup_strategy"] = spec["backup_strategy"]
    
    if "scaling_strategy" in spec:
        result["scaling_strategy"] = spec["scaling_strategy"]
    
    if "security" in spec:
        result["security"] = spec["security"]
    
    return result
