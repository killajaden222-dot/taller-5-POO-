"""Punto de entrada: python main.py  (usar --vacio para iniciar sin datos de ejemplo)."""
import sys

from gestor import CentroSalud
from gui import App


def main():
    centro = CentroSalud()
    if "--vacio" not in sys.argv:
        centro.cargar_datos_demo()
    App(centro).mainloop()


if __name__ == "__main__":
    main()
