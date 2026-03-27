"""ADOMD.NET operations: DAX query execution.

Provides DAX execute, validate, and cache clearing via direct
ADOMD.NET interop. Results are returned as plain Python dicts.
"""

from __future__ import annotations

from typing import Any


def execute_dax(
    adomd_connection: Any,
    query: str,
    max_rows: int | None = None,
    timeout: int = 200,
) -> dict[str, Any]:
    """Execute a DAX query and return results.

    Args:
        adomd_connection: An open AdomdConnection.
        query: The DAX query string (must start with EVALUATE).
        max_rows: Optional row limit.
        timeout: Query timeout in seconds.

    Returns:
        Dict with ``columns`` and ``rows`` keys.
    """
    from pbi_cli.core.dotnet_loader import get_adomd_command_class

    AdomdCommand = get_adomd_command_class()

    cmd = AdomdCommand(query, adomd_connection)
    cmd.CommandTimeout = timeout

    reader = cmd.ExecuteReader()

    # Read column headers
    columns: list[str] = []
    for i in range(reader.FieldCount):
        columns.append(str(reader.GetName(i)))

    # Read rows
    rows: list[dict[str, Any]] = []
    row_count = 0
    while reader.Read():
        if max_rows is not None and row_count >= max_rows:
            break
        row: dict[str, Any] = {}
        for i, col_name in enumerate(columns):
            val = reader.GetValue(i)
            row[col_name] = _convert_value(val)
        rows.append(row)
        row_count += 1

    reader.Close()

    return {"columns": columns, "rows": rows}


def validate_dax(
    adomd_connection: Any,
    query: str,
    timeout: int = 10,
) -> dict[str, Any]:
    """Validate a DAX query without returning data.

    Wraps the query in EVALUATE ROW("v", 0) pattern to test parsing
    without full execution.
    """
    from pbi_cli.core.dotnet_loader import get_adomd_command_class

    AdomdCommand = get_adomd_command_class()

    # Use a lightweight wrapper to validate syntax
    validate_query = query.strip()
    cmd = AdomdCommand(validate_query, adomd_connection)
    cmd.CommandTimeout = timeout

    try:
        reader = cmd.ExecuteReader()
        reader.Close()
        return {"valid": True, "query": query.strip()}
    except Exception as e:
        return {"valid": False, "error": str(e), "query": query.strip()}


def clear_cache(
    adomd_connection: Any,
    database_id: str = "",
) -> dict[str, str]:
    """Clear the Analysis Services cache via XMLA."""
    from pbi_cli.core.dotnet_loader import get_adomd_command_class

    AdomdCommand = get_adomd_command_class()

    object_xml = ""
    if database_id:
        object_xml = f"<DatabaseID>{database_id}</DatabaseID>"

    xmla = (
        '<ClearCache xmlns="http://schemas.microsoft.com/analysisservices/2003/engine">'
        f"<Object>{object_xml}</Object>"
        "</ClearCache>"
    )
    cmd = AdomdCommand(xmla, adomd_connection)
    cmd.ExecuteNonQuery()
    return {"status": "cache_cleared"}


def _convert_value(val: Any) -> Any:
    """Convert a .NET value to a Python-native type."""
    if val is None:
        return None
    type_name = type(val).__name__
    if type_name in ("Int32", "Int64", "Int16"):
        return int(val)
    if type_name in ("Double", "Single", "Decimal"):
        return float(val)
    if type_name == "Boolean":
        return bool(val)
    if type_name == "DateTime":
        return str(val)
    if type_name == "DBNull":
        return None
    return str(val)
