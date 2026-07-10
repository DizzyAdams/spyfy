"""Testes do Dispatcher + adapters de notificação."""
from spyfy.notifications import (Channel, Notification, NotificationPrefs,
                                 Priority)
from spyfy.notifiers import (NotificationDispatcher, WebhookAdapter)

PREFS = NotificationPrefs(
    enabled_channels={Channel.IN_APP, Channel.EMAIL, Channel.SLACK,
                      Channel.PUSH, Channel.WEBHOOK},
)
NOTIF = Notification("evt_1", "offer.scaling", "Escalando", "Keto BR", Priority.HIGH)
RECIP = {"user_id": "u1", "email": "u@x.com",
         "apprise_urls": {"slack": "slack://T/C"},
         "ntfy_topic": "user-u1", "webhook_url": "https://hook.test"}


class FakeNotifier:
    def __init__(self, name, ok=True, fail_times=0):
        self.name = name
        self.ok = ok
        self.fail_times = fail_times
        self.calls = 0

    def send(self, channel, recipient, notif):
        self.calls += 1
        if self.fail_times >= self.calls:
            return False
        return self.ok


def _dispatcher(**notifiers):
    return NotificationDispatcher(notifiers)


def test_dispatch_delivers_to_all_routed_channels():
    d = _dispatcher(novu=FakeNotifier("novu"), apprise=FakeNotifier("apprise"),
                    postal=FakeNotifier("postal"), sms=FakeNotifier("sms"),
                    mobile=FakeNotifier("mobile"), native=FakeNotifier("native"))
    rep = d.dispatch(plan="pro", prefs=PREFS, notif=NOTIF, recipient=RECIP,
                     hour_local=14, sent_today=0)
    assert not rep.route.suppressed
    assert rep.all_ok
    assert Channel.SLACK in rep.delivered


def test_suppressed_route_no_delivery():
    d = _dispatcher(novu=FakeNotifier("novu"))
    rep = d.dispatch(plan="pro", prefs=PREFS, notif=NOTIF, recipient=RECIP,
                     hour_local=14, sent_today=0, seen_event=True)
    assert rep.route.suppressed
    assert rep.deliveries == []


def test_missing_adapter_marks_failure():
    d = _dispatcher(novu=FakeNotifier("novu"))  # sem apprise/ntfy
    rep = d.dispatch(plan="pro", prefs=PREFS, notif=NOTIF, recipient=RECIP,
                     hour_local=14, sent_today=0)
    fails = [r for r in rep.deliveries if not r.ok]
    assert any(r.error == "no_adapter" for r in fails)


def test_retry_then_success():
    flaky = FakeNotifier("novu", fail_times=1)  # falha 1x, sucede na 2a
    d = NotificationDispatcher({"novu": flaky, "apprise": FakeNotifier("apprise"),
                                "postal": FakeNotifier("postal"),
                                "sms": FakeNotifier("sms"),
                                "mobile": FakeNotifier("mobile"),
                                "native": FakeNotifier("native")}, max_retries=2)
    rep = d.dispatch(plan="pro", prefs=PREFS, notif=NOTIF, recipient=RECIP,
                     hour_local=14, sent_today=0)
    novu = [r for r in rep.deliveries if r.backend == "novu"][0]
    assert novu.ok and novu.attempts == 2


def test_retry_exhausted_fails():
    dead = FakeNotifier("ntfy", fail_times=99)
    d = NotificationDispatcher({"novu": FakeNotifier("novu"),
                                "apprise": FakeNotifier("apprise"),
                                "postal": FakeNotifier("postal"),
                                "sms": FakeNotifier("sms"),
                                "mobile": dead,
                                "native": FakeNotifier("native")}, max_retries=2)
    rep = d.dispatch(plan="pro", prefs=PREFS, notif=NOTIF, recipient=RECIP,
                     hour_local=14, sent_today=0)
    push = [r for r in rep.deliveries if r.channel == Channel.PUSH][0]
    assert not push.ok and push.attempts == 3


def test_webhook_adapter_signs(monkeypatch):
    sent = {}

    class Client:
        def post(self, url, content=None, headers=None, **kw):
            sent["headers"] = headers
            class R:
                status_code = 200
            return R()

    wh = WebhookAdapter(secret="whsec", _client=Client())
    ok = wh.send(Channel.WEBHOOK, RECIP, NOTIF)
    assert ok
    assert sent["headers"]["X-SpyFy-Signature"].startswith("sha256=")


def test_free_plan_limits_delivery_channels():
    d = _dispatcher(novu=FakeNotifier("novu"), apprise=FakeNotifier("apprise"),
                    postal=FakeNotifier("postal"), sms=FakeNotifier("sms"),
                    mobile=FakeNotifier("mobile"), native=FakeNotifier("native"))
    rep = d.dispatch(plan="free", prefs=PREFS, notif=NOTIF, recipient=RECIP,
                     hour_local=14, sent_today=0)
    assert set(rep.delivered) <= {Channel.IN_APP, Channel.EMAIL}
