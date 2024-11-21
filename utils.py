def TaglistParser(tags: str) -> set:
    if tags:
        return set([t.strip() for t in tags.split(",")])
    else:
        return set()
