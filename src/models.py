from dataclasses import dataclass
from functools import cached_property
import uuid
from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, Union


class BaseField(BaseModel):
    key: str
    label: str
    value: Any


class OptionType(BaseModel):
    id: str
    text: str
    isOtherOption: Optional[bool] = None
    optionId: Optional[str] = None


class Media(BaseModel):
    id: str
    name: str
    url: str
    mimeType: str
    size: int


class InputTextField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"INPUT_TEXT")]
    value: Optional[str] = None


class InputEmailField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"INPUT_EMAIL")]
    value: Optional[EmailStr] = None


class CheckboxField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"CHECKBOXES")]
    value: Optional[List[str]] = None
    options: List[OptionType]


class CheckboxAnswerField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"CHECKBOXES")]
    value: Optional[bool] = None


class CalculatedFieldsField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"CALCULATED_FIELDS")]
    value: Optional[int | str] = None


class DropdownField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"DROPDOWN")]
    value: Optional[List[str]] = Field(default_factory=list)
    options: List[OptionType]


class TextAreaField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"TEXTAREA")]
    value: Optional[str] = None


class InputNumberField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"INPUT_NUMBER")]
    value: Optional[int] = None


class LinearScaleField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"LINEAR_SCALE")]
    value: Optional[int] = None


class MultipleChoiceField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"MULTIPLE_CHOICE")]
    value: Optional[List[str]] = Field(default_factory=list)
    options: List[OptionType]


class FileUploadField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"FILE_UPLOAD")]
    value: Optional[List[Media]] = Field(default_factory=list)


class SignatureField(BaseField):
    type: Annotated[str, StringConstraints(pattern=r"SIGNATURE")]
    value: Optional[List[Media]] = Field(default_factory=list)


# Model for the data object
class ResponseData(BaseModel):
    responseId: str
    submissionId: str
    respondentId: str
    formId: str
    formName: str
    createdAt: datetime
    fields: List[
        InputTextField
        | InputEmailField
        | CheckboxField
        | CheckboxAnswerField
        | CalculatedFieldsField
        | DropdownField
        | TextAreaField
        | InputNumberField
        | LinearScaleField
        | MultipleChoiceField
        | FileUploadField
        | SignatureField
    ]


# Main model for the webhook event
class TallyWebhookEvent(BaseModel):
    eventId: uuid.UUID
    eventType: Annotated[str, StringConstraints(pattern=r"FORM_RESPONSE")]
    createdAt: datetime
    data: ResponseData

    def __init__(self, **data):
        super().__init__(**data)
        # Convert the fields list into a dictionary for faster lookups
        self._fields_dict = {field.label: field.value for field in self.data.fields}


class DataPerjanjianPemasaranProperti(TallyWebhookEvent):
    @cached_property
    def owner_name(self) -> Optional[str]:
        return self._fields_dict.get("owner_name")

    @cached_property
    def owner_address(self) -> Optional[str]:
        return self._fields_dict.get("owner_address")

    @cached_property
    def owner_ktp_num(self) -> Optional[str]:
        return self._fields_dict.get("owner_ktp_num")

    @cached_property
    def owner_phone_num(self) -> Optional[str]:
        return self._fields_dict.get("owner_phone_num")

    @cached_property
    def owner_email(self) -> Optional[str]:
        return self._fields_dict.get("owner_email")

    @cached_property
    def transaction_type(self) -> Optional[str]:
        return self._fields_dict.get("transaction_type")

    # TODO add more properties here
