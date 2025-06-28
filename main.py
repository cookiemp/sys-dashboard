import typer
import platform
import psutil
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

app = typer.Typer()

def bytes_to_readable(b):
    gb = b / (1024**3)
    return f"{gb:.2f} GB" if gb >= 1 else f"{b / (1024**2):.2f} MB"

def get_snapshot_table():
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory    = psutil.virtual_memory()
    disk      = psutil.disk_usage('/')
    net       = psutil.net_io_counters()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Value",    style="magenta")

    os_name = (
        "Windows " + platform.win32_ver()[0]
        if platform.system() == "Windows"
        else f"{platform.system()} {platform.release()}"
    )
    table.add_row("OS",           os_name)
    table.add_row("Architecture", platform.machine())
    table.add_row("CPU Cores",    f"{psutil.cpu_count(logical=False)} Cores, {psutil.cpu_count(logical=True)} Threads")
    table.add_row("[bold green]CPU Usage[/bold green]",   f"[bold green]{cpu_usage}%[/bold green]")
    table.add_row("[bold green]Memory Usage[/bold green]", f"[bold green]{memory.percent}% ({bytes_to_readable(memory.used)} / {bytes_to_readable(memory.total)})[/bold green]")
    table.add_row("[bold green]Disk Usage (/)[/bold green]", f"[bold green]{disk.percent}% ({bytes_to_readable(disk.used)} / {bytes_to_readable(disk.total)})[/bold green]")
    table.add_row("Network", f"Sent: {bytes_to_readable(net.bytes_sent)} | Received: {bytes_to_readable(net.bytes_recv)}")
    return table

@app.command()
def main(
    watch: bool = typer.Option(
        False,
        "--watch", "-w",
        help="Keep the dashboard running and refresh every second."
    )
):
    console = Console()

    if not watch:
        panel = Panel.fit(
            get_snapshot_table(),
            title="[bold blue]💻 System Stats Snapshot[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
        console.print(panel)
        return

    # live mode
    psutil.cpu_percent(interval=None)  # prime
    def render_live():
        table = get_snapshot_table()  # same fields, but cpu_percent now non-blocking
        return Panel.fit(
            table,
            title="[bold blue]💻 System Dashboard (Live)[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )

    try:
        with Live(render_live(), console=console, screen=True, redirect_stderr=False) as live:
            while True:
                time.sleep(1)
                live.update(render_live())
    except KeyboardInterrupt:
        console.print("\n[bold red]Dashboard stopped.[/bold red]")

if __name__ == "__main__":
    app()
