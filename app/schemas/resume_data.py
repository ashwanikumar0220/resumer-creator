from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List


class ResumeBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class PersonalDetails(ResumeBaseModel):
    full_name: str = Field(default="", max_length=120)
    job_title: str = Field(default="", max_length=160)
    email: str = Field(default="", max_length=254)
    phone: str = Field(default="", max_length=40)
    location: str = Field(default="", max_length=180)
    website: str = Field(default="", max_length=500)
    linkedin: str = Field(default="", max_length=500)
    summary: str = Field(default="", max_length=5000)


class EducationItem(ResumeBaseModel):
    id: str = Field(default="", max_length=80)
    institution: str = Field(default="", max_length=200)
    degree: str = Field(default="", max_length=160)
    field_of_study: str = Field(default="", max_length=160)
    start_date: str = Field(default="", max_length=50)
    end_date: str = Field(default="", max_length=50)
    grade: str = Field(default="", max_length=80)
    description: str = Field(default="", max_length=3000)


class ExperienceItem(ResumeBaseModel):
    id: str = Field(default="", max_length=80)
    company: str = Field(default="", max_length=200)
    position: str = Field(default="", max_length=160)
    location: str = Field(default="", max_length=180)
    start_date: str = Field(default="", max_length=50)
    end_date: str = Field(default="", max_length=50)
    description: str = Field(default="", max_length=5000)


class ProjectItem(ResumeBaseModel):
    id: str = Field(default="", max_length=80)
    name: str = Field(default="", max_length=180)
    technologies: str = Field(default="", max_length=500)
    link: str = Field(default="", max_length=500)
    description: str = Field(default="", max_length=4000)


class CertificationItem(ResumeBaseModel):
    id: str = Field(default="", max_length=80)
    name: str = Field(default="", max_length=200)
    issuer: str = Field(default="", max_length=180)
    date: str = Field(default="", max_length=50)


class CustomSection(ResumeBaseModel):
    id: str = Field(default="", max_length=80)
    title: str = Field(default="", max_length=120)
    content: str = Field(default="", max_length=6000)


class ResumeData(ResumeBaseModel):
    personal: PersonalDetails = Field(default_factory=PersonalDetails)
    education: List[EducationItem] = Field(default_factory=list, max_length=30)
    experience: List[ExperienceItem] = Field(default_factory=list, max_length=30)
    projects: List[ProjectItem] = Field(default_factory=list, max_length=30)
    skills: List[str] = Field(default_factory=list, max_length=100)
    certifications: List[CertificationItem] = Field(default_factory=list, max_length=30)
    languages: List[str] = Field(default_factory=list, max_length=50)
    achievements: List[str] = Field(default_factory=list, max_length=50)
    custom_sections: List[CustomSection] = Field(default_factory=list, max_length=20)

    @field_validator("skills", "languages", "achievements")
    @classmethod
    def clean_string_lists(cls, values):
        return [str(value).strip()[:500] for value in values if str(value).strip()]
