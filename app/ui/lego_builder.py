from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class LegoValidationRule(BaseModel):
    required: Optional[Union[bool, str]] = None
    validationType: Optional[str] = Field(None, description="One of: 'email', 'phone', 'phone_us', 'pattern', 'regex', 'numeric', 'length'")
    pattern: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    errorMessage: Optional[str] = None
    validateOn: Optional[str] = Field("blur", description="'blur', 'change', 'submit', or 'both'")

class LegoInputProps(BaseModel):
    name: str
    label: Optional[str] = None
    placeholder: Optional[str] = None
    inputType: Optional[str] = "text"
    required: Optional[Union[bool, str]] = None
    validationType: Optional[str] = None
    pattern: Optional[str] = None
    errorMessage: Optional[str] = None
    validation: Optional[LegoValidationRule] = None
    className: Optional[str] = None

class LegoLiveErrorProps(BaseModel):
    title: Optional[str] = "Operation Error Detected"
    message: Optional[str] = "An unexpected error occurred during the live monitored process."
    errorCode: Optional[str] = None
    details: Optional[Union[str, Dict[str, Any]]] = None
    retryActionUrl: Optional[str] = None
    retryLabel: Optional[str] = "Retry Operation"

class LegoWidgetConfig(BaseModel):
    type: str
    props: Optional[Dict[str, Any]] = None
    children: Optional[List["LegoWidgetConfig"]] = None

LegoWidgetConfig.model_rebuild()

def create_input_widget(
    name: str,
    label: str,
    placeholder: str = "",
    input_type: str = "text",
    required: bool = False,
    validation_type: Optional[str] = None,
    error_message: Optional[str] = None,
) -> LegoWidgetConfig:
    """Helper to quickly construct a validated input widget element."""
    props = {
        "name": name,
        "label": label,
        "placeholder": placeholder,
        "inputType": input_type,
        "required": required,
    }
    if validation_type:
        props["validationType"] = validation_type
    if error_message:
        props["errorMessage"] = error_message

    return LegoWidgetConfig(type="input", props=props)

def create_live_error_widget(
    title: str,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Union[str, Dict[str, Any]]] = None,
    retry_action_url: Optional[str] = None,
) -> LegoWidgetConfig:
    """Helper to construct a standardized live monitoring error banner widget."""
    props: Dict[str, Any] = {
        "title": title,
        "message": message,
    }
    if error_code:
        props["errorCode"] = error_code
    if details:
        props["details"] = details
    if retry_action_url:
        props["retryActionUrl"] = retry_action_url

    return LegoWidgetConfig(type="live-error-banner", props=props)
