from math import ceil


def paginate(query, page: int, per_page: int = 10):
    """Return the current query slice and metadata used by the templates."""
    total = query.order_by(None).count()
    total_pages = max(1, ceil(total / per_page))
    current_page = min(max(page, 1), total_pages)

    items = query.offset((current_page - 1) * per_page).limit(per_page).all()

    start = max(1, current_page - 1)
    end = min(total_pages, current_page + 1)
    visible_pages = sorted({1, total_pages, *range(start, end + 1)})
    pages = []
    previous = 0
    for number in visible_pages:
        if number - previous > 1:
            pages.append(None)
        pages.append(number)
        previous = number

    return items, {
        "page": current_page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "pages": pages,
        "has_previous": current_page > 1,
        "has_next": current_page < total_pages,
    }
