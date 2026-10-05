from datetime import date, datetime

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTFigure, LTChar

from models.models import Address, Applicant, Attorney, AttorneyType

FIELDS = {
    # --- APPLICANT ---
    "doctor_name": (76.32, 566.4, 543.36, 557.16),
    "first_name": (96.84, 246.96, 500.88, 514.8),
    "last_name": (449.64, 566.28, 500.88, 514.8),
    "date_of_birth": (67.8, 246.96, 486.0, 499.8),
    "address": (82.2, 291.12, 471.24, 484.92),
    "city": (320.04, 408.84, 471.24, 484.92),
    "state": (441.24, 476.28, 471.24, 484.92),
    "zip_code": (501.48, 566.28, 471.24, 484.92),
    "injury_dates": (119.28, 299.04, 426.6, 440.4),
    "wcab_number": (156.24, 566.28, 381.96, 395.76),
    "claim_number": (81.48, 566.28, 367.08, 380.88),
    "evaluation_type": (121.8, 558.24, 246.96, 571.92),
    "language": (301.68, 566.28, 352.2, 366.0),
    # --- APPLICANT ATTORNEY ---
    "applicant_attorney_firm_name": (67.92, 246.96, 319.56, 333.36),
    "applicant_attorney_name": (283.08, 566.28, 319.56, 333.36),
    "applicant_attorney_address": (82.2, 291.12, 304.68, 318.48),
    "applicant_attorney_city": (320.04, 408.84, 304.68, 318.48),
    "applicant_attorney_state": (441.24, 476.28, 304.68, 318.48),
    "applicant_attorney_zip_code": (501.48, 566.28, 304.68, 318.48),
    "applicant_attorney_phone": (92.52, 246.96, 289.8, 303.6),
    # --- DEFENSE ATTORNEY ---
    "defense_attorney_firm_name": (68.28, 246.96, 243.72, 256.08),
    "defense_attorney_name": (283.08, 566.28, 243.72, 256.08),
    "defense_attorney_address": (82.2, 291.12, 228.84, 242.64),
    "defense_attorney_city": (320.04, 408.84, 228.84, 242.64),
    "defense_attorney_state": (441.24, 476.28, 228.84, 242.64),
    "defense_attorney_zip_code": (501.48, 566.28, 228.84, 242.64),
    "defense_attorney_phone": (92.88, 246.96, 214.08, 227.76),
    # --- EMPLOYER INFO ---
    "employer": (90.48, 566.28, 166.44, 180.24),
    # --- INSURANCE COMPANY ---
    "insurance_company_name": (139.56, 566.28, 118.92, 132.72),
    "insurance_adjuster_name": (86.16, 299.04, 104.04, 117.84),
    "insurance_address": (82.2, 291.12, 89.28, 102.96),
    "insurance_city": (320.04, 408.84, 89.28, 102.96),
    "insurance_state": (441.24, 476.28, 89.28, 102.96),
    "insurance_zip_code": (501.48, 566.28, 89.28, 102.96),
    "insurance_phone": (92.88, 390.12, 74.4, 88.2),
}


def obtener_texto_figure(figure):
    caracteres = []

    for elemento in figure:
        if isinstance(elemento, LTChar):
            caracteres.append(elemento.get_text())

    return "".join(caracteres).strip()


def extraer_elementos(pdf_path):
    elementos = []

    for page in extract_pages(pdf_path):

        for elemento in page:

            if not isinstance(elemento, LTFigure):
                continue

            texto = obtener_texto_figure(elemento)

            if not texto:
                continue

            x0, y0, x1, y1 = elemento.bbox

            elementos.append(
                {
                    "text": texto,
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1,
                }
            )

    return elementos


def buscar_por_posicion(elementos, x_min, x_max, y_min, y_max):
    for elemento in elementos:
        if x_min <= elemento["x0"] <= x_max and y_min <= elemento["y0"] <= y_max:
            return elemento["text"]

    return None


def obtener_campo(elementos, nombre):
    x_min, x_max, y_min, y_max = FIELDS[nombre]

    return buscar_por_posicion(
        elementos,
        x_min,
        x_max,
        y_min,
        y_max,
    )


def convertir_fecha(fecha: str) -> date | None:
    if fecha is None:
        return None

    return datetime.strptime(
        fecha,
        "%m/%d/%y",
    ).date()


def crear_applicant(elementos) -> Applicant:

    # --- APPLICANT ATTORNEY ---
    applicant_attorney = Attorney(
        name=obtener_campo(elementos, "applicant_attorney_name"),
        company_name=obtener_campo(elementos, "applicant_attorney_firm_name"),
        address=Address(
            street=obtener_campo(elementos, "applicant_attorney_address"),
            city=obtener_campo(elementos, "applicant_attorney_city"),
            state=obtener_campo(elementos, "applicant_attorney_state"),
            zip_code=obtener_campo(elementos, "applicant_attorney_zip_code"),
        ),
        type=AttorneyType.APPLICANT,
    )

    # --- DEFENSE ATTORNEY ---
    defense_attorney = Attorney(
        name=obtener_campo(elementos, "defense_attorney_name"),
        company_name=obtener_campo(elementos, "defense_attorney_firm_name"),
        address=Address(
            street=obtener_campo(elementos, "defense_attorney_address"),
            city=obtener_campo(elementos, "defense_attorney_city"),
            state=obtener_campo(elementos, "defense_attorney_state"),
            zip_code=obtener_campo(elementos, "defense_attorney_zip_code"),
        ),
        type=AttorneyType.DEFENDANT,
    )

    # --- INSURANCE COMPANY ---
    insurance_company = Attorney(
        name=obtener_campo(elementos, "insurance_adjuster_name"),
        company_name=obtener_campo(elementos, "insurance_company_name"),
        address=Address(
            street=obtener_campo(elementos, "insurance_address"),
            city=obtener_campo(elementos, "insurance_city"),
            state=obtener_campo(elementos, "insurance_state"),
            zip_code=obtener_campo(elementos, "insurance_zip_code"),
        ),
        type=AttorneyType.INSURANCE_COMPANY,
    )

    return Applicant(
        first_name=obtener_campo(
            elementos,
            "first_name",
        ),
        last_name=obtener_campo(
            elementos,
            "last_name",
        ),
        evaluation_type=obtener_campo(
            elementos,
            "evaluation_type",
        ),
        evaluation_date=None,
        doctor_name=obtener_campo(
            elementos,
            "doctor_name",
        ),
        phone=None,
        language=obtener_campo(
            elementos,
            "language",
        ),
        date_of_birth=convertir_fecha(
            obtener_campo(
                elementos,
                "date_of_birth",
            )
        ),
        injury_dates=obtener_campo(
            elementos,
            "injury_dates",
        ),
        wcab_number=obtener_campo(
            elementos,
            "wcab_number",
        ),
        claim_number=obtener_campo(
            elementos,
            "claim_number",
        ),
        employer=obtener_campo(
            elementos,
            "employer",
        ),
        residence=obtener_campo(
            elementos,
            "city",
        ),
        attorneys=[
            applicant_attorney,
            defense_attorney,
            insurance_company,
        ],
    )
