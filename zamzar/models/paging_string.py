# coding: utf-8

"""
    Zamzar API

    Zamzar provides a simple API for fast, scalable, high-quality file conversion for 100s of formats.

    The version of the OpenAPI document: 0.0.7
    Contact: api-sdks@zamzar.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class PagingString(BaseModel):
    """
    When you request a list of of all resources of any type (files, formats, jobs), you will receive a paged collection as a response. A paged collection allows you to view a subset of the entire collection (limited to 50 elements) and makes it easy to implement pagination in your application. Use the `limit` parameter to limit the number of results and the `after` parameter to request the next page of results (based on the value of `last` within the paging object).
    """ # noqa: E501
    total_count: Optional[StrictInt] = Field(default=None, description="The number of elements in the entire collection")
    first: Optional[StrictStr] = Field(default=None, description="The identifier of the first element in this page of the collection")
    last: Optional[StrictStr] = Field(default=None, description="The identifier of the last element in this page of the collection")
    limit: Optional[StrictInt] = Field(default=None, description="The maximum number of elements this page could contain")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["total_count", "first", "last", "limit"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of PagingString from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * Fields in `self.additional_properties` are added to the output dict.
        """
        excluded_fields: Set[str] = set([
            "additional_properties",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PagingString from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "total_count": obj.get("total_count"),
            "first": obj.get("first"),
            "last": obj.get("last"),
            "limit": obj.get("limit")
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


