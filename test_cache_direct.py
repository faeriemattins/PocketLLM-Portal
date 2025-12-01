from backend.cache_manager import cache_manager

print("Testing cache viewer...")
items = cache_manager.get_all_items()
print(f"\nTotal cache items: {len(items)}")
print("\nFirst 10 items:")
for i, item in enumerate(items[:10], 1):
    key_preview = item['key'][:60] + '...' if len(item['key']) > 60 else item['key']
    print(f"{i}. Key: {key_preview}")
    print(f"   Time: {item['store_time']}, Access Count: {item['access_count']}")
    print()
