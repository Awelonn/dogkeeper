from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import box
from rich.panel import Panel
from rich.console import Group
from rich.columns import Columns
from rich.text import Text
import os
from foods import FOODS
from ui import print_header

console = Console()


def upgrade_cost(kennel, upgrade_type):
    costs = {
        "max_amount": kennel.max_amount_level * 200,
        "max_food_reserves": kennel.max_food_reserves_level * 150,
    }
    return costs.get(upgrade_type, 0)


def max_upgrades_cost(kennel):
    total = 0
    coins = kennel.coins
    level_amount = kennel.max_amount_level
    level_food = kennel.max_food_reserves_level
    while True:
        cost_amount = level_amount * 200
        cost_food = level_food * 150
        cheapest = min(cost_amount, cost_food)
        if coins < cheapest:
            break
        if cheapest == cost_amount:
            level_amount += 1
        else:
            level_food += 1
        coins -= cheapest
        total += cheapest
    return total


def buy_max_upgrades(kennel):
    while True:
        cheapest = min(
            ("max_amount", upgrade_cost(kennel, "max_amount")),
            ("max_food_reserves", upgrade_cost(kennel, "max_food_reserves")),
            key=lambda x: x[1],
        )
        if kennel.coins < cheapest[1]:
            break
        kennel.upgrades(cheapest[0])
    return True


DEFAULT_QUICK_ACTIONS = {
    3: {
        "label": "upgrade \\[kennel size]",
        "action": lambda k: k.upgrades("max_amount"),
        "cost": lambda k: upgrade_cost(k, "max_amount"),
    },
    4: {
        "label": "upgrade \\[everything possible]",
        "cost": max_upgrades_cost,
        "action": lambda k: buy_max_upgrades(k),
    },
    5: {
        "label": "buy \\[simple food]",
        "cost": lambda k: 3,
        "action": lambda k: k.buy_food("simple"),
    },
}

QUICK_ACTIONS = {
    3: {
        "label": "upgrade \\[kennel size]",
        "action": lambda k: k.upgrades("max_amount"),
        "cost": lambda k: upgrade_cost(k, "max_amount"),
    },
    4: {
        "label": "upgrade \\[everything possible]",
        "cost": max_upgrades_cost,
        "action": lambda k: buy_max_upgrades(k),
    },
    5: {
        "label": "buy \\[simple food]",
        "cost": lambda k: 3,
        "action": lambda k: k.buy_food("simple"),
    },
}

NEW_QUICK_ACTIONS = {}

AVAILABLE_ACTIONS = {
    "upgrade size": {
        "label": "upgrade \\[kennel size]",
        "action": lambda k: k.upgrades("max_amount"),
        "cost": lambda k: upgrade_cost(k, "max_amount"),
    },
    "upgrade resources": {
        "label": "upgrade \\[kennel food capacity]",
        "action": lambda k: k.upgrades("max_food_reserves"),
        "cost": lambda k: upgrade_cost(k, "max_food_reserves"),
    },
    "upgrade everything": {
        "label": "upgrade \\[everything possible]",
        "action": lambda k: buy_max_upgrades(k),
        "cost": max_upgrades_cost,
    },
    "buy simple food": {
        "label": "buy \\[simple food]",
        "action": lambda k: k.buy_food("simple"),
        "cost": lambda k: 3,
    },
}

def display_shop(kennel):
    # 1. Left Table
    menus = Table(box=box.MINIMAL_HEAVY_HEAD)
    menus.add_column("#", style="cyan")
    menus.add_column("Section")
    menus.add_row("1", "Dogs")
    menus.add_row("2", "Food")

    # 2. Right Table
    quick = Table(box=box.MINIMAL_HEAVY_HEAD)
    quick.add_column("#", style="cyan")
    quick.add_column(Text("Action", justify="center"), justify="left", no_wrap=True)
    quick.add_column("Cost", justify="right")
    for id, action in QUICK_ACTIONS.items():
        quick.add_row(str(id), action["label"], f"{action['cost'](kennel)} coins")

    layout_grid = Table.grid(expand=True)
    layout_grid.add_column(justify="left")
    layout_grid.add_column(ratio=1)
    layout_grid.add_column(justify="right", no_wrap=True)
    layout_grid.add_row(menus, "", quick)

    return Panel(
        layout_grid,
        title="[bold green]Shop[/]",
        subtitle="[dim]Customize: 0[/]",
        subtitle_align="left",
        border_style="green",
        expand=True,
        padding=(1, 2),
    )
    
def display_food_shop(kennel):
    kennel_xp = getattr(kennel, "xp", 0)
    table = Table(box=box.MINIMAL_HEAVY_HEAD)
    table.add_column("#", style="cyan")
    table.add_column("Name")
    table.add_column("Effect")
    table.add_column("Cost", justify="right")
    table.add_column("Storage", justify="right")
    table.add_column("XP", justify="right")

    for id, food in FOODS.items():
        locked = kennel_xp < food["xp_required"]
        affordable = kennel.coins >= food["cost"]
        xp_col = f"[red]{food['xp_required']} XP[/]" if locked else "[green]Unlocked[/]"
        style = "dim" if (locked or not affordable) else ""
        table.add_row(str(id), food["label"], food["effect"], f"{food['cost']} coins", f"{food['storage']}", xp_col, style=style)

    return Panel(table, title="[bold green]Food Shop[/]", border_style="green")

def food_shop_loop(kennel):
    last_output = None
    while True:
        os.system("clear")
        print_header(kennel)
        status = f"[bold yellow]Coins: {kennel.coins}[/]  [bold blue]Food: {kennel.food_reserves}/{kennel.max_food_reserves}[/]  [bold white]Dogs: {kennel.amount}/{kennel.max_amount}[/]"
        console.print(Panel(status, style="dim white", expand=False))
        console.print(display_food_shop(kennel))
        if last_output:
            console.print(last_output)
        choice = Prompt.ask("[bold cyan]Food Shop[/]")
        last_output = None
        if choice == "back":
            break
        else:
            try:
                choice = int(choice)
                if choice in FOODS:
                    food = FOODS[choice]
                    kennel_xp = getattr(kennel, "xp", 0)
                    if kennel_xp < food["xp_required"]:
                        last_output = "[red]Not enough XP to unlock this food.[/]"
                    elif kennel.coins < food["cost"]:
                        last_output = "[red]Not enough coins.[/]"
                    elif kennel.food_reserves + food["storage"] > kennel.max_food_reserves:
                        last_output = "[red]Not enough storage space.[/]"
                    else:
                        kennel.coins -= food["cost"]
                        kennel.food_reserves += food["storage"]
                        last_output = "[green]Done.[/]"
                else:
                    last_output = "[red]Invalid choice.[/]"
            except ValueError:
                last_output = "[red]Invalid choice.[/]"
    
def display_customization(kennel):
    actions = Table(box=box.SIMPLE_HEAD)
    actions.add_column("Command")
    actions.add_column("Arguments")
    actions.add_row("add", "\\[name] or ?")
    actions.add_row("remove", "\\[id]")
    actions.add_row("swap", "\\[id of 1st] \\[id of 2nd]")
    actions.add_row("cancel", "")
    actions.add_row("default", "")
    actions.add_row("save", "")
    actions.add_row("back", "")

    current_quick_actions = Table(title="Current Quick Actions", box=box.MINIMAL_HEAVY_HEAD)
    current_quick_actions.add_column("#")
    current_quick_actions.add_column(Text("Action", justify="center"))
    for id, action in NEW_QUICK_ACTIONS.items():
        current_quick_actions.add_row(
            str(id), action["label"]
        )
    layout_grid = Table.grid(expand=True)
    layout_grid.add_column(justify="left")
    layout_grid.add_column(ratio=1)
    layout_grid.add_column(justify="right")
    layout_grid.add_row(actions, "", current_quick_actions)
    return Panel(
        layout_grid,
        title="[bold yellow]Customization[/]",
        border_style="yellow",
    )

def customization_loop(kennel):
    global QUICK_ACTIONS
    global NEW_QUICK_ACTIONS
    NEW_QUICK_ACTIONS = QUICK_ACTIONS.copy()
    last_output = None
    while True:
        os.system("clear")
        print_header(kennel)
        status = f"[bold yellow]Coins: {kennel.coins}[/]  [bold blue]Food: {kennel.food_reserves}/{kennel.max_food_reserves}[/]  [bold white]Dogs: {kennel.amount}/{kennel.max_amount}[/]"
        console.print(Panel(status, style="dim white", expand=False))
        console.print(display_customization(kennel))

        if last_output:
            console.print(last_output)
        choice = Prompt.ask("[bold cyan]Customization[/]")
        last_output = None


        if choice == "save":
            QUICK_ACTIONS = NEW_QUICK_ACTIONS.copy()

        elif choice.startswith("add"):
            parts = choice.split(" ", 1)
            try:
                if parts[1] == "?":
                    last_output = "[cyan]Available actions:[/] " + ", ".join(AVAILABLE_ACTIONS.keys())
                else:
                    key = parts[1]
                    if key in AVAILABLE_ACTIONS:
                        next_id = max(NEW_QUICK_ACTIONS.keys()) + 1
                        NEW_QUICK_ACTIONS[next_id] = AVAILABLE_ACTIONS[key]
                    else:
                        last_output = f"[red]Unknown action '{key}'. Type '?' after 'add' to see available actions.[/]"
            except IndexError:
                last_output = "[red]Usage: add \\[action]. Type 'add ?' to see available actions.[/]"
        
        elif choice.startswith("remove"):
            parts = choice.split(" ", 1)
            try:
                key = int(parts[1])
                if key in NEW_QUICK_ACTIONS:
                    del NEW_QUICK_ACTIONS[key]
                    NEW_QUICK_ACTIONS = {
                        i + 3: action
                        for i, action in enumerate(NEW_QUICK_ACTIONS.values())
                    }
                else:
                    last_output = f"[red]No action with id {key}.[/]"
            except (IndexError, ValueError):
                last_output = "[red]Usage: remove [id][/]"

        elif choice.startswith("swap"):
            try:
                parts = choice.split(" ")
                temp = NEW_QUICK_ACTIONS[int(parts[1])]
                NEW_QUICK_ACTIONS[int(parts[1])] = NEW_QUICK_ACTIONS[int(parts[2])]
                NEW_QUICK_ACTIONS[int(parts[2])] = temp
            except (KeyError, IndexError, ValueError):
                print(
                    "Usage: swap [id of first quick action] [id of second quick action]"
                )
        elif choice == "default":
            NEW_QUICK_ACTIONS = DEFAULT_QUICK_ACTIONS.copy()
        elif choice == "cancel":
            NEW_QUICK_ACTIONS = QUICK_ACTIONS.copy()
        elif choice == "back":
            break

def shop_loop(kennel):
    last_output = None
    while True:
        os.system("clear")
        print_header(kennel)
        status = f"[bold yellow]Coins: {kennel.coins}[/]  [bold blue]Food: {kennel.food_reserves}/{kennel.max_food_reserves}[/]  [bold white]Dogs: {kennel.amount}/{kennel.max_amount}[/]"
        console.print(Panel(status, style="dim white", expand=False))
        console.print(display_shop(kennel))

        if last_output:
            console.print(last_output)
        choice = Prompt.ask("[bold cyan]Shop[/]")
        last_output = None
        if choice == "back":
            break
        elif choice == "0":
            customization_loop(kennel)
        elif choice == "2":
            food_shop_loop(kennel)
        else:
            try:
                choice = int(choice)
                if choice in QUICK_ACTIONS:
                    result = QUICK_ACTIONS[choice]["action"](kennel)
                    last_output = (
                        "[green]Done.[/]" if result else "[red]Not enough coins.[/]"
                    )
                else:
                    last_output = "[red]Invalid choice.[/]"
            except ValueError:
                last_output = "[red]Invalid choice.[/]"


if __name__ == "__main__":
    from dogkeeper import Kennel

    kennel = Kennel()
    console.print(display_shop(kennel))
