from functools import cached_property
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Union


# Model for the fields array
class Field(BaseModel):
    key: str
    label: str
    type: str
    value: Optional[Union[str, int, float, bool]]


# Model for the data object
class ResponseData(BaseModel):
    responseId: str
    submissionId: str
    respondentId: str
    formId: str
    formName: str
    createdAt: datetime
    fields: List[Field]


# Main model for the webhook event
class TallyWebhookEvent(BaseModel):
    eventId: str
    eventType: str
    createdAt: datetime
    data: ResponseData

    def __init__(self, **data):
        super().__init__(**data)
        # Convert the fields list into a dictionary for faster lookups
        self._fields_dict = {field.label: field.value for field in self.data.fields}


class DataPerjanjianPemasaranProperti(TallyWebhookEvent):
    @cached_property
    def user_email(self) -> Optional[str]:
        """Retrieve the user_email from the fields dictionary."""
        return self._fields_dict.get("user_email")

    @cached_property
    def name(self) -> Optional[str]:
        """Retrieve the name from the fields dictionary."""
        return self._fields_dict.get("name")
