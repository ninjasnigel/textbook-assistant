def last_index_page(book):
    start = 0
    for index, page in enumerate(reversed(book)):
        if "index" in page.extract_text().lower():
            started =+ 1
            continue
        if started:
            return len(book) - index, len(book) - started
    print("No index found")
    return 0, 0

def category_dict(book):
    import re
    categories = {}
    last_index = last_index_page(book)
    for page in book[last_index[0]:last_index[1]]:
        text = page.extract_text().lower()
        text = re.split(r'[,|\n|-]', text)
        curr_category = ""
        curr_pages = []
        last_was_category = False
        for item in text:
            item = item.strip()
            if not item or item == "index":
                continue
            if not (item.isdigit() or "–" in item):
                if last_was_category:
                    curr_category += " " + item
                    continue
                if curr_category:
                    categories[curr_category] = curr_pages
                curr_category = item
                curr_pages = []
            else:
                curr_pages.append(item)
    return fix_dict(categories)

def fix_dict(dict):
    for key, value in dict.items():
        new_value = []  # List to store new values
        for pagenr in value:
            if "–" in pagenr:  # Check for page ranges
                start, end = pagenr.split("–")
                if start.isdigit() and end.isdigit():  # Ensure they're numeric
                    new_value.extend(str(i) for i in range(int(start), int(end) + 1))
                else:  # If not numeric, append the original string
                    new_value.append(pagenr)
            else:  # If not a page range, append the original string
                new_value.append(pagenr)
        dict[key] = new_value  # Replace the value list for this key
    return dict
