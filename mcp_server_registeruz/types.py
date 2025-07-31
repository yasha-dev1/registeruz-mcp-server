"""Type definitions for RegisterUZ API responses and requests."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Types of entities in RegisterUZ."""
    
    UCTOVNE_JEDNOTKY = "uctovne-jednotky"
    UCTOVNE_ZAVIERKY = "uctovne-zavierky"
    UCTOVNE_VYKAZY = "uctovne-vykazy"
    VYROCNE_SPRAVY = "vyrocne-spravy"


class LegalForm(str, Enum):
    """Common legal forms in Slovakia."""
    
    SRO = "112"  # s.r.o. - Limited liability company
    AS = "121"   # a.s. - Joint stock company
    KS = "113"   # k.s. - Limited partnership
    VS = "111"   # v.o.s. - General partnership
    SE = "301"   # SE - European company
    DRUZSTVO = "221"  # Družstvo - Cooperative
    
    @classmethod
    def from_string(cls, value: str) -> Optional["LegalForm"]:
        """Convert string to LegalForm enum if possible."""
        for form in cls:
            if form.value == value:
                return form
        return None


class BaseSearchParams(BaseModel):
    """Base parameters for search endpoints."""
    
    zmenene_od: str = Field(
        ...,
        description="Date from which to retrieve changed records (YYYY-MM-DD or YYYY-MM-DD'T'hh:mm:ssZ)"
    )
    pokracovat_za_id: Optional[int] = Field(
        None,
        description="Continue pagination after this ID"
    )
    max_zaznamov: Optional[int] = Field(
        None,
        ge=1,
        le=10000,
        description="Maximum number of records to return (default 1000, max 10000)"
    )


class AccountingEntitySearchParams(BaseSearchParams):
    """Parameters specific to accounting entity search."""
    
    ico: Optional[str] = Field(
        None,
        description="Company identification number (IČO)"
    )
    dic: Optional[str] = Field(
        None,
        description="Tax identification number (DIČ)"
    )
    pravna_forma: Optional[Union[str, LegalForm]] = Field(
        None,
        description="Legal form code"
    )


class ApiResponse(BaseModel):
    """Standard API response structure."""
    
    id: List[int] = Field(
        default_factory=list,
        description="List of entity identifiers"
    )
    existujeDalsieId: bool = Field(
        default=False,
        description="Whether more records exist for pagination"
    )


class RemainingCountResponse(BaseModel):
    """Response for remaining ID count endpoint."""
    
    pocet: int = Field(
        ...,
        description="Number of remaining IDs"
    )


class Template(BaseModel):
    """Report template structure."""
    
    id: int = Field(..., description="Template ID")
    nazov: Optional[str] = Field(None, description="Template name")
    tabulky: Optional[List[dict]] = Field(None, description="Tables data")
    nariadenieMF: Optional[str] = Field(None, description="Ministry of Finance regulation")


class TemplatesResponse(BaseModel):
    """Response for templates endpoint."""
    
    sablony: List[Template] = Field(
        default_factory=list,
        description="List of report templates"
    )


class Address(BaseModel):
    """Address structure."""
    
    ulica: Optional[str] = Field(None, description="Street")
    cislo: Optional[str] = Field(None, description="Number")
    psc: Optional[str] = Field(None, description="Postal code")
    mesto: Optional[str] = Field(None, description="City")


class AccountingEntityDetail(BaseModel):
    """Detailed accounting entity information."""
    
    id: int = Field(..., description="Entity ID")
    ico: Optional[str] = Field(None, description="Company identification number (IČO)")
    dic: Optional[str] = Field(None, description="Tax identification number (DIČ)")
    sid: Optional[str] = Field(None, description="SID")
    nazovUJ: Optional[str] = Field(None, description="Entity name")
    mesto: Optional[str] = Field(None, description="City")
    ulica: Optional[str] = Field(None, description="Street with number")
    psc: Optional[str] = Field(None, description="Postal code")
    datumZalozenia: Optional[str] = Field(None, description="Founding date (YYYY-MM-DD)")
    datumZrusenia: Optional[str] = Field(None, description="Dissolution date (YYYY-MM-DD)")
    pravnaForma: Optional[str] = Field(None, description="Legal form code")
    skNace: Optional[str] = Field(None, description="SK NACE classification code")
    velkostOrganizacie: Optional[str] = Field(None, description="Organization size category code")
    druhVlastnictva: Optional[str] = Field(None, description="Ownership type code")
    kraj: Optional[str] = Field(None, description="Region code")
    okres: Optional[str] = Field(None, description="District code")
    sidlo: Optional[str] = Field(None, description="Municipality code")
    konsolidovana: Optional[bool] = Field(None, description="Has consolidated financial statements")
    idUctovnychZavierok: Optional[List[int]] = Field(None, description="List of financial statement IDs")
    idVyrocnychSprav: Optional[List[int]] = Field(None, description="List of annual report IDs")
    zdrojDat: Optional[str] = Field(None, description="Data source")
    datumPoslednejUpravy: Optional[str] = Field(None, description="Last update date (YYYY-MM-DD)")


class FinancialStatementDetail(BaseModel):
    """Detailed financial statement information."""
    
    id: int = Field(..., description="Statement ID")
    obdobieOd: Optional[str] = Field(None, description="Period from (YYYY-MM)")
    obdobieDo: Optional[str] = Field(None, description="Period to (YYYY-MM)")
    datumPodania: Optional[str] = Field(None, description="Submission date (YYYY-MM-DD)")
    datumZostavenia: Optional[str] = Field(None, description="Compilation date (YYYY-MM-DD)")
    datumSchvalenia: Optional[str] = Field(None, description="Approval date (YYYY-MM-DD)")
    datumZostaveniaK: Optional[str] = Field(None, description="Compiled as of date (YYYY-MM-DD)")
    datumPrilozeniaSpravyAuditora: Optional[str] = Field(None, description="Auditor report attachment date (YYYY-MM-DD)")
    nazovFondu: Optional[str] = Field(None, description="Fund name")
    leiKod: Optional[str] = Field(None, description="LEI code")
    idUJ: Optional[int] = Field(None, description="Accounting entity ID")
    konsolidovana: Optional[bool] = Field(None, description="Is consolidated")
    konsolidovanaZavierkaUstrednejStatnejSpravy: Optional[bool] = Field(None, description="Is central government consolidated")
    suhrnnaUctovnaZavierkaVerejnejSpravy: Optional[bool] = Field(None, description="Is public administration summary")
    typ: Optional[str] = Field(None, description="Type (Riadna/Mimoriadna/Priebežná/Kombinovaná)")
    idUctovnychVykazov: Optional[List[int]] = Field(None, description="List of financial report IDs")
    zdrojDat: Optional[str] = Field(None, description="Data source")
    datumPoslednejUpravy: Optional[str] = Field(None, description="Last update date (YYYY-MM-DD)")


class Attachment(BaseModel):
    """Attachment information."""
    
    id: int = Field(..., description="Attachment ID")
    meno: Optional[str] = Field(None, description="File name")
    mimeType: Optional[str] = Field(None, description="MIME type")
    velkostPrilohy: Optional[int] = Field(None, description="File size")
    pocetStran: Optional[int] = Field(None, description="Page count")
    digest: Optional[str] = Field(None, description="SHA-256 hash")
    jazyk: Optional[str] = Field(None, description="Language")


class TitlePage(BaseModel):
    """Title page of financial report."""
    
    nazovUctovnejJednotky: Optional[str] = Field(None, description="Entity name")
    ico: Optional[str] = Field(None, description="IČO")
    dic: Optional[str] = Field(None, description="DIČ")
    sid: Optional[str] = Field(None, description="SID")
    adresa: Optional[Address] = Field(None, description="Address")
    miestoPodnikania: Optional[Address] = Field(None, description="Business location")
    pravnaForma: Optional[str] = Field(None, description="Legal form code")
    skNace: Optional[str] = Field(None, description="SK NACE code")
    typZavierky: Optional[str] = Field(None, description="Statement type")
    konsolidovana: Optional[bool] = Field(None, description="Is consolidated")
    konsolidovanaZavierkaUstrednejStatnejSpravy: Optional[bool] = Field(None, description="Is central government consolidated")
    suhrnnaUctovnaZavierkaVerejnejSpravy: Optional[bool] = Field(None, description="Is public administration summary")
    typUctovnejJednotky: Optional[str] = Field(None, description="Entity type (malá/veľká)")
    oznacenieObchodnehoRegistra: Optional[str] = Field(None, description="Commercial register designation")
    nazovSpravcovskehoFondu: Optional[str] = Field(None, description="Management company/fund name")
    leiKod: Optional[str] = Field(None, description="LEI code")
    obdobieOd: Optional[str] = Field(None, description="Period from (YYYY-MM)")
    obdobieDo: Optional[str] = Field(None, description="Period to (YYYY-MM)")
    predchadzajuceObdobieOd: Optional[str] = Field(None, description="Previous period from (YYYY-MM)")
    predchadzajuceObdobieDo: Optional[str] = Field(None, description="Previous period to (YYYY-MM)")
    datumVyplnenia: Optional[str] = Field(None, description="Fill date (YYYY-MM-DD)")
    datumSchvalenia: Optional[str] = Field(None, description="Approval date (YYYY-MM-DD)")
    datumZostavenia: Optional[str] = Field(None, description="Compilation date (YYYY-MM-DD)")
    datumZostaveniaK: Optional[str] = Field(None, description="Compiled as of date (YYYY-MM-DD)")
    datumPrilozeniaSpravyAuditora: Optional[str] = Field(None, description="Auditor report attachment date (YYYY-MM-DD)")


class Table(BaseModel):
    """Financial report table."""
    
    nazov: Optional[Dict[str, str]] = Field(None, description="Table name (localized)")
    data: Optional[List[str]] = Field(None, description="Table data")


class ReportContent(BaseModel):
    """Financial report content."""
    
    titulnaStrana: Optional[TitlePage] = Field(None, description="Title page")
    tabulky: Optional[List[Table]] = Field(None, description="Tables")


class FinancialReportDetail(BaseModel):
    """Detailed financial report information."""
    
    id: int = Field(..., description="Report ID")
    idUctovnejZavierky: Optional[int] = Field(None, description="Financial statement ID")
    idVyrocnejSpravy: Optional[int] = Field(None, description="Annual report ID")
    idSablony: Optional[int] = Field(None, description="Template ID")
    mena: Optional[str] = Field(None, description="Currency")
    kodDanovehoUradu: Optional[str] = Field(None, description="Tax office code")
    pristupnostDat: Optional[str] = Field(None, description="Data accessibility (Verejné/Verejné prílohy/Neverejné)")
    prilohy: Optional[List[Attachment]] = Field(None, description="Attachments")
    obsah: Optional[ReportContent] = Field(None, description="Report content")
    zdrojDat: Optional[str] = Field(None, description="Data source")
    datumPoslednejUpravy: Optional[str] = Field(None, description="Last update date (YYYY-MM-DD)")


class AnnualReportDetail(BaseModel):
    """Detailed annual report information."""
    
    id: int = Field(..., description="Report ID")
    nazovUJ: Optional[str] = Field(None, description="Entity name at submission time")
    typ: Optional[str] = Field(None, description="Report type")
    nazovFondu: Optional[str] = Field(None, description="Fund name")
    leiKod: Optional[str] = Field(None, description="LEI code")
    obdobieOd: Optional[str] = Field(None, description="Period from (YYYY-MM)")
    obdobieDo: Optional[str] = Field(None, description="Period to (YYYY-MM)")
    datumPodania: Optional[str] = Field(None, description="Submission date (YYYY-MM-DD)")
    datumZostaveniaK: Optional[str] = Field(None, description="Compiled as of date (YYYY-MM-DD)")
    pristupnostDat: Optional[str] = Field(None, description="Data accessibility (Verejné/Neverejné)")
    prilohy: Optional[List[Attachment]] = Field(None, description="Attachments")
    idUctovnychVykazov: Optional[List[int]] = Field(None, description="List of financial report IDs")
    idUJ: Optional[int] = Field(None, description="Accounting entity ID")
    zdrojDat: Optional[str] = Field(None, description="Data source")
    datumPoslednejUpravy: Optional[str] = Field(None, description="Last update date (YYYY-MM-DD)")


class AccountingEntity(BaseModel):
    """Accounting entity details."""
    
    id: int = Field(..., description="Entity ID")
    ico: Optional[str] = Field(None, description="Company identification number")
    dic: Optional[str] = Field(None, description="Tax identification number")
    nazov: str = Field(..., description="Entity name")
    pravna_forma: Optional[str] = Field(None, description="Legal form code")
    
    @property
    def legal_form_enum(self) -> Optional[LegalForm]:
        """Get legal form as enum if possible."""
        if self.pravna_forma:
            return LegalForm.from_string(self.pravna_forma)
        return None


class FinancialStatement(BaseModel):
    """Financial statement details."""
    
    id: int = Field(..., description="Statement ID")
    uctovna_jednotka_id: int = Field(..., description="Accounting entity ID")
    obdobie_od: str = Field(..., description="Period from")
    obdobie_do: str = Field(..., description="Period to")
    typ: str = Field(..., description="Statement type")
    vytvorene: datetime = Field(..., description="Created date")
    zmenene: datetime = Field(..., description="Modified date")


class FinancialReport(BaseModel):
    """Financial report details."""
    
    id: int = Field(..., description="Report ID")
    uctovna_zavierka_id: int = Field(..., description="Financial statement ID")
    typ_vykazu: str = Field(..., description="Report type")
    vytvorene: datetime = Field(..., description="Created date")
    zmenene: datetime = Field(..., description="Modified date")


class AnnualReport(BaseModel):
    """Annual report details."""
    
    id: int = Field(..., description="Report ID")
    uctovna_jednotka_id: int = Field(..., description="Accounting entity ID")
    rok: int = Field(..., description="Year")
    typ: str = Field(..., description="Report type")
    vytvorene: datetime = Field(..., description="Created date")
    zmenene: datetime = Field(..., description="Modified date")