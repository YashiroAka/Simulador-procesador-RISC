from cpu.isa import Instruction                     
from memory.cache import Cache                       
from cpu.pipeline import PipelineStage               
from collections import deque                        
from io_devices.interrupt_handler import InterruptHandler  
from io_devices.devices import Device                

registers = [0] * 32                  # 32 registros de propósito general
main_memory = [0] * 1024              # Memoria principal de 1024 posiciones
interrupt_pending = False            # Indicador de interrupción pendiente
cache = Cache(size=16, block_size=4, associativity=2)  # Inicializa una caché de 16 bloques, 2 vías, 4 palabras por bloque

pipeline = {
    'IF': PipelineStage('IF'),      # Instruction Fetch
    'ID': PipelineStage('ID'),      # Instruction Decode
    'EX': PipelineStage('EX'),      # Execute
    'MEM': PipelineStage('MEM'),    # Memory access
    'WB': PipelineStage('WB')       # Write Back
}

# ===== Programas de ejemplo (benchmarks) =====
program_secuencial = [
    Instruction('LD', rd=1, imm=0),
    Instruction('LD', rd=2, imm=4),
    Instruction('LD', rd=3, imm=8),
    Instruction('LD', rd=4, imm=12),
    Instruction('LD', rd=5, imm=16),
]

program_aleatorio = [
    Instruction('LD', rd=1, imm=100),
    Instruction('LD', rd=2, imm=250),
    Instruction('LD', rd=3, imm=30),
    Instruction('LD', rd=4, imm=75),
    Instruction('LD', rd=5, imm=10),
]

program_aritmetico = [
    Instruction('LD', rd=1, imm=0),
    Instruction('LD', rd=2, imm=4),
    Instruction('ADD', rd=3, rs1=1, rs2=2),
    Instruction('ST', rs1=3, imm=8),
    Instruction('MUL', rd=4, rs1=3, rs2=1),
]

benchmarks = {
    "Memoria Secuencial": program_secuencial,
    "Memoria Aleatoria": program_aleatorio,
    "Aritmético Intensivo": program_aritmetico,
}

program = program_secuencial
PC = 0                              # Program Counter
clock_cycles = 0                    # Ciclos de reloj
cache_hits = 0                      # Número de aciertos en caché
cache_misses = 0                    # Número de fallos en caché

# Inicialización de E/S y sistema de interrupciones 
interrupt_handler = InterruptHandler()
teclado = Device("Teclado")         # Dispositivo simulado de entrada
pantalla = Device("Pantalla")       # Dispositivo simulado de salida

# Simulación de E/S inicial
pantalla.write("Inicio del simulador")
interrupt_handler.trigger("INT_TECLADO")  # Genera interrupción externa del teclado

# Limpia las etapas del pipeline
def flush_pipeline():
    for stage in pipeline.values():
        stage.instr = None

# Carga uno de los benchmarks y reinicia el estado del sistema
def set_program(key):
    global program, PC, clock_cycles, interrupt_pending, cache_hits, cache_misses
    program = benchmarks[key]
    PC = 0
    clock_cycles = 0
    interrupt_pending = False
    cache_hits = 0
    cache_misses = 0
    flush_pipeline()

    # Reinicia registros
    for i in range(len(registers)):
        registers[i] = 0

    # Reinicia memoria
    for i in range(len(main_memory)):
        main_memory[i] = 0

    # Inicializa memoria con valores conocidos
    for i in range(0, 260):
        main_memory[i] = i

    # Limpia caché
    for i in range(len(cache.sets)):
        cache.sets[i] = deque(maxlen=cache.associativity)

# Obtiene la siguiente instrucción del programa
def fetch_next_instruction():
    global PC
    if PC < len(program):
        instr = program[PC]
        PC += 1
        return instr
    return None

# Simula un ciclo de reloj completo del pipeline
def simulate_cycle():
    global PC, clock_cycles, interrupt_pending, cache_hits, cache_misses

    # Interrupciones internas
    if interrupt_pending:
        print("[CPU] Atendiendo interrupción interna")
        pipeline['IF'].instr = Instruction('LD', rd=10, imm=99)  # Simula interrupción como una instrucción especial
        interrupt_pending = False
        clock_cycles += 1
        return

    # Etapa WB (Write Back) 
    instr = pipeline['WB'].instr
    if instr and instr.opcode in ['ADD', 'SUB', 'MUL', 'LD']:
        registers[instr.rd] = instr.result

    # Etapa MEM (acceso a memoria o caché) 
    instr = pipeline['MEM'].instr
    if instr:
        if instr.opcode == 'LD':
            hit = cache.access(instr.imm, main_memory)
            instr.result = main_memory[instr.imm]
            if hit:
                cache_hits += 1
            else:
                cache_misses += 1
        elif instr.opcode == 'ST':
            main_memory[instr.imm] = registers[instr.rs1]

    # Etapa EX (ejecución de operaciones aritméticas o saltos) 
    instr = pipeline['EX'].instr
    if instr:
        a = registers[instr.rs1] if instr.rs1 is not None else 0
        b = registers[instr.rs2] if instr.rs2 is not None else instr.imm
        if instr.opcode == 'ADD':
            instr.result = a + b
        elif instr.opcode == 'SUB':
            instr.result = a - b
        elif instr.opcode == 'MUL':
            instr.result = a * b
        elif instr.opcode == 'BEQ' and a == b:
            PC += instr.imm
            flush_pipeline()
            clock_cycles += 1
            return
        elif instr.opcode == 'BNE' and a != b:
            PC += instr.imm
            flush_pipeline()
            clock_cycles += 1
            return
        elif instr.opcode == 'JMP':
            PC = instr.imm
            flush_pipeline()
            clock_cycles += 1
            return
        elif instr.opcode == 'INT':
            print("[CPU] Instrucción INT: interrupción programada")
            interrupt_pending = True
            flush_pipeline()
            clock_cycles += 1
            return

    # Detección de dependencias (hazard) entre ID y EX 
    id_instr = pipeline['ID'].instr
    ex_instr = pipeline['EX'].instr
    if id_instr and ex_instr and id_instr.rs1 == ex_instr.rd:
        pipeline['WB'].instr = pipeline['MEM'].instr
        pipeline['MEM'].instr = pipeline['EX'].instr
        pipeline['EX'].instr = None
        clock_cycles += 1
        return

    # Etapa IF (Instruction Fetch)
    fetched_instr = fetch_next_instruction()

    # Avance del pipeline 
    pipeline['WB'].instr = pipeline['MEM'].instr
    pipeline['MEM'].instr = pipeline['EX'].instr
    pipeline['EX'].instr = pipeline['ID'].instr
    pipeline['ID'].instr = pipeline['IF'].instr
    pipeline['IF'].instr = fetched_instr

    clock_cycles += 1

# Simulación extendida con E/S e interrupciones externas 
def run_simulacion_con_io(ciclos=10):
    global interrupt_pending
    print("\n=== Iniciando simulación extendida con E/S ===")
    for ciclo in range(ciclos):
        print(f"\n[Ciclo {ciclo+1}]")

        simulate_cycle()

        # Manejo de interrupciones externas
        interrupt = interrupt_handler.handle_next()
        if interrupt:
            print(f"[I/O] Atendiendo interrupción externa: {interrupt}")
            interrupt_pending = True

if __name__ == "__main__":
    set_program("Memoria Secuencial")     
    run_simulacion_con_io(ciclos=8)       
