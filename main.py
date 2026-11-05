"""
Punto de entrada del proyecto.

    python main.py
"""
from gui.app import Aplicacion


def main():
    app = Aplicacion()
    app.mainloop()


if __name__ == "__main__":
    main()
