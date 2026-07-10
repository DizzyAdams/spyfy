"""Testes dos Loops 7/8/9: Proxy Pool, CRM, Cart/Page/Garantia."""
import time
from spyfy.proxy_pool import ProxyPool, Proxy, ProxyType, Rotation
from spyfy.crm import CRM, Contact, Deal, Stage
from spyfy.cart import (AbandonedCart, CartStatus, PageRequest, build_page, evaluate_guarantee, next_reminder,
                       recover, expire)


# ---- Loop 7: Proxy Pool ----
def test_sticky_keeps_same_proxy():
    pool = ProxyPool([Proxy("http://a", ProxyType.RESIDENTIAL, "BR"),
                      Proxy("http://b", ProxyType.RESIDENTIAL, "BR")],
                     rotation=Rotation.STICKY)
    p1 = pool.get(region="BR", sticky_id="s1")
    p2 = pool.get(region="BR", sticky_id="s1")
    assert p1.url == p2.url


def test_proxy_banned_after_max_failures():
    pool = ProxyPool([Proxy("http://a")], max_failures=2)
    p = pool.get()
    pool.report(p, ok=False)
    pool.report(p, ok=False)
    assert p.banned is True
    assert pool.get() is None or pool.get().url != "http://a"


def test_region_filtering():
    pool = ProxyPool([Proxy("http://br", ProxyType.RESIDENTIAL, "BR"),
                      Proxy("http://us", ProxyType.RESIDENTIAL, "US")])
    p = pool.get(region="BR")
    assert p is None or p.region == "BR"


# ---- Loop 8: CRM ----
def test_crm_pipeline_lead_to_paying():
    crm = CRM()
    crm.upsert_contact(Contact("u1", "Ana", "ana@x.com"))
    crm.add_deal(Deal("d1", "u1", "Keto", Stage.LEAD, 0, "ofr_1"))
    crm.on_offer_found("u1", "ofr_1", "keto")
    crm.on_clone_done("u1", "ofr_1", "clone_1")
    crm.on_sale("u1", 96.0)
    assert crm.deals["d1"].stage == Stage.PAYING
    assert crm.deals["d1"].value_usd == 96.0
    assert crm.pipeline_summary()["paying"] == 1


def test_crm_winback_reactivates_churned():
    crm = CRM()
    crm.upsert_contact(Contact("u2", "Bob"))
    crm.add_deal(Deal("d2", "u2", "X", Stage.CHURNED))
    crm.winback("u2")
    assert crm.deals["d2"].stage == Stage.CONTACTED


# ---- Loop 9: Cart / Page / Garantia ----
def test_cart_reminder_after_30min():
    now = time.time()
    cart = AbandonedCart("c1", "u1", "pro", 49.0, now - 31 * 60)
    assert next_reminder(cart, now) == 0


def test_cart_recover():
    cart = AbandonedCart("c2", "u1", "pro", 49.0, time.time())
    recover(cart, time.time())
    assert cart.status == CartStatus.RECOVERED


def test_cart_expire_after_24h():
    now = time.time()
    cart = AbandonedCart("c3", "u1", "pro", 49.0, now - (25 * 3600))
    assert expire(cart, now) is True
    assert cart.status == CartStatus.EXPIRED


def test_page_built_from_brief():
    req = PageRequest("r1", "u1", "ofr_1",
                      "Lander com VSL e CTA para Keto BR")
    html = build_page(req, time.time())
    assert req.status == "delivered" and "Keto BR" in html


def test_guarantee_ok_within_sla():
    now = time.time()
    req = PageRequest("r1", "u1", "ofr_1", "brief", created_at=now - 3600)
    req.status = "delivered"
    req.delivered_at = now - 100
    g = evaluate_guarantee(req, now, 588.0)
    assert g.within_sla is True and g.refund_usd == 0


def test_guarantee_refund_year_if_late():
    now = time.time()
    late = PageRequest("r2", "u2", "ofr_2", "brief",
                       created_at=now - (25 * 3600))
    g = evaluate_guarantee(late, now, 588.0)
    assert g.within_sla is False
    assert g.refund_usd == 588.0 and g.free_months == 12


def test_guarantee_pending_still_in_time():
    now = time.time()
    pending = PageRequest("r3", "u3", "ofr_3", "brief",
                          created_at=now - 3600)   # 1h, ainda no prazo
    g = evaluate_guarantee(pending, now, 100.0)
    assert g.within_sla is True and g.refund_usd == 0
