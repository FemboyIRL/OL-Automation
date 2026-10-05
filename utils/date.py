import re
from datetime import datetime


def format_injury_dates(injury_dates: str | None) -> str:
    if not injury_dates:
        return "+"

    # Buscar todas las fechas con año de 2 o 4 dígitos
    pattern = r"\b\d{1,2}/\d{1,2}/(?:\d{2}|\d{4})\b"

    matches = re.findall(pattern, injury_dates)

    if not matches:
        return "+"

    formatted_dates = []

    for part in matches:
        fecha = None

        # Intentar primero con año de 4 dígitos y luego con 2
        for date_format in ("%m/%d/%Y", "%m/%d/%y"):
            try:
                fecha = datetime.strptime(part, date_format).date()
                break
            except ValueError:
                continue

        if fecha is None:
            continue

        formatted_dates.append(f"{fecha.strftime('%B')} {fecha.day}, {fecha.year}")

    if not formatted_dates:
        return "+"

    # Eliminar fechas duplicadas, conservando el orden
    formatted_dates = list(dict.fromkeys(formatted_dates))

    if len(formatted_dates) == 2:
        return f"{formatted_dates[0]} to {formatted_dates[1]}"

    return ", ".join(formatted_dates)
