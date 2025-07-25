# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os

import pytest

from haystack.components.converters.txt import TextFileToDocument
from haystack.dataclasses import ByteStream


class TestTextfileToDocument:
    def test_run(self, test_files_path):
        """
        Test if the component runs correctly.
        """
        bytestream = ByteStream.from_file_path(test_files_path / "txt" / "doc_3.txt")
        bytestream.meta["file_path"] = str(test_files_path / "txt" / "doc_3.txt")
        bytestream.meta["key"] = "value"
        files = [str(test_files_path / "txt" / "doc_1.txt"), test_files_path / "txt" / "doc_2.txt", bytestream]
        converter = TextFileToDocument()
        output = converter.run(sources=files)
        docs = output["documents"]
        assert len(docs) == 3
        assert "Some text for testing." in docs[0].content
        assert "This is a test line." in docs[1].content
        assert "That's yet another file!" in docs[2].content
        assert docs[0].meta["file_path"] == os.path.basename(files[0])
        assert docs[1].meta["file_path"] == os.path.basename(files[1])
        assert docs[2].meta == {"file_path": os.path.basename(bytestream.meta["file_path"]), "key": "value"}

    def test_run_with_store_full_path(self, test_files_path):
        """
        Test if the component runs correctly with store_full_path= False.
        """
        bytestream = ByteStream.from_file_path(test_files_path / "txt" / "doc_3.txt")
        bytestream.meta["file_path"] = str(test_files_path / "txt" / "doc_3.txt")
        bytestream.meta["key"] = "value"
        files = [str(test_files_path / "txt" / "doc_1.txt"), bytestream]
        converter = TextFileToDocument(store_full_path=False)
        output = converter.run(sources=files)
        docs = output["documents"]
        assert len(docs) == 2
        assert "Some text for testing." in docs[0].content
        assert "That's yet another file!" in docs[1].content
        assert docs[0].meta["file_path"] == "doc_1.txt"
        assert docs[1].meta["file_path"] == "doc_3.txt"

    def test_run_error_handling(self, test_files_path, caplog):
        """
        Test if the component correctly handles errors.
        """
        paths = [test_files_path / "txt" / "doc_1.txt", "non_existing_file.txt", test_files_path / "txt" / "doc_3.txt"]
        converter = TextFileToDocument()
        with caplog.at_level(logging.WARNING):
            output = converter.run(sources=paths)
            assert "non_existing_file.txt" in caplog.text
        docs = output["documents"]
        assert len(docs) == 2
        assert docs[0].meta["file_path"] == os.path.basename(paths[0])
        assert docs[1].meta["file_path"] == os.path.basename(paths[2])

    def test_encoding_override(self, test_files_path):
        """
        Test if the encoding metadata field is used properly
        """
        bytestream = ByteStream.from_file_path(test_files_path / "txt" / "doc_1.txt")
        bytestream.meta["key"] = "value"

        converter = TextFileToDocument(encoding="utf-16")
        output = converter.run(sources=[bytestream])
        assert "Some text for testing." not in output["documents"][0].content

        bytestream.meta["encoding"] = "utf-8"
        output = converter.run(sources=[bytestream])
        assert "Some text for testing." in output["documents"][0].content

    def test_run_with_meta(self):
        bytestream = ByteStream(data=b"test", meta={"author": "test_author", "language": "en"})

        converter = TextFileToDocument()

        output = converter.run(sources=[bytestream], meta=[{"language": "it"}])
        document = output["documents"][0]

        # check that the metadata from the bytestream is merged with that from the meta parameter
        assert document.meta == {"author": "test_author", "language": "it"}
