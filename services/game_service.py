import os
import re
from typing import Any, Dict, List, Tuple
from mysql.connector import Error as MySQLError
from db_game import get_config

ONLY_READ = str(os.getenv("ONLY_READ_QUERIES", "true")).lower() in {"1","true","yes","on"}

WRITE_PATTERNS = re.compile(
    r"^\s*(INSERT|UPDATE|DELETE|REPLACE|DROP|TRUNCATE|ALTER|CREATE|GRANT|REVOKE|RENAME|CALL|MERGE|LOCK|UNLOCK)\b",
    re.IGNORECASE
)

def _statement_type(sql: str) -> str:
    first = re.findall(r"^\s*([a-zA-Z]+)", sql or "")
    return (first[0].upper() if first else "UNKNOWN")

def execute_sql(sql: str) -> Tuple[int, Dict[str, Any]]:


    if not sql or not sql.strip():
        return 400, {"ok": False, "error": "Query vacía"}

    stmt_type = _statement_type(sql)


    if ONLY_READ and WRITE_PATTERNS.match(sql):
        return 403, {
            "ok": False,
            "error": "Solo se permiten consultas SELECT en este entorno",
            "statement_type": stmt_type
        }

    try:
        conn = get_config()
        cur = conn.cursor(dictionary=True)
        cur.execute(sql)

        if cur.with_rows:
            rows: List[Dict[str, Any]] = cur.fetchall()
            columns = [d[0] for d in (cur.column_names or [])] if hasattr(cur, "column_names") else list(rows[0].keys()) if rows else []
            conn.commit()
            cur.close()
            conn.close()
            return 200, {
                "ok": True,
                "statement_type": stmt_type,
                "count": len(rows),
                "columns": columns,
                "rows": rows
            }
        else:
            affected = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            return 200, {
                "ok": True,
                "statement_type": stmt_type,
                "affected_rows": affected
            }

    except MySQLError as e:
        return 400, {"ok": False, "error": str(e), "statement_type": stmt_type}
    except Exception as e:
        return 500, {"ok": False, "error": f"Unexpected error: {e}", "statement_type": stmt_type}
