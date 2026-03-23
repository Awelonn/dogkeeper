import json
from datetime import date
import sys
import os
import time
import random
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.console import Group
from rich import box
console = Console()

DOG_NAMES = ["Buddy", "Max", "Bella", "Charlie", "Luna", "Cooper", "Daisy", "Rocky", "Molly", "Bear", "Sadie", "Tucker", "Lola", "Duke", "Zoe", "Thor", "Nala", "Rex", "Cleo", "Bruno", "Rosie", "Atlas", "Nova", "Diesel", "Maple", "Ghost", "Shadow", "Storm", "Biscuit", "Pepper"]

def plural_check(word, amount):
    if amount != 1:
        word += "s"
    return word

class Kennel:
    def __init__(self):
        self.amount = 0
        self.max_amount = 3
        self.max_amount_level = 1
        self.dogs_list = []
        self.food_reserves = 7
        self.max_food_reserves = 10
        self.max_food_reserves_level = 1
        self.created_at = date.today()
        self.last_processed_day = date.today()
        self.coins = 100

    def __str__(self):
        days = (date.today() - self.created_at).days
        return f"Kennel statistics:\n\tDate created:\t{self.created_at} ({(date.today() - self.created_at).days} {plural_check('day', days)} ago)\n\tCoins: {self.coins}\n\tDogs:\t\t{self.amount}/{self.max_amount}\n\tFood:\t\t{self.food_reserves}/{self.max_food_reserves}"
    
    def __rich__(self):
        days = (date.today() - self.created_at).days
        table = Table(
            title="[bold]Kennel[/bold]",
            box=box.ROUNDED,
            header_style="bold magenta",
            title_style="bold blue",
            row_styles=["none", "dim"]
        )
        table.add_column("Attribute", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="yellow")
        table.add_row("Created", f"{self.created_at} ({days} {plural_check('day', days)} ago)")
        table.add_row("Coins", str(self.coins))
        table.add_row("Dogs", f"{self.amount}/{self.max_amount}")
        table.add_row("Food", f"{self.food_reserves}/{self.max_food_reserves}")
        return table
    
    def rich_day_summary(self, before):
        from rich.table import Table
        from rich import box
    # Use a cleaner box style and collapse padding for a sleek look
        table = Table(
            title="[bold]Kennel Summary[/bold]", 
            box=box.ROUNDED,
            header_style="bold magenta",
            title_style="bold blue",
            row_styles=["none", "dim"]
        )

        table.add_column("Attribute", style="cyan", no_wrap=True)
        table.add_column("Before", justify="right", style="yellow")
        table.add_column("After", justify="right", style="green")
        table.add_column("Change", justify="right")

        # Helper to calculate and format the difference
        def get_row_data(label, old_val, new_val):
            diff = new_val - old_val
            diff_str = f"[bold red]{diff}[/]" if diff < 0 else f"[bold green]+{diff}[/]"
            if diff == 0: diff_str = "[dim]0[/]"
            return [label, str(old_val), str(new_val), diff_str]

        table.add_row(*get_row_data("Coins", before['coins'], self.coins))
        table.add_row(*get_row_data("Food", before['food_reserves'], self.food_reserves))

        return table

    
    def save(self):
        dict_list = [dog.__dict__ for dog in self.dogs_list]
        with open("kennel.json", "w") as f:
            json.dump({ "dogs": dict_list,  
                        "amount": self.amount,
                        "max_amount": self.max_amount,
                        "max_amount_level": self.max_amount_level,
                        "food_reserves": self.food_reserves,
                        "max_food_reserves": self.max_food_reserves,
                        "max_food_reserves_level": self.max_food_reserves_level,
                        "created_at": str(self.created_at),
                        "last_processed_day": str(self.last_processed_day),
                        "coins": self.coins
                    }, f, indent=4)

    def load(self):
        try:
            with open("kennel.json", "r") as f:
                data = json.load(f)
            self.dogs_list = [Dog(**dog) for dog in data["dogs"]]
            self.coins = data["coins"]
            self.amount = data["amount"]
            self.max_amount = data["max_amount"]
            self.max_amount_level = data["max_amount_level"]
            self.food_reserves = data["food_reserves"]
            self.max_food_reserves = data["max_food_reserves"]
            self.max_food_reserves_level = data["max_food_reserves_level"]
            self.created_at = date.fromisoformat(data["created_at"])
            self.amount = len(self.dogs_list)
            self.last_processed_day = date.fromisoformat(data["last_processed_day"])
            missed_days = (date.today() - self.last_processed_day).days
            snapshots = {
                dog.name: {
                    "happiness": dog.happiness, 
                    "is_fed": dog.is_fed,
                    "weight": dog.weight,
                    "size": dog.size
                } for dog in self.dogs_list
            }
            snapshots["kennel"] = {"coins": self.coins, "food_reserves": self.food_reserves}
            if missed_days > 0:
                for _ in range(missed_days):
                    self.new_day()
                self.last_processed_day = date.today()
                print(f"You were gone for {missed_days} {plural_check('day', missed_days)}.")
                console.print(self.rich_day_summary(snapshots["kennel"]))
                print()
                for dog in self.dogs_list:
                    console.print(dog.rich_day_summary(snapshots[dog.name]))
                print()
        except FileNotFoundError:
            print("No save found.")

    def new_day(self):
        size_multiplier = {"tiny": 0.5, "small": 0.7, "medium": 1, "large": 1.3, "huge": 2}
        for dog in self.dogs_list:
            if dog.is_fed:
                dog.happiness = min(dog.happiness + 2, 10)
            else:
                dog.happiness = max(dog.happiness - 5, 0)
            dog.happiness = max(dog.happiness - 2, 0)

            dog.is_fed = False
            dog.can_play = True
            dog.weight = max(dog.weight - 1, 1)
            dog.determine_size()

            if dog.happiness == 10:
                happiness_multiplier = 2
            elif dog.happiness == 0:
                happiness_multiplier = 0
            elif dog.happiness < 5:
                happiness_multiplier = 0.5
            else:
                happiness_multiplier = 1
            self.coins += 10 * size_multiplier.get(dog.size) * happiness_multiplier
        
    def buy_dog(self, name=None):
        if name is None:
            name = random.choice(DOG_NAMES)
        cost = 100
        if self.coins >= cost:
            dog = Dog(name)
            result = self.add_dog(dog)
            if result:
                self.coins -= cost
                return result
        else:
            print(f"Not enough coins.")

    def add_dog(self, dog: 'Dog'):
        if self.amount == self.max_amount:
            print(f"The kennel is full.")
            return None
        elif not any(d.name == dog.name for d in self.dogs_list):
            self.dogs_list.append(dog)
            self.amount += 1
            return dog
        else:
            print(f"{dog.name} is already in the kennel.")
            return None

    def remove_dog(self, dog: 'Dog'):
        if dog in self.dogs_list:
            self.dogs_list.remove(dog)
            self.amount -= 1
            print(f"{dog.name} removed from the kennel. ({self.amount}/{self.max_amount} dogs in the kennel.)")
        else:
            print(f"{dog.name} is already not in the kennel.")

    def sort(self, method, reverse):
        try:
            order = "ascending" if not reverse else "descending"
            sorted_list = sorted(self.dogs_list, key=lambda x: getattr(x, method), reverse=reverse)
            print(f"Dogs in kennel sorted by {method} ({order}): ")
            if method == "name":
                for dog in sorted_list:
                    print(dog.name)
            else:
                for dog in sorted_list:
                    print(f"{dog.name}: \t{getattr(dog, method)}")
            print()
        except AttributeError:
            print(f"Dogs dont have '{method}' attribute.")

    def feed(self):

        table = Table(
            title="[bold]Feeding Report[/bold]", 
            box=box.ROUNDED,
            header_style="bold magenta",
            title_style="bold yellow",
            row_styles=["none", "dim"]
        )

        table.add_column("Dog", style="cyan", no_wrap=True)
        table.add_column("Cost", justify="right", style="yellow")
        table.add_column("Weight Growth", justify="center")
        table.add_column("Size Change", justify="center")
        table.add_column("Status", justify="right")

        fed_all = True
        for dog in self.dogs_list:
            old_weight = dog.weight
            old_size = dog.size
            old_food_req = dog.food_req
            
            if self.food_reserves >= dog.food_req:
                self.food_reserves -= dog.food_req
                dog.is_fed = True
                dog.weight += 1
                dog.determine_size()
                
                weight_str = f"{old_weight} [blue]→[/] {dog.weight}"
                size_str = f"{old_size} [bold pink]→ {dog.size}[/]" if old_size != dog.size else f"[dim]{dog.size}[/]"
                status_str = "[bold green]FED[/]"
                
                table.add_row(dog.name, str(old_food_req), weight_str, size_str, status_str)
            else:
                table.add_row(
                    dog.name, 
                    f"[red]{old_food_req}[/]", 
                    f"[dim]{dog.weight}[/]", 
                    f"[dim]{dog.size}[/]", 
                    "[bold red]HUNGRY[/]"
                )
                fed_all = False
        if not fed_all:
            return Group(table, "[bold red]⚠ Warning: Some dogs are hungry![/]")
        return table
    
    
    def play(self, first: 'Dog', second: 'Dog'):
        if first.can_play and second.can_play:
            first_reference_happiness = first.happiness
            second_reference_happiness = second.happiness
            first.happiness = first.happiness + 1 if first.happiness + 1 <= 10 else 10
            second.happiness = second.happiness + 1 if second.happiness + 1 <= 10 else 10
            first.can_play = False
            second.can_play = False
            print(f"{first.name} and {second.name} played together and had a lot of fun!\n{first.name} {first_reference_happiness}/10 -> {first.happiness}/10 happiness\n{second.name} {second_reference_happiness}/10 -> {second.happiness}/10 happiness\n")
        elif not first.can_play and second.can_play:
            print(f"{first.name} has already played today.")
        elif first.can_play and not second.can_play:
            print(f"{second.name} has already played today.")
        else:
            print(f"Both {first.name} and {second.name} have already played today")
        
    def upgrades(self, upgrade):
        if upgrade == "max_amount":
            cost = self.max_amount_level * 200
            if self.coins >= cost:
                self.max_amount_level += 1
                self.max_amount += 1
                self.coins -= cost
                print(f"Upgraded the maximum amount of dogs your kennel can have. {self.max_amount_level - 1} -> {self.max_amount_level} level. {self.max_amount - 1} -> {self.max_amount} dog capacity")
            else:
                print(f"Not enough coins.")


                


class Dog:
    def __init__(self, name, age=None, weight=None, happiness=None, is_fed=False, can_play=True, size="", food_req=0):
        self.name = name
        self.age = age if age is not None else random.randint(1, 16)
        self.weight = weight if weight is not None else random.randint(2, 50)
        self.happiness = happiness if happiness is not None else random.randint(4, 9)
        self.is_fed = is_fed
        self.can_play = can_play
        self.size = size
        self.food_req = food_req
        self.determine_size()

    def determine_size(self):
        if self.weight < 5:
            self.size = "tiny"
            self.food_req = 1
        elif self.weight < 10:
            self.size = "small"
            self.food_req = 2
        elif self.weight < 20:
            self.size = "medium"
            self.food_req = 3
        elif self.weight < 45:
            self.size = "large"
            self.food_req = 5
        else:
            self.size = "huge"
            self.food_req = 10         

    def __str__(self):
        hungry = "yes" if not self.is_fed else "no"
        return f"\tName:\t\t\t{self.name}\n\tAge:\t\t\t{self.age}\n\tWeight:\t\t\t{self.weight} kg\n\tSize:\t\t\t{self.size}\n\tFood consumption:\t{self.food_req} food per day\n\tHungry:\t\t\t{hungry}\n\tHappiness:\t\t{self.happiness}/10\n"

    def __rich__(self):
        hungry = "[red]yes[/red]" if not self.is_fed else "[green]no[/green]"
        table = Table(
            title=f"[bold]{self.name}[/bold]",
            box=box.ROUNDED,
            header_style="bold magenta",
            title_style="bold green",
            row_styles=["none", "dim"]
        )
        table.add_column("Attribute", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="yellow")
        table.add_row("Age", str(self.age))
        table.add_row("Weight", f"{self.weight} kg")
        table.add_row("Size", self.size)
        table.add_row("Food/day", str(self.food_req))
        table.add_row("Hungry", hungry)
        table.add_row("Happiness", f"{self.happiness}/10")
        return table

    def rich_day_summary(self, before):  
        table = Table(
            title=f"[bold]{self.name}[/bold]", 
            box=box.ROUNDED,
            header_style="bold magenta",
            title_style="bold green",
            title_justify="center",
            row_styles=["none", "dim"]
        )

        table.add_column("Attribute", style="cyan", no_wrap=True)
        table.add_column("Before", justify="right", style="yellow")
        table.add_column("After", justify="right", style="green")
        table.add_column("Change", justify="right")

        # 1. Happiness Row
        h_diff = self.happiness - before['happiness']
        h_change = f"[bold green]+{h_diff}[/]" if h_diff > 0 else (f"[bold red]{h_diff}[/]" if h_diff < 0 else "[dim]0[/]")
        table.add_row("Happiness", f"{before['happiness']}/10", f"{self.happiness}/10", h_change)

        # 2. Weight Row (Tracking the -1kg loss)
        w_diff = self.weight - before['weight']
        w_change = f"[bold red]{w_diff}kg[/]" if w_diff < 0 else (f"[bold green]+{w_diff}kg[/]" if w_diff > 0 else "[dim]0[/]")
        table.add_row("Weight", f"{before['weight']}kg", f"{self.weight}kg", w_change)

        # 3. Size Row (Tracking if they shrunk)
        size_changed = before['size'] != self.size
        s_change = "[bold red]↓ SHRUNK[/]" if size_changed else "[dim]--[/]"
        table.add_row("Size", before['size'], self.size, s_change)

        # 4. Hunger Status Row
        was_fed = "[green]no[/]" if before['is_fed'] else "[red]yes[/]"
        is_hungry = "[red]yes[/]" if not self.is_fed else "[green]no[/]"
        status_change = "[bold blue]→[/]" if before['is_fed'] != self.is_fed else "[dim]--[/]"
        table.add_row("Hungry?", was_fed, is_hungry, status_change)

        return table


kennel1 = Kennel()


console = Console()

def main():
    rprint = console.print
    last_output = None

    while True:
        os.system('clear')
        rprint(Panel.fit(
        "[bold yellow]DOGKEEPER[/]\n[dim]Manage your kennel, feed your dogs.[/]",
        border_style="blue", 
        box=box.DOUBLE
        ))

        status = f"[bold yellow]🪙 {kennel1.coins}[/]  [bold blue]🍖 {kennel1.food_reserves}/{kennel1.max_food_reserves}[/]  [bold white]🐕 {kennel1.amount}/{kennel1.max_amount}[/]"
        rprint(Panel(status, style="dim white", expand=False))

        if last_output:
            rprint(last_output)

        raw_input = Prompt.ask("[bold cyan]Dogkeeper[/]")
        full_command = raw_input.split(" ")
        cmd = full_command[0].lower()


        if cmd == "buy":
            name = Prompt.ask("Name?", default="")
            result = kennel1.buy_dog(name if name else None)
            last_output = result if result else "[red]Not enough coins.[/]"
        
        elif cmd == "feed":
            last_output = kennel1.feed()

        elif cmd == "kennel":
            last_output = kennel1

        elif cmd == "dog":
            if len(full_command) > 1:
                dog = next((d for d in kennel1.dogs_list if d.name.lower() == full_command[1].lower()), None)
                if dog:
                    last_output = dog
                else:
                   last_output = f"[red]No dog named '{full_command[1]}' found.[/]"
            else:
                names = [f"[cyan]{dog.name}[/]" for dog in kennel1.dogs_list]
                last_output = ", ".join(names)

        elif cmd in ["save", "load"]:
            getattr(kennel1, cmd)()
            last_output = f"[bold green]✔ {cmd.capitalize()} successful![/]"

        elif cmd == "clear":
            last_output = None

        elif cmd == "exit":
            break

        else:
            last_output = "[dim]Commands: buy, feed, kennel, dog <name>, play, save, load, clear[/]"

main()
