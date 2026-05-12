from app.auth.forms import clean_text


def clean_search_args(args):
    return {
        "q": clean_text(args.get("q"), 80),
        "location": clean_text(args.get("location"), 80),
        "property_type": clean_text(args.get("property_type"), 30),
        "min_price": args.get("min_price", type=int),
        "max_price": args.get("max_price", type=int),
        "bedrooms": args.get("bedrooms", type=int),
        "amenities": clean_text(args.get("amenities"), 120),
        "status": clean_text(args.get("status"), 30),
        "premium": args.get("premium") == "1",
        "sort": clean_text(args.get("sort") or "newest", 30),
        "page": max(args.get("page", 1, type=int), 1),
    }
