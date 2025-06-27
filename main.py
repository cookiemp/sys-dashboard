# main.py
import typer
import platform
import psutil
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

# Helper function
def bytes_to_readable(b):
    """Converts bytes to a human-readable format (GB or MB)."""
    gb = b / (1024**3)
    if gb >= 1:
        return f"{gb:.2f} GB"
    mb = b / (1024**2)
    return f"{mb:.2f} MB"

def generate_stats_table() -> Table:
    """Generates the table with all system stats."""
    # --- Static System Info ---
    os_name = platform.system()
    os_ver = platform.release()
    arch = platform.machine()
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)

    # --- Live Stats ---
    cpu_usage = psutil.cpu_percent(interval=None) # Set interval to None for non-blocking
    memory = psutil.virtual_memory()
    mem_total = bytes_to_readable(memory.total)
    mem_used = bytes_to_readable(memory.used)
    mem_percent = memory.percent
    
    disk = psutil.disk_usage('/')
    disk_total = bytes_to_readable(disk.total)
    disk_used = bytes_to_readable(disk.used)
    disk_percent = disk.percent
    
    net = psutil.net_io_counters()
    net_sent = bytes_to_readable(net.bytes_sent)
    net_recv = bytes_to_readable(net.bytes_recv)

    # --- Create Rich Table ---
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    # Add rows to the table
    table.add_row("OS", f"{os_name} {os_ver}")
    table.add_row("Architecture", arch)
    table.add_row("CPU Cores", f"{cpu_cores} Cores, {cpu_threads} Threads")
    table.add_row("[bold green]CPU Usage[/bold green]", f"[bold green]{cpu_usage}%[/bold green]")
    table.add_row("[bold green]Memory Usage[/bold green]", f"[bold green]{mem_percent}% ({mem_used} / {mem_total})[/bold green]")
    table.add_row("[bold green]Disk Usage (/)[/bold green]", f"[bold green]{disk_percent}% ({disk_used} / {disk_total})[/bold green]")
    table.add_row("Network", f"Sent: {net_sent} | Received: {net_recv}")
    
    return table


def main(watch: bool = typer.Option(False, "--watch", "-w", help="Keep the dashboard running and refresh every second.")):
    """
    A CLI dashboard to display your system's information and live stats.
    """
    console = Console()

    if not watch:
        # If not watching, just print once and exit.
        table = generate_stats_table()
        panel = Panel.fit(table, title="[bold blue]💻 System Dashboard[/bold blue]", border_style="blue", padding=(1, 2))
        console.print(panel)
    else:
        # If watching, use Rich's Live feature.
        try:
            with Live(console=console, screen=True, redirect_stderr=False) as live:
                while True:
                    table = generate_stats_table()
                    panel = Panel.fit(table, title="[bold blue]💻 System Dashboard[/bold blue]", border_style="blue", padding=(1, 2))
                    live.update(panel)
                    time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold red]Dashboard stopped.[/bold red]")

if __name__ == "__main__":
    typer.run(main)