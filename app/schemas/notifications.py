from pydantic import BaseModel, Field, model_validator
from typing import List, Optional


class AttachmentSchema(BaseModel):
    filename: str
    content: bytes


class Notification(BaseModel):
    methods: List[str] = ["email"]
    recipients: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)
    subject: str = "Notification"
    body: str
    attachments: List[AttachmentSchema] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_data(self):
        if not self.recipients and not self.groups:
            raise ValueError("Either recipients or groups must be provided")
        return self


class NotificationResult(BaseModel):
    status: str = "success"
    error_message: Optional[str] = None