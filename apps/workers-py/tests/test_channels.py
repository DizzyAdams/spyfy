"""Testes do Loop 6: Email / SMS / Mobile Push OSS (channels.py)."""
from spyfy.notifications import Channel, NotificationPrefs, Priority
from spyfy.notifiers import NotificationDispatcher, NovuAdapter
from spyfy.channels import EmailAdapter, SmsAdapter, MobilePushAdapter
from spyfy.agents import NotifyAgent
from spyfy.events import EventBus, DomainEvent


class _Client:
    def __init__(self): self.calls = []
    def post(self, url, content=None, json=None, headers=None, **kw):
        self.calls.append({"url": url, "body": content or json, "headers": headers})

        class R:
            status_code = 200

        return R()


def test_email_adapter_posts_to_postal():
    c = _Client()
    a = EmailAdapter(base_url="https://mail.test", api_key="k", _client=c)
    ok = a.send(Channel.EMAIL, {"email": "u@x.com"}, _notif())
    assert ok and any("send/message" in x["url"] for x in c.calls)


def test_email_requires_email():
    a = EmailAdapter(_client=_Client())
    assert a.send(Channel.EMAIL, {"user_id": "u"}, _notif()) is False


def test_sms_requires_phone():
    a = SmsAdapter(_client=_Client())
    assert a.send(Channel.SMS, {"email": "u@x.com"}, _notif()) is False


def test_sms_normalizes_phone():
    c = _Client()
    a = SmsAdapter(_client=c)
    a.send(Channel.SMS, {"phone": "(11) 9555-1234"}, _notif())
    body = c.calls[0]["body"]
    assert body["to"] == "+1195551234" and len(body["text"]) <= 160


def test_mobile_ntfy_used_when_topic():
    c = _Client()
    a = MobilePushAdapter(ntfy_url="https://ntfy.test", _client=c)
    a.send(Channel.PUSH, {"ntfy_topic": "user-u1"}, _notif())
    assert any("ntfy.test/user-u1" in x["url"] for x in c.calls)


def test_mobile_fcm_when_token():
    c = _Client()
    a = MobilePushAdapter(fcm_server_key="k", _client=c)
    a.send(Channel.PUSH, {"fcm_token": "tk"}, _notif())
    assert any("fcm.googleapis.com" in x["url"] for x in c.calls)


def test_mobile_apns_stub_ok_with_token():
    a = MobilePushAdapter()
    assert a.send(Channel.PUSH, {"apns_token": "apns-1"}, _notif()) is True


def test_dispatcher_routes_email_sms_push():
    from spyfy.notifiers import NovuAdapter
    c = _Client()
    dispatcher = NotificationDispatcher({
        "novu": NovuAdapter(), "postal": EmailAdapter(_client=c),
        "sms": SmsAdapter(_client=c), "mobile": MobilePushAdapter(_client=c),
        "apprise": NovuAdapter(), "native": NovuAdapter(),
    })
    prefs = NotificationPrefs(enabled_channels={
        Channel.IN_APP, Channel.EMAIL, Channel.SMS, Channel.PUSH})
    rep = dispatcher.dispatch(
        plan="agency", prefs=prefs,
        notif=_notif("order.paid", Priority.NORMAL),
        recipient={"user_id": "u1", "email": "u@x.com", "phone": "1199999",
                   "ntfy_topic": "user-u1"}, hour_local=14, sent_today=0)
    chans = {r.channel for r in rep.deliveries}
    assert {Channel.EMAIL, Channel.SMS, Channel.PUSH} <= chans
    assert len(c.calls) >= 2     # email + sms + push posts


def test_e2e_event_to_email_sms_push():
    c = _Client()
    dispatcher = NotificationDispatcher({
        "novu": NovuAdapter(), "postal": EmailAdapter(_client=c),
        "sms": SmsAdapter(_client=c), "mobile": MobilePushAdapter(_client=c),
        "apprise": NovuAdapter(), "native": NovuAdapter(),
    })
    agent = NotifyAgent(
        dispatcher,
        resolve_recipients=lambda e: [{"user_id": "u1", "email": "u@x.com",
                                       "phone": "1195551234", "ntfy_topic": "user-u1"}],
        resolve_context=lambda uid: ("agency", NotificationPrefs(
            enabled_channels={Channel.IN_APP, Channel.EMAIL,
                                Channel.SMS, Channel.PUSH}), 0),
    )
    bus = EventBus()
    agent.register(bus)
    bus.publish(DomainEvent("e6", "order.paid", {"amount": 96}))
    assert agent.total_delivered >= 3   # in_app + email + sms + push


def _notif(type: str = "offer.scaling", prio=Priority.HIGH):
    from spyfy.notifications import Notification
    return Notification("n1", type, "Title", "Body", prio, {})
