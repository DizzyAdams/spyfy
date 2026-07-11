"""SpyFy Python workers — mining, enrichment, IA e Scale/ROI engine."""
from .roi import (AdSignals, NicheEconomics, ScoreWeights, OfferEstimate,
                  estimate_offer, rank_offers)
from .webhooks import (sign_payload, verify_webhook, parse_event, DedupStore)
from .notifications import (Channel, Priority, Notification, NotificationPrefs,
                           RouteDecision, resolve_channels, PLAN_CHANNELS,
                           PLAN_DAILY_LIMIT, CHANNEL_BACKEND)
from .notifiers import (NotificationDispatcher, DispatchReport, DeliveryResult,
                        NovuAdapter, AppriseAdapter, NtfyAdapter, WebhookAdapter)
from .channels import (EmailAdapter, SmsAdapter, MobilePushAdapter)
from .proxy_pool import (ProxyPool, Proxy, ProxyType, Rotation)
from .crm import (CRM, Contact, Deal, Stage, ActivityType)
from .cart import (AbandonedCart, CartStatus, PageRequest, PageBlock,
                 build_page, evaluate_guarantee, SLA_SECONDS)
from .events import DomainEvent, EventBus, DeadLetter, EVENT_TYPES
from .agents import NotifyAgent, EVENT_MAP
from .personalization import (Persona, UserContext, Widget, build_home_tab,
                              infer_persona)
from .retention import (UsageSnapshot, HealthResult, ChurnRisk, health_score,
                        should_trigger_winback, expansion_ready)
from .gamification import (GameState, GameEvent, apply_action, level_for,
                           register_daily_login, progress_to_next_level)
from .digest import (FeedOffer, UserFeedPrefs, rank_feed, build_digest,
                     personalized_score, optimal_send_hour)
from .radar import (RadarQuery, RadarOffer, run_radar, win_probability,
                    early_mover_bonus, radar_report, should_alert)
from .meta_library import MetaAdLibrary, MetaScrapeError
from .tiktok_library import TikTokAdLibrary, TikTokScrapeError
from .google_library import GoogleAdsTransparency, GoogleTransparencyError


__all__ = ["AdSignals", "NicheEconomics", "ScoreWeights", "OfferEstimate",
           "estimate_offer", "rank_offers",
           "sign_payload", "verify_webhook", "parse_event", "DedupStore",
           "Channel", "Priority", "Notification", "NotificationPrefs",
           "RouteDecision", "resolve_channels", "PLAN_CHANNELS",
           "PLAN_DAILY_LIMIT", "CHANNEL_BACKEND",
           "NotificationDispatcher", "DispatchReport", "DeliveryResult",
           "NovuAdapter", "AppriseAdapter", "NtfyAdapter", "WebhookAdapter",
           "EmailAdapter", "SmsAdapter", "MobilePushAdapter",
           "ProxyPool", "Proxy", "ProxyType", "Rotation",
           "CRM", "Contact", "Deal", "Stage", "ActivityType",
           "AbandonedCart", "CartStatus", "PageRequest", "PageBlock",
           "build_page", "evaluate_guarantee", "SLA_SECONDS",
           "DomainEvent", "EventBus", "DeadLetter", "EVENT_TYPES",
           "NotifyAgent", "EVENT_MAP",
           "Persona", "UserContext", "Widget", "build_home_tab", "infer_persona",
           "UsageSnapshot", "HealthResult", "ChurnRisk", "health_score",
           "should_trigger_winback", "expansion_ready",
           "GameState", "GameEvent", "apply_action", "level_for",
           "register_daily_login", "progress_to_next_level",
           "FeedOffer", "UserFeedPrefs", "personalized_score", "rank_feed",
           "build_digest", "optimal_send_hour",
           "RadarQuery", "RadarOffer", "run_radar", "win_probability",
           "MetaAdLibrary", "MetaScrapeError",
           "TikTokAdLibrary", "TikTokScrapeError",
           "GoogleAdsTransparency", "GoogleTransparencyError",

           "early_mover_bonus", "radar_report", "should_alert"]
__version__ = "0.1.0"
