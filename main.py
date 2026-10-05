from datetime import datetime
from pathlib import Path

from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from models.models import AttorneyType
from parser.parser import crear_applicant, extraer_elementos


def obtener_fecha_evaluacion(nombre_archivo: str) -> datetime.date:
    """Extrae la fecha de evaluación desde el nombre del PDF.

    Formato esperado: "<applicant> <algo> <doctor> <YYYY-MM-DD>.pdf"
    """
    partes = nombre_archivo.rsplit(" ", 3)
    fecha_texto = partes[3].replace(".pdf", "")
    return datetime.strptime(fecha_texto, "%Y-%m-%d").date()


def formatear_carpeta_evaluacion(fecha: datetime.date) -> str:
    """Devuelve el nombre de carpeta con formato 'Month Day, Year'."""
    return f"{fecha.strftime('%B')} {fecha.day}, {fecha.year}"


def configurar_estilo_documento(document: Document) -> None:
    """Aplica el estilo base (Times New Roman 11) al documento."""
    style = document.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    # Compatibilidad con Word
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")


def agregar_attorneys(document: Document, applicant) -> None:
    """Agrega los attorneys en el orden predefinido, si existen."""
    attorney_order = [
        AttorneyType.INSURANCE_COMPANY,
        AttorneyType.APPLICANT,
        AttorneyType.DEFENDANT,
    ]

    for attorney_type in attorney_order:
        attorney = next(
            (a for a in applicant.attorneys if a.type == attorney_type),
            None,
        )
        if attorney is None:
            continue

        document.add_paragraph(str(attorney))
        document.add_paragraph()


def crear_word(applicant, evaluation_folder: str) -> Path:
    """Crea el documento Word para un applicant y devuelve su ruta."""
    folder = Path("applicants") / evaluation_folder / applicant.folder_name
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / applicant.file_name

    document = Document()
    configurar_estilo_documento(document)

    agregar_attorneys(document, applicant)
    document.add_paragraph(applicant.case_information)
    document.add_paragraph(applicant.applicant_description)
    document.add_paragraph(applicant.text_message_to_applicant)

    document.save(file_path)
    return file_path


def cargar_applicants(templates_folder: Path) -> list:
    """Lee los PDFs de templates y construye la lista de applicants."""
    pdf_files = list(templates_folder.glob("*.pdf"))

    if not pdf_files:
        return []

    applicants = []

    for pdf_path in pdf_files:
        print(f"Procesando: {pdf_path.name}")

        elementos = extraer_elementos(pdf_path)
        applicant = crear_applicant(elementos)
        applicant.evaluation_date = obtener_fecha_evaluacion(pdf_path.name)

        applicants.append(applicant)

    return applicants


def main() -> None:
    templates_folder = Path("templates")

    applicants = cargar_applicants(templates_folder)

    if not applicants:
        print("No se encontraron demos dentro de templates")
        return

    # Ordenar por fecha de evaluación
    applicants.sort(key=lambda a: a.evaluation_date)

    for applicant in applicants:
        evaluation_folder = formatear_carpeta_evaluacion(applicant.evaluation_date)
        file_path = crear_word(applicant, evaluation_folder)
        print(f"Word creado: {file_path}")


if __name__ == "__main__":
    main()
