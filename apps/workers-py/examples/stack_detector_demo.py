"""Exemplo: detecção de stack de uma página com spyfy.clone.detect_stack."""

import sys
from pathlib import Path

# Garante que a pasta raiz (apps/workers-py) esteja no PYTHONPATH ao rodar o script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spyfy.clone import detect_stack

# HTML de exemplo contendo Kiwify (checkout), Stripe e Meta Pixel.
HTML_EXEMPLO = """
<html>
  <head>
    <script src="https://connect.facebook.net/en_US/fbevents.js"></script>
  </head>
  <body>
    <script src="https://static.kiwify.com/checkout.js"></script>
    <script src="https://js.stripe.com/v3/"></script>
  </body>
</html>
"""

if __name__ == "__main__":
    # Detecta as plataformas presentes no HTML.
    plataformas = detect_stack(HTML_EXEMPLO)
    print("Plataformas detectadas:", plataformas)
