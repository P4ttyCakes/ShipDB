from typing import Dict, Any, List, Tuple
from loguru import logger

BASIC_TYPE_MAP_PG = {
    "string": "TEXT",
    "int": "INTEGER",
    "integer": "INTEGER",
    "float": "DOUBLE PRECISION",
    "number": "DOUBLE PRECISION",
    "bool": "BOOLEAN",
    "boolean": "BOOLEAN",
    "date": "DATE",
    "datetime": "TIMESTAMP",
    "json": "JSONB",
    "uuid": "UUID",
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
    for ent in spec.get("entities", []):
        cols: List[str] = []
        pks: List[str] = []
        uniques: List[str] = []
        fks: List[str] = []
        for f in ent.get("fields", []):
            col = f['name']
            pg_type = BASIC_TYPE_MAP_PG.get(_normalize_type(f.get('type')), 'TEXT')
            nullable = "NOT NULL" if f.get("required") else ""
            default = f.get("default")
            default_sql = f" DEFAULT {default}" if default is not None else ""
            cols.append(f"\"{col}\" {pg_type} {nullable}{default_sql}".strip())
        # Constraints
        pk = ent.get("primary_key") or []
        if isinstance(pk, list) and pk:
            pks = [f'"{c}"' for c in pk]
        for uq in ent.get("unique", []) or []:
            if isinstance(uq, list) and uq:
                uniques.append(f"UNIQUE ({', '.join([f'\"{c}\"' for c in uq])})")
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
        stmts.append(f"CREATE TABLE IF NOT EXISTS \"{table}\" (\n  " + ",\n  ".join(body) + "\n);")
        # Indexes
        for i, idx in enumerate(ent.get("indexes", []) or []):
            fields = idx.get("fields") or []
            if not fields:
                continue
            cols_idx = ", ".join([f'"{f.get("field")}" {("DESC" if f.get("order")=="desc" else "ASC")}' for f in fields])
            unique_kw = "UNIQUE " if idx.get("unique") else ""
            stmts.append(f"CREATE {unique_kw}INDEX IF NOT EXISTS \"{table}_idx_{i}\" ON \"{table}\" ({cols_idx});")
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
    return {
        "json_schema": to_json_schema(spec),
        "mongo_scripts": to_mongo_scripts(spec),
        "postgres_sql": to_postgres_sql(spec),
        "dynamodb_tables": to_dynamodb_defs(spec),
    }
