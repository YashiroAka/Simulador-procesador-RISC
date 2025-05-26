# Simulador de Pipeline de Procesador con GUI, Caché e Interrupciones

Este proyecto es un simulador educativo de una arquitectura de procesador que incluye:

- Pipeline de 5 etapas (IF, ID, EX, MEM, WB)
- Memoria caché con reemplazo asociativo
- Memoria principal (RAM)
- Interrupciones y dispositivos de E/S simulados
- Interfaz gráfica (GUI) con Tkinter
- Pruebas unitarias con `unittest`

---

## Estructura del Proyecto

proyecto_arquitectura/  
├── cpu/  
│ ├── isa.py # Definición de instrucciones   
│ └── pipeline.py # Implementación de etapas del pipeline   
├── memory/  
│ └── cache.py # Lógica de la caché  
├── io_devices/  
│ ├── devices.py # Dispositivos simulados (teclado, pantalla)  
│ └── interrupt_handler.py # Manejador de interrupciones    
├── gui/  
│ └── gui.py # Interfaz gráfica con Tkinter  
├── tests/  
│ ├── test_cpu.py # Pruebas para el pipeline  
│ ├── test_memory.py # Pruebas para la caché  
│ └── test_io.py # Pruebas para E/S e interrupciones  
├── main.py # Simulación principal por consola  
├── .gitignore # Archivos ignorados por Git  
└── README.md # Este archivo  

## Ejecución

```bash
python gui.py
```
