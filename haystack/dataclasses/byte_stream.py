# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(repr=False)
class ByteStream:
    """
    Base data class representing a binary object in the Haystack API.

    :param data: The binary data stored in Bytestream.
    :param meta: Additional metadata to be stored with the ByteStream.
    :param mime_type: The mime type of the binary data.
    """

    data: bytes
    meta: Dict[str, Any] = field(default_factory=dict, hash=False)
    mime_type: Optional[str] = field(default=None)

    def to_file(self, destination_path: Path) -> None:
        """
        Write the ByteStream to a file. Note: the metadata will be lost.

        :param destination_path: The path to write the ByteStream to.
        """
        with open(destination_path, "wb") as fd:
            fd.write(self.data)

    @classmethod
    def from_file_path(
        cls, filepath: Path, mime_type: Optional[str] = None, meta: Optional[Dict[str, Any]] = None
    ) -> "ByteStream":
        """
        Create a ByteStream from the contents read from a file.

        :param filepath: A valid path to a file.
        :param mime_type: The mime type of the file.
        :param meta: Additional metadata to be stored with the ByteStream.
        """
        with open(filepath, "rb") as fd:
            return cls(data=fd.read(), mime_type=mime_type, meta=meta or {})

    @classmethod
    def from_string(
        cls, text: str, encoding: str = "utf-8", mime_type: Optional[str] = None, meta: Optional[Dict[str, Any]] = None
    ) -> "ByteStream":
        """
        Create a ByteStream encoding a string.

        :param text: The string to encode
        :param encoding: The encoding used to convert the string into bytes
        :param mime_type: The mime type of the file.
        :param meta: Additional metadata to be stored with the ByteStream.
        """
        return cls(data=text.encode(encoding), mime_type=mime_type, meta=meta or {})

    def to_string(self, encoding: str = "utf-8") -> str:
        """
        Convert the ByteStream to a string, metadata will not be included.

        :param encoding: The encoding used to convert the bytes to a string. Defaults to "utf-8".
        :returns: The string representation of the ByteStream.
        :raises: UnicodeDecodeError: If the ByteStream data cannot be decoded with the specified encoding.
        """
        return self.data.decode(encoding)

    def __repr__(self) -> str:
        """
        Return a string representation of the ByteStream, truncating the data to 100 bytes.
        """
        fields = []
        truncated_data = self.data[:100] + b"..." if len(self.data) > 100 else self.data
        fields.append(f"data={truncated_data!r}")
        fields.append(f"meta={self.meta!r}")
        fields.append(f"mime_type={self.mime_type!r}")
        fields_str = ", ".join(fields)
        return f"{self.__class__.__name__}({fields_str})"
