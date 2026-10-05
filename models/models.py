from dataclasses import dataclass
from datetime import date
from enum import Enum

from utils.date import format_injury_dates


class AttorneyType(Enum):
    APPLICANT = "Applicant"
    DEFENDANT = "Defendant"
    INSURANCE_COMPANY = "Insurance Company"


@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str

    def __str__(self) -> str:
        return f"{self.street},\n{self.city},{self.state} {self.zip_code}"


@dataclass
class Attorney:
    name: str
    company_name: str
    address: Address
    type: AttorneyType

    def __str__(self):
        return f"{self.name},\n{self.company_name},\n{self.address}"


from dataclasses import dataclass, field
from datetime import date


@dataclass
class Applicant:
    first_name: str
    last_name: str
    evaluation_type: str | None
    evaluation_date: date
    doctor_name: str
    phone: str
    language: str

    date_of_birth: date
    injury_dates: str
    wcab_number: str
    claim_number: str
    employer: str
    residence: str

    attorneys: list[Attorney] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int | None:
        if self.date_of_birth is None:
            return None

        today = self.evaluation_date or date.today()

        age = today.year - self.date_of_birth.year

        if (today.month, today.day) < (
            self.date_of_birth.month,
            self.date_of_birth.day,
        ):
            age -= 1

        return age

    @property
    def folder_name(self) -> str:
        phone = self.phone or ""
        return f"{self.full_name} {phone} {self.language}"

    @property
    def file_name(self) -> str:
        return f"{self.last_name}.{self.first_name}-{self.evaluation_type}-History-{self.evaluation_date}-{self.doctor_name}.docx"

    @property
    def text_message_to_applicant(self) -> str:
        evaluation_date = (
            f"{self.evaluation_date.strftime('%B')} "
            f"{self.evaluation_date.day}, "
            f"{self.evaluation_date.year}"
            if self.evaluation_date
            else "+"
        )

        if self.language == "Spanish":
            return (
                f"Este mensaje es para {self.full_name}. "
                f"Soy Luis por parte del consultorio de {self.doctor_name}. "
                f"Le hemos programado una evaluación ortopédica para el "
                f"{evaluation_date} en relación con "
                f"su reclamación por lesión laboral. Necesitamos obtener su "
                f"historial médico antes de su visita. Es una entrevista "
                f"telefónica que dura entre 30 minutos y una hora. Por favor, "
                f"responda a este mensaje de texto para avisarme cuándo puedo "
                f"llamarle para la entrevista. Gracias."
            )

        else:
            return (
                f"This message is for {self.full_name}. "
                f"I am Luis from Dr. {self.doctor_name}'s office. "
                f"We have scheduled you for an orthopedic evaluation on "
                f"{evaluation_date} regarding your workers' compensation claim. "
                f"We need to obtain your medical history before your visit. "
                f"This is a telephone interview that takes approximately "
                f"30 minutes to one hour. Please reply to this text message "
                f"to let me know when I can call you for the interview. "
                f"Thank you."
            )

    @property
    def applicant_attorney(self) -> Attorney | None:
        return next(
            (
                attorney
                for attorney in self.attorneys
                if attorney.type == AttorneyType.APPLICANT
            ),
            None,
        )

    @property
    def defendant_attorney(self) -> Attorney | None:
        return next(
            (
                attorney
                for attorney in self.attorneys
                if attorney.type == AttorneyType.DEFENDANT
            ),
            None,
        )

    @property
    def insurance_company(self) -> Attorney | None:
        return next(
            (
                attorney
                for attorney in self.attorneys
                if attorney.type == AttorneyType.INSURANCE_COMPANY
            ),
            None,
        )

    @property
    def case_information(self) -> str:
        evaluation_date = (
            f"{self.evaluation_date.strftime('%B')} "
            f"{self.evaluation_date.day}, "
            f"{self.evaluation_date.year}"
            if self.evaluation_date
            else "+"
        )

        date_of_birth = (
            self.date_of_birth.strftime("%m/%d/%Y") if self.date_of_birth else "+"
        )

        return (
            f"Re: {self.full_name.upper()}\n"
            f"Employer: {self.employer}\n"
            f"WCAB No.: {self.wcab_number}\n"
            f"Applicant DOB: {date_of_birth}\n"
            f"Dates/Dates of Injury: {self.injury_dates}\n"
            f"Claim/File No.: {self.claim_number}\n"
            f"Date of Evaluation: {evaluation_date}"
        )

    @property
    def applicant_description(self) -> str:
        age = self.age if self.age is not None else "+"

        # gender = self.gender or "+"

        residence = self.residence or "+"

        if self.date_of_birth:
            date_of_birth = self.date_of_birth.strftime("%B %d, %Y")
            date_of_birth = date_of_birth.replace(
                f" {self.date_of_birth.day:02d},",
                f" {self.date_of_birth.day},",
            )
        else:
            date_of_birth = "+"

        injury_dates = format_injury_dates(self.injury_dates)

        employer = self.employer or "+"

        pronoun_subject = "He/She"
        pronoun_possessive = "his/her"

        # if gender.lower() == "woman":
        #     pronoun_subject = "She"
        #     pronoun_possessive = "her"
        # else:
        #     pronoun_subject = "He"
        #     pronoun_possessive = "his"

        return (
            f"Mr./Ms. {self.last_name} is a {age}-year-old "
            f"+-hand dominant +Caucasian/African American/Hispanic/Asian man/woman "
            f"who resides in {residence}, California. "
            f"{pronoun_possessive} date of birth is {date_of_birth}. "
            f"{pronoun_subject} is evaluated today pursuant to a claim of "
            f"(specific injury / cumulative trauma) on {injury_dates}, involving "
            f"{pronoun_possessive} +, while {pronoun_subject.lower()} "
            f"was working for {employer} as a +."
        )
