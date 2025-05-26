import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main
from main import pipeline, simulate_cycle, registers, main_memory, cache, set_program
from io_devices.devices import Device
from io_devices.interrupt_handler import InterruptHandler


class PipelineGUI:
    def __init__(self, root):
        self.root = root
        root.title("Simulador de Pipeline")

        # Periféricos y manejador de interrupciones
        self.interrupt_handler = InterruptHandler()
        self.teclado = Device("Teclado")
        self.pantalla = Device("Pantalla")

        # Interfaz principal
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.grid(row=0, column=0, sticky="NSEW")

        self.cycle_label = ttk.Label(self.main_frame, text="Ciclo: 0", font=("Arial", 16, "bold"))
        self.cycle_label.grid(row=0, column=0, columnspan=4, pady=10)

        # Pipeline
        pipeline_frame = ttk.LabelFrame(self.main_frame, text="Etapas del Pipeline", padding=10)
        pipeline_frame.grid(row=1, column=0, columnspan=4, sticky="EW", padx=5, pady=5)
        pipeline_frame.columnconfigure(tuple(range(5)), weight=1)

        self.pipeline_labels = {}
        for idx, stage in enumerate(["IF", "ID", "EX", "MEM", "WB"]):
            ttk.Label(pipeline_frame, text=stage, font=("Arial", 10, "bold")).grid(row=0, column=idx, padx=5)
            label = ttk.Label(pipeline_frame, text="-", relief="solid", width=15, anchor="center")
            label.grid(row=1, column=idx, padx=5, pady=5)
            self.pipeline_labels[stage] = label

        # Áreas de información
        self.reg_text = self.create_text_frame("Registros", row=2, column=0)
        self.mem_text = self.create_text_frame("Memoria Principal (64)", row=2, column=1)
        self.cache_text = self.create_text_frame("Caché", row=2, column=2)
        self.ops_text = self.create_text_frame("Operaciones", row=3, column=0)

        # Nuevo: interrupciones y logs de E/S
        self.interrupt_list = self.create_listbox_frame("Cola de Interrupciones", row=3, column=1)
        self.log_text = self.create_text_frame("Log de Entrada/Salida", row=3, column=2)

        # Botones
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="▶ Siguiente Ciclo", command=self.next_cycle).pack(side="left", padx=5)
        ttk.Button(button_frame, text="▶ Ejecutar Todo", command=self.run_all).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🔄 Reiniciar", command=self.reset_simulation).pack(side="left", padx=5)

        # E/S manual
        ttk.Button(button_frame, text="⌨ Simular Teclado", command=self.simular_teclado).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🖥 Simular Pantalla", command=self.simular_pantalla).pack(side="left", padx=5)

        # Benchmark
        select_frame = ttk.Frame(self.main_frame)
        select_frame.grid(row=5, column=0, columnspan=4, pady=(10, 0))
        ttk.Label(select_frame, text="Benchmark:").pack(side="left", padx=5)

        self.benchmark_var = tk.StringVar()
        self.benchmark_combo = ttk.Combobox(select_frame, textvariable=self.benchmark_var, state="readonly")
        self.benchmark_combo['values'] = list(main.benchmarks.keys())
        self.benchmark_combo.current(0)
        self.benchmark_combo.pack(side="left", padx=5)

        ttk.Button(select_frame, text="📂 Cargar", command=self.load_benchmark).pack(side="left", padx=5)

        self.update_display()

    def create_text_frame(self, title, row, column):
        frame = ttk.LabelFrame(self.main_frame, text=title, padding=10)
        frame.grid(row=row, column=column, sticky="NSEW", padx=5, pady=5)
        text = tk.Text(frame, width=40, height=10, wrap="none")
        text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame, command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.configure(yscrollcommand=scrollbar.set)
        return text

    def create_listbox_frame(self, title, row, column):
        frame = ttk.LabelFrame(self.main_frame, text=title, padding=10)
        frame.grid(row=row, column=column, sticky="NSEW", padx=5, pady=5)
        listbox = tk.Listbox(frame, height=8)
        listbox.pack(fill="both", expand=True)
        return listbox

    def simular_teclado(self):
        self.interrupt_handler.trigger("INT_TECLADO")
        self.log_text.insert(tk.END, "Teclado: INT_TECLADO generada\n")
        self.update_display()

    def simular_pantalla(self):
        self.pantalla.write("Hola desde GUI")
        self.log_text.insert(tk.END, "Pantalla: mensaje enviado\n")
        self.update_display()

    def next_cycle(self):
        simulate_cycle()
        interrupt = self.interrupt_handler.handle_next()
        if interrupt:
            self.log_text.insert(tk.END, f"[INT] Atendiendo: {interrupt}\n")
            main.interrupt_pending = True
        self.update_display()

    def run_all(self):
        if any(stage.instr for stage in pipeline.values()) or main.PC < len(main.program):
            self.next_cycle()
            self.root.after(150, self.run_all)

    def reset_simulation(self):
        set_program(self.benchmark_var.get())
        self.interrupt_handler.interrupt_queue.clear()
        self.log_text.delete("1.0", tk.END)
        self.update_display()

    def load_benchmark(self):
        key = self.benchmark_var.get()
        set_program(key)
        self.update_display()

    def update_display(self):
        self.cycle_label.config(text=f"Ciclo: {main.clock_cycles}")
        for stage, label in self.pipeline_labels.items():
            instr = pipeline[stage].instr
            label.config(text=instr.opcode if instr else "-")

        self.reg_text.delete("1.0", tk.END)
        for i in range(0, 32, 4):
            line = "  ".join([f"R{j}:{registers[j]:>3}" for j in range(i, i+4)])
            self.reg_text.insert(tk.END, line + "\n")

        self.mem_text.delete("1.0", tk.END)
        for i in range(0, 64, 8):
            line = "  ".join([f"[{j}]:{main_memory[j]:>3}" for j in range(i, i+8)])
            self.mem_text.insert(tk.END, line + "\n")

        self.cache_text.delete("1.0", tk.END)
        for i, cache_set in enumerate(cache.sets):
            self.cache_text.insert(tk.END, f"Set {i}:\n")
            for block in cache_set:
                val = "V" if block.valid else "-"
                tag = block.tag if block.valid else "-"
                data = block.data if block.valid else "-"
                self.cache_text.insert(tk.END, f"  [{val}] Tag: {tag} | Data: {data}\n")

        self.ops_text.delete("1.0", tk.END)
        for stage in ["EX", "MEM", "WB"]:
            instr = pipeline[stage].instr
            op_str = self.instr_operation_str(stage, instr)
            self.ops_text.insert(tk.END, f"{stage}: {op_str}\n")

        # Actualizar lista de interrupciones
        self.interrupt_list.delete(0, tk.END)
        for interrupt in self.interrupt_handler.interrupt_queue:
            self.interrupt_list.insert(tk.END, interrupt)

    @staticmethod
    def instr_operation_str(stage, instr):
        if not instr:
            return "-"
        op = instr.opcode
        rd = f"R{instr.rd}" if instr.rd is not None else ""
        rs1 = f"R{instr.rs1}" if instr.rs1 is not None else ""
        rs2 = f"R{instr.rs2}" if instr.rs2 is not None else ""
        imm = f"{instr.imm}" if instr.imm is not None else ""

        if stage == 'EX':
            if op in ['ADD', 'SUB', 'MUL']:
                return f"{rd} = {rs1} {op.lower()} {rs2}"
            elif op == 'LD':
                return f"Cargando {rd} desde M[{imm}]"
            elif op == 'ST':
                return f"Guardando {rs1} en M[{imm}]"
            elif op == 'BEQ':
                return f"Si {rs1} == {rs2} saltar {imm}"
            elif op == 'BNE':
                return f"Si {rs1} != {rs2} saltar {imm}"
            elif op == 'JMP':
                return f"Saltar a {imm}"
            elif op == 'INT':
                return "Interrupción"
        elif stage == 'MEM':
            if op == 'LD':
                return f"Leer M[{imm}] → {rd}"
            elif op == 'ST':
                return f"Escribir {rs1} → M[{imm}]"
        elif stage == 'WB':
            if op in ['ADD', 'SUB', 'MUL', 'LD']:
                res = getattr(instr, 'result', None)
                return f"{rd} = {res}"
        return op


if __name__ == '__main__':
    root = tk.Tk()
    gui = PipelineGUI(root)
    root.mainloop()