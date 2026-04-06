import json
import os
import asyncio
import random
import aiohttp
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, RichLog, ProgressBar, TabbedContent, TabPane, Input, Button
from textual.reactive import reactive

class Sidebar(Vertical): pass
class MainWorkspace(Vertical): pass

class OctraTerminalApp(App):
    """Advanced TUI Manager for Octra FHE Network."""

    CSS = """
    Screen { background: $surface-darken-1; }
    Sidebar { width: 30%; dock: left; border-right: solid green; padding: 1; background: #0a0a0a; }
    MainWorkspace { width: 70%; padding: 1; background: #000000; }
    .wallet-title { color: lime; text-style: bold; padding-bottom: 1; }
    .wallet-data { color: #00ff00; margin-bottom: 2; }
    .metric-title { color: orange; text-style: bold; margin-top: 2; }
    
    RichLog { height: 35%; border-top: dashed green; background: #050505; color: #00ff00; }
    Input { background: #1a1a1a; color: #00ff00; border: solid green; margin-bottom: 0; height: 3; }
    Button { background: green; color: black; text-style: bold; margin-top: 1; }
    Button:hover { background: lime; }
    .grid-display { color: cyan; text-style: bold; background: #111; padding: 1; margin-bottom: 1; border: solid cyan;}
    """

    BINDINGS = [
        ("q", "quit", "Quit Terminal"),
        ("d", "app.toggle_dark", "Toggle Dark Mode"),
        ("b", "trigger_bootstrap", "Run Bootstrapping"),
    ]

    wallet_address = reactive("Loading...")
    wallet_balance = reactive("0.0 OCT")
    current_noise_level = reactive(12.5)
    
    gol_grid = reactive([
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0]
    ])

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal():
            with Sidebar():
                yield Static("=== OCTRA WALLET ===", classes="wallet-title")
                yield Static(id="lbl_address", classes="wallet-data")
                yield Static(id="lbl_balance", classes="wallet-data")
                
                yield Static("=== HFHE METRICS ===", classes="metric-title")
                yield Static("Cubic Noise Level (Max 35%)", classes="wallet-data")
                yield ProgressBar(total=100.0, show_eta=False, id="noise_bar")
                
            with MainWorkspace():
                with TabbedContent(initial="tab-transcipher"): 
                    
                    with TabPane("FHE Game of Life", id="tab-gol"):
                        yield Static("\n[bold lime]Encrypted Cellular Automata[/bold lime]\n5x5 'Blinker' state. Computed via HFHE without IF conditions.\n", markup=True)
                        yield Static(id="grid_ui", classes="grid-display")
                        yield Button("Evolve Generation (HFHE C++ Engine)", id="btn_gol_evolve")
                    
                    with TabPane("FHE Sandbox", id="tab-sandbox"):
                        yield Static("\n[bold lime]Local HFHE Simulation[/bold lime]\n", markup=True)
                        yield Input(placeholder="Vector A (e.g., 111)", id="input_vec_a")
                        yield Input(placeholder="Vector B (e.g., 222)", id="input_vec_b")
                        yield Button("Run Homomorphic Addition", id="btn_fhe_add")
                    
                    with TabPane("Transciphering", id="tab-transcipher"):
                        yield Static("\n[bold lime]Proxy Re-encryption Transfer[/bold lime]\n", markup=True)
                        yield Input(placeholder="Target Address (oct...)", id="input_target_addr")
                        yield Input(placeholder="Amount to send", id="input_amount")
                        yield Button("Execute Transcipher Transfer", id="btn_transfer")
                
                yield RichLog(id="system_log", highlight=True, markup=True)
                
        yield Footer()

    async def on_mount(self) -> None:
        self.title = "Octra FHE Terminal - axFH017/2026"
        self.load_wallet_config()
        self.update_ui_state()
        self.render_grid()
        self.set_interval(3.0, self.simulate_irmin_db_logs)

    def render_grid(self) -> None:
        display_text = ""
        for row in self.gol_grid:
            display_text += " ".join(["[lime]█[/lime]" if cell == 1 else "[dim]·[/dim]" for cell in row]) + "\n"
        self.query_one("#grid_ui", Static).update(display_text)

    def load_wallet_config(self) -> None:
        try:
            if os.path.exists("wallet.json"):
                with open("wallet.json", "r") as f:
                    data = json.load(f)
                    self.wallet_address = data.get("addr", "UNKNOWN")
            else:
                self.wallet_address = "No wallet.json found!"
        except Exception as e:
            self.write_log(f"[red]Error loading wallet: {e}[/red]")

    def update_ui_state(self) -> None:
        short_addr = f"{self.wallet_address[:10]}...{self.wallet_address[-4:]}" if len(self.wallet_address) > 15 else self.wallet_address
        self.query_one("#lbl_address", Static).update(f"Addr: {short_addr}")
        self.query_one("#lbl_balance", Static).update(f"Balance: 1,450.00 OCT")
        self.query_one("#noise_bar", ProgressBar).update(progress=self.current_noise_level)

    def write_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.query_one("#system_log", RichLog).write(f"[[dim]{timestamp}[/dim]] {message}")

    def simulate_irmin_db_logs(self) -> None:
        events = ["Synced vector objects from Bootstrap node.", "Validating hyperedge intersections..."]
        self.write_log(f"[dim][IrminDB] {random.choice(events)}[/dim]")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        # İŞTE HATAMIZI DÜZELTTİĞİMİZ YER BURASI!
        if button_id == "btn_gol_evolve":
            await self.run_gol_fhe_step()
        elif button_id == "btn_fhe_add":
            self.increase_noise(4.5)
        elif button_id == "btn_transfer":
            await self.run_transcipher_transfer() # Artık gerçek fonksiyonu çağırıyor!

    async def run_gol_fhe_step(self) -> None:
        self.write_log("[yellow]Serializing state and sending to C++ Circle Engine...[/yellow]")
        state_str = "".join(str(cell) for row in self.gol_grid for cell in row)
        binary_path = os.path.abspath(os.path.join(os.getcwd(), "circle_contract", "octra_gol"))
        
        if not os.path.exists(binary_path):
            self.write_log("[bold red]FATAL ERROR: C++ binary 'octra_gol' not found! Please compile it.[/bold red]")
            return

        try:
            process = await asyncio.create_subprocess_exec(
                binary_path, state_str,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.write_log(f"[bold red]Circle Execution Failed:[/bold red] {stderr.decode().strip()}")
                return

            output_data = json.loads(stdout.decode().strip())
            new_grid = [[int(output_data["new_state"][i * 5 + j]) for j in range(5)] for i in range(5)]
            self.gol_grid = new_grid
            self.render_grid()
            
            self.write_log(f"[bold green]Circle Execution Complete (C++ Subprocess OK)[/bold green]")
            self.write_log(f"[cyan]➜ Execution Time:[/cyan] {output_data['execution_ms']:.4f} ms")
            self.increase_noise(8.5)
        except Exception as e:
            self.write_log(f"[bold red]System Error:[/bold red] {str(e)}")

    async def run_transcipher_transfer(self) -> None:
        target = self.query_one("#input_target_addr", Input).value
        amount = self.query_one("#input_amount", Input).value
        
        if not target or not amount:
            self.write_log("[red]Error: Address and Amount required.[/red]")
            return

        self.write_log(f"[yellow]Preparing LIVE Transcipher Transfer of {amount} OCT to {target[:8]}...[/yellow]")
        
        try:
            with open("wallet.json", "r") as f:
                wallet_data = json.load(f)
            
            rpc_url = wallet_data.get("rpc", "https://octra.network")
            sender_addr = wallet_data.get("addr")
            
            payload = {
                "jsonrpc": "2.0",
                "method": "octra_sendEncryptedTransaction",
                "params": [{
                    "from": sender_addr,
                    "to": target,
                    "amount": amount,
                    "encryption_type": "HFHE_Transcipher",
                    "signature": "mock_signature_for_now"
                }],
                "id": 1
            }

            self.write_log(f"[dim]Broadcasting to {rpc_url}...[/dim]")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(rpc_url, json=payload) as response:
                    # Octra sunucularından gelen GERÇEK cevabı ekrana basıyoruz
                    if response.status == 200:
                        data = await response.json()
                        self.write_log(f"[bold green]RPC Response 200 OK:[/bold green] {data}")
                    else:
                        error_text = await response.text()
                        self.write_log(f"[bold red]RPC Error {response.status}:[/bold red] {error_text}")
                        
        except Exception as e:
            self.write_log(f"[bold red]Network Connection Failed:[/bold red] {str(e)}")
            
        self.increase_noise(15.2)

    def increase_noise(self, amount: float) -> None:
        self.current_noise_level += amount
        if self.current_noise_level > 35.0: self.current_noise_level = 35.0
        self.update_ui_state()
        if self.current_noise_level >= 35.0:
            self.write_log("[bold red]CRITICAL: Ciphertext noise reached 35% threshold! Press 'b' to Bootstrap.[/bold red]")

    def action_trigger_bootstrap(self) -> None:
        self.current_noise_level = 1.0
        self.update_ui_state()
        self.write_log("[bold green][+] Bootstrapping complete. Noise reduced to 1.0%.[/bold green]")

if __name__ == "__main__":
    app = OctraTerminalApp()
    app.run()