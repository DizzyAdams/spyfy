"""Demo do agente A13 (Alert/Notify) — SpyFy.

Mostra como o dispatcher de notificações é montado e como o endpoint
POST /v1/notify roteia notificações pelos canais conforme o plano do usuário.
NÃO envia notificações de rede (apenas inspeciona a configuração).

Rode com:  python examples/notify_demo.py   (a partir de apps/workers-py)
"""
import sys
from pathlib import Path

# garante que o pacote 'spyfy' (um diretório acima de examples/) seja importável
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spyfy.notifiers import AppriseAdapter, NotificationDispatcher
from spyfy.notifications import Channel, Priority


def main() -> None:
    dispatcher = NotificationDispatcher({"apprise": AppriseAdapter()})
    print("Backends registrados no dispatcher:", list(dispatcher.notifiers.keys()))
    print("Canais suportados pelo motor:", [c.value for c in Channel])
    print("Prioridades disponíveis:", [p.value for p in Priority])
    print(
        "POST /v1/notify roteia via resolve_channels(plano, prefs, notif, ...) "
        "e entrega em paralelo pelos adapters corretos (Apprise/Ntfy/Webhook/Novu)."
    )


if __name__ == "__main__":
    main()
