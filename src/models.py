import abc
from dataclasses import dataclass
from functools import cached_property
import uuid
import requests
from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, Union


class BaseField(BaseModel):
    key: str
    label: str
    value: Any

    def get_value(self):
        return self.value


class OptionType(BaseModel):
    id: str
    text: str
    isOtherOption: Optional[bool] = None
    optionId: Optional[str] = None


class HasOptions(BaseModel, abc.ABC):
    options: List[OptionType]

    def get_options(self) -> Dict[str, OptionType]:
        return {option.id: option for option in self.options}


class OptionsField(BaseField, HasOptions):
    value: Optional[List[str]] = None

    def get_values(self) -> List[str]:
        options = self.get_options()
        return [options[option].text for option in self.value]

    def get_first_value(self) -> Optional[str]:
        if not self.value:
            return None
        return self.get_values()[0]


class Media(BaseModel):
    id: str
    name: str
    url: str
    mimeType: str
    size: int

    def download(self) -> bytes:
        response = requests.get(self.url)
        response.raise_for_status()
        return response.content


class MediaFields(BaseField):
    value: Optional[List[Media]] = Field(default_factory=list)

    def get_urls(self) -> List[str]:
        return [media.url for media in self.value]

    def get_first_url(self) -> Optional[str]:
        return self.value[0].url if self.value else None

    def download(self) -> List[bytes]:
        return [media.download() for media in self.value]

    def download_first(self) -> Optional[bytes]:
        return self.value[0].download() if self.value else None


class InputTextField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"INPUT_TEXT")]
    value: Optional[str] = None


class InputEmailField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"INPUT_EMAIL")]
    value: Optional[EmailStr] = None


class CheckboxField(OptionsField):
    type: Annotated[str, StringConstraints(pattern=r"CHECKBOXES")]


class SingleCheckboxField(CheckboxField):
    def is_checked(self) -> Optional[bool]:
        return self.get_first_value() is not None


class CheckboxAnswerField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"CHECKBOXES")]
    value: Optional[bool] = None


class CalculatedFieldsField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"CALCULATED_FIELDS")]
    value: Optional[int | str] = None


class DropdownField(OptionsField):
    type: Annotated[str, StringConstraints(pattern=r"DROPDOWN")]


class TextAreaField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"TEXTAREA")]
    value: Optional[str] = None


class InputNumberField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"INPUT_NUMBER")]
    value: Optional[int] = None


class LinearScaleField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"LINEAR_SCALE")]
    value: Optional[int] = None


class MultipleChoiceField(OptionsField):
    type: Annotated[str, StringConstraints(pattern=r"MULTIPLE_CHOICE")]


class FileUploadField(MediaFields):
    type: Annotated[str, StringConstraints(pattern=r"FILE_UPLOAD")]


class SignatureField(MediaFields):
    type: Annotated[str, StringConstraints(pattern=r"SIGNATURE")]


class ResponseData(BaseModel):
    responseId: str
    submissionId: str
    respondentId: str
    formId: str
    formName: str
    createdAt: datetime
    fields: List[
        InputTextField
        | InputNumberField
        | InputEmailField
        | TextAreaField
        | SingleCheckboxField
        | CheckboxField
        | CheckboxAnswerField
        | CalculatedFieldsField
        | DropdownField
        | LinearScaleField
        | MultipleChoiceField
        | FileUploadField
        | SignatureField
    ]


class TallyWebhookEvent(BaseModel):
    eventId: uuid.UUID
    eventType: Annotated[str, StringConstraints(pattern=r"FORM_RESPONSE")]
    createdAt: datetime
    data: ResponseData

    def __init__(self, **data):
        super().__init__(**data)
        self._fields_dict = {field.label: field for field in self.data.fields}


class DataPerjanjianPemasaranProperti(TallyWebhookEvent):
    @cached_property
    def owner_name(self) -> Optional[str]:
        return self._fields_dict.get("owner_name").get_value()

    @cached_property
    def owner_address(self) -> Optional[str]:
        return self._fields_dict.get("owner_address").get_value()

    @cached_property
    def owner_ktp_num(self) -> Optional[str]:
        return self._fields_dict.get("owner_ktp_num").get_value()

    @cached_property
    def owner_phone_num(self) -> Optional[str]:
        return self._fields_dict.get("owner_phone_num").get_value()

    @cached_property
    def owner_email(self) -> Optional[str]:
        return self._fields_dict.get("owner_email").get_value()

    @cached_property
    def cp_is_owner(self) -> Optional[bool]:
        return self._fields_dict.get("cp_is_owner").is_checked()

    @cached_property
    def cp_name(self) -> Optional[str]:
        if self.cp_is_owner:
            return self.owner_name
        return self._fields_dict.get("cp_name").get_value()

    @cached_property
    def cp_address(self) -> Optional[str]:
        if self.cp_is_owner:
            return self.owner_address
        return self._fields_dict.get("cp_address").get_value()

    @cached_property
    def cp_ktp_num(self) -> Optional[str]:
        if self.cp_is_owner:
            return self.owner_ktp_num
        return self._fields_dict.get("cp_ktp_num").get_value()

    @cached_property
    def cp_phone_num(self) -> Optional[str]:
        if self.cp_is_owner:
            return self.owner_phone_num
        return self._fields_dict.get("cp_phone_num").get_value()

    @cached_property
    def cp_email(self) -> Optional[str]:
        if self.cp_is_owner:
            return self.owner_email
        return self._fields_dict.get("cp_email").get_value()

    @cached_property
    def transaction_type(self) -> Optional[str]:
        return self._fields_dict.get("transaction_type").get_first_value()

    @cached_property
    def property_type(self) -> Optional[str]:
        return self._fields_dict.get("property_type").get_first_value()

    @cached_property
    def property_address(self) -> Optional[str]:
        return self._fields_dict.get("property_address").get_value()

    @cached_property
    def property_land_area(self) -> Optional[int]:
        return self._fields_dict.get("property_land_area").get_value()

    @cached_property
    def property_building_area(self) -> Optional[int]:
        return self._fields_dict.get("property_building_area").get_value()

    @cached_property
    def property_floor_count(self) -> Optional[int]:
        return self._fields_dict.get("property_floor_count").get_value()

    @cached_property
    def property_bedroom(self) -> Optional[int]:
        return self._fields_dict.get("property_bedroom").get_value()

    @cached_property
    def property_helper_bedroom(self) -> Optional[int]:
        return self._fields_dict.get("property_helper_bedroom").get_value()

    @cached_property
    def property_bathroom(self) -> Optional[int]:
        return self._fields_dict.get("property_bathroom").get_value()

    @cached_property
    def property_helper_bathroom(self) -> Optional[int]:
        return self._fields_dict.get("property_helper_bathroom").get_value()

    @cached_property
    def property_garage(self) -> Optional[int]:
        return self._fields_dict.get("property_garage").get_value()

    @cached_property
    def property_facing_to(self) -> Optional[str]:
        return self._fields_dict.get("property_facing_to").get_first_value()

    @cached_property
    def property_condition(self) -> Optional[str]:
        return self._fields_dict.get("property_condition").get_value()

    @cached_property
    def property_certificate_status(self) -> Optional[str]:
        return self._fields_dict.get("property_certificate_status").get_first_value()

    @cached_property
    def property_wattage(self) -> Optional[List[str]]:
        return self._fields_dict.get("property_wattage").get_first_value()

    @cached_property
    def property_water_type(self) -> Optional[List[str]]:
        return self._fields_dict.get("property_water_type").get_first_value()

    @cached_property
    def property_air_cond_count(self) -> Optional[int]:
        return self._fields_dict.get("property_air_cond_count").get_value()

    @cached_property
    def property_phone_line_count(self) -> Optional[int]:
        return self._fields_dict.get("property_phone_line_count").get_value()

    @cached_property
    def property_furniture_completion(self) -> Optional[str]:
        return self._fields_dict.get("property_furniture_completion").get_first_value()

    @cached_property
    def property_certificate_url(self) -> Optional[str]:
        return self._fields_dict.get("property_certificate_file").get_first_url()

    @cached_property
    def property_certificate_file(self) -> Optional[bytes]:
        return self._fields_dict.get("property_certificate_file").download_first()

    @cached_property
    def owner_ktp_url(self) -> Optional[str]:
        return self._fields_dict.get("owner_ktp_file").get_first_url()

    @cached_property
    def owner_ktp_file(self) -> Optional[bytes]:
        return self._fields_dict.get("owner_ktp_file").download_first()

    @cached_property
    def property_pbb_url(self) -> Optional[str]:
        return self._fields_dict.get("property_pbb_file").get_first_url()

    @cached_property
    def property_pbb_file(self) -> Optional[bytes]:
        return self._fields_dict.get("property_pbb_file").download_first()

    @cached_property
    def property_imb_url(self) -> Optional[str]:
        return self._fields_dict.get("property_imb_file").get_first_url()

    @cached_property
    def property_imb_file(self) -> Optional[bytes]:
        return self._fields_dict.get("property_imb_file").download_first()

    @cached_property
    def price(self) -> Optional[int]:
        return self._fields_dict.get("price").get_value()

    @cached_property
    def rent_payment_frequency(self) -> Optional[int]:
        return self._fields_dict.get("rent_payment_frequency").get_value()

    @cached_property
    def additional_notes(self) -> Optional[str]:
        return self._fields_dict.get("additional_notes").get_value()

    @cached_property
    def agreement_online_marketing(self) -> Optional[bool]:
        return self._fields_dict.get("agreement_online_marketing").is_checked()

    @cached_property
    def agreement_offline_marketing(self) -> Optional[bool]:
        return self._fields_dict.get("agreement_offline_marketing").is_checked()

    @cached_property
    def success_fee(self) -> Optional[int]:
        return self._fields_dict.get("success_fee").get_value()

    @cached_property
    def signature_url(self) -> Optional[str]:
        return self._fields_dict.get("signature").get_first_url()

    @cached_property
    def signature_file(self) -> Optional[bytes]:
        return self._fields_dict.get("signature").download_first()

    def get_filename(self) -> str:
        property_address_trimmed = self.property_address.split(",")[0][:72]
        return f"Listing - {self.transaction_type} {self.property_type} {property_address_trimmed}.pdf"

    def get_form_properties(self) -> Dict[str, str]:
        return {
            "owner_name": self.owner_name,
            "owner_email": self.owner_email,
            "cp_name": self.cp_name,
            "cp_email": self.cp_email,
            "transaction_type": self.transaction_type,
            "property_type": self.property_type,
            "property_address": self.property_address,
            "created_at": self.createdAt.isoformat(),
            "response_id": self.data.responseId,
            "submission_id": self.data.submissionId,
            "respondent_id": self.data.respondentId,
            "filename": self.get_filename(),
        }
