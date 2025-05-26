import json
from typing import Dict, List, Optional, Union

from rich import box
from rich.console import Console
from rich.table import Table

console = Console()


def __table(
    data: Union[Dict, List],
    columns: List[str] = None,
    title: Optional[str] = None,
):
    """
    Print a table from a JSON response using rich.

    Parameters:
        data (dict or list): The JSON data.
        path (list): Path to the list of items you want to tabulate.
        columns (list): The keys from each item to show as columns.
        title(str)
    """

    if isinstance(data, list):
        if not columns:
            columns = list(data[0].keys())
        rows = data
    elif isinstance(data, dict):
        if not columns:
            columns = list(data.keys())
        rows = [data]
    else:
        return

    table = Table(title=title, box=box.SIMPLE)

    for col in columns:
        table.add_column(col, style="cyan", no_wrap=True)

    for item in rows:
        row = [str(item.get(col, "")) for col in columns]
        table.add_row(*row)

    console.print(table)


def __json(data):
    console.print_json(json.dumps(data))


def raw(data):
    console.print(data)


def print(
    args,
    data: Union[Dict, List],
    columns: List[str] = None,
    title: Optional[str] = None,
):
    if args.json:
        __json(data)
    else:
        __table(data=data, columns=columns, title=title)
