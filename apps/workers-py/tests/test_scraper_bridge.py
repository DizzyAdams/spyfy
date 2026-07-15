import pytest
from spyfy.scraper_bridge import mine, _process_with_rag, _is_placeholder
from spyfy.agents.memory import OfferMemory

def test_is_placeholder():
    assert _is_placeholder("") is True
    assert _is_placeholder(None) is True
    assert _is_placeholder("/videos/fitness.mp4") is True
    assert _is_placeholder("https://cdn.com/real_video.mp4") is False

def test_scraper_bridge_rag_enrichment():
    # Use a clean test-specific OfferMemory collection
    mem = OfferMemory(collection_name="test_scraper_bridge_offers")
    
    # 1. We create a "real" retrieved offer with actual CDN media URLs
    real_offer = {
        "id": "real_offer_123",
        "headline": "Super Secret Diet Protocol for losing fat fast",
        "niche": "keto",
        "network": "meta",
        "advertiser": "HealthBR",
        "image": "https://cdn.com/real_image.jpg",
        "thumb": "https://cdn.com/real_image.jpg",
        "videoUrl": "https://cdn.com/real_video.mp4",
        "format": "video",
        "winningScore": 95.0,
    }
    
    # Add the real offer to memory
    mem.add_offers([real_offer])
    
    # 2. We retrieve a "synthetic" offer that has similar text but placeholder media URLs
    synthetic_offer = {
        "id": "synthetic_offer_456",
        "headline": "Super Secret Diet Protocol for losing fat fast",
        "niche": "keto",
        "network": "meta",
        "advertiser": "HealthBR",
        "image": "/images/placeholder.jpg",
        "thumb": "/images/placeholder.jpg",
        "videoUrl": "/videos/fitness.mp4",
        "format": "video",
        "winningScore": 90.0,
    }
    
    # Process the synthetic offer with RAG
    # We mock _SCRAPER_MEMORY in the bridge to point to our test-specific memory
    import spyfy.scraper_bridge as sb
    original_mem = sb._SCRAPER_MEMORY
    try:
        sb._SCRAPER_MEMORY = mem
        processed = _process_with_rag([synthetic_offer])
        
        # Verify it got enriched with the real media URLs!
        enriched = processed[0]
        assert enriched["videoUrl"] == "https://cdn.com/real_video.mp4"
        assert enriched["image"] == "https://cdn.com/real_image.jpg"
        assert enriched["thumb"] == "https://cdn.com/real_image.jpg"
    finally:
        sb._SCRAPER_MEMORY = original_mem

def test_mine_simulate_always_caches():
    # Verify mine(simulate=True) runs successfully and caches the synthetic offers
    import spyfy.scraper_bridge as sb
    mem = OfferMemory(collection_name="test_mine_simulate")
    original_mem = sb._SCRAPER_MEMORY
    try:
        sb._SCRAPER_MEMORY = mem
        offers = mine(niche="keto", network="meta", count=2, simulate=True)
        assert len(offers) == 2
        # Check that the memory cache now contains these offers
        assert mem.count() == 2
    finally:
        sb._SCRAPER_MEMORY = original_mem
