from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

def print_header(kennel):
    console.print(Panel.fit(
        f"[bold yellow]DOGKEEPER[/] · [bold magenta]{kennel.name}[/]\n[dim]Manage your kennel, feed your dogs.[/]",
        border_style="blue",
        box=box.DOUBLE,
    ))
