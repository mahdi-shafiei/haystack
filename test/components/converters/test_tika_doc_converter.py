# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import sys
from unittest.mock import patch

import pytest

from haystack.components.converters.tika import TikaDocumentConverter
from haystack.dataclasses import ByteStream


class TestTikaDocumentConverter:
    @patch("haystack.components.converters.tika.tika_parser.from_buffer")
    def test_run(self, mock_tika_parser):
        mock_tika_parser.return_value = {"content": "<div><p>Content of mock source</p></div>"}

        component = TikaDocumentConverter()
        source = ByteStream(data=b"placeholder data")
        documents = component.run(sources=[source])["documents"]

        assert len(documents) == 1
        assert documents[0].content == "Content of mock source"

    def test_run_with_meta(self, test_files_path):
        bytestream = ByteStream(data=b"test", meta={"author": "test_author", "language": "en"})

        converter = TikaDocumentConverter()
        with patch("haystack.components.converters.tika.tika_parser.from_buffer"):
            output = converter.run(
                sources=[bytestream, test_files_path / "markdown" / "sample.md"], meta={"language": "it"}
            )

        # check that the metadata from the sources is merged with that from the meta parameter
        assert output["documents"][0].meta["author"] == "test_author"
        assert output["documents"][0].meta["language"] == "it"
        assert output["documents"][1].meta["language"] == "it"

    def test_run_with_store_full_path_false(self, test_files_path):
        bytestream = ByteStream(data=b"test")
        bytestream.meta["file_path"] = str(test_files_path / "txt" / "doc_3.txt")

        converter = TikaDocumentConverter(store_full_path=False)
        with patch("haystack.components.converters.tika.tika_parser.from_buffer"):
            output = converter.run(sources=[bytestream, test_files_path / "markdown" / "sample.md"])

        # check that the metadata from the sources is merged with that from the meta parameter
        assert output["documents"][0].meta["file_path"] == "doc_3.txt"
        assert output["documents"][1].meta["file_path"] == "sample.md"

    def test_run_nonexistent_file(self, caplog):
        component = TikaDocumentConverter()
        with caplog.at_level("WARNING"):
            component.run(sources=["nonexistent.pdf"])
            assert "Could not read nonexistent.pdf. Skipping it." in caplog.text

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(sys.platform != "linux", reason="Tika Docker container can only run on Ubuntu GitHub runners")
    def test_run_with_txt_files(self, test_files_path):
        component = TikaDocumentConverter()
        output = component.run(sources=[test_files_path / "txt" / "doc_1.txt", test_files_path / "txt" / "doc_2.txt"])
        documents = output["documents"]
        assert len(documents) == 2
        assert "Some text for testing.\nTwo lines in here." in documents[0].content
        assert "This is a test line.\n123 456 789\n987 654 321" in documents[1].content

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(sys.platform != "linux", reason="Tika Docker container can only run on Ubuntu GitHub runners")
    def test_run_with_pdf_file(self, test_files_path):
        component = TikaDocumentConverter()
        output = component.run(
            sources=[test_files_path / "pdf" / "sample_pdf_1.pdf", test_files_path / "pdf" / "sample_pdf_2.pdf"]
        )
        documents = output["documents"]
        assert len(documents) == 2
        assert "A sample PDF file" in documents[0].content
        assert "Page 2 of Sample PDF" in documents[0].content
        assert "Page 4 of Sample PDF" in documents[0].content
        assert documents[0].content.count("\f") == 3  # 4 pages

        assert "First Page" in documents[1].content
        assert (
            "Wiki engines usually allow content to be written using a simplified markup language"
            in documents[1].content
        )
        assert "This section needs additional citations for verification." in documents[1].content
        assert "This would make it easier for other users to find the article." in documents[1].content
        assert documents[1].content.count("\f") == 3  # 4 pages

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(sys.platform != "linux", reason="Tika Docker container can only run on Ubuntu GitHub runners")
    def test_run_with_docx_file(self, test_files_path):
        component = TikaDocumentConverter()
        output = component.run(sources=[test_files_path / "docx" / "sample_docx.docx"])
        documents = output["documents"]
        assert len(documents) == 1
        assert "Sample Docx File" in documents[0].content
        assert "Now we are in Page 2" in documents[0].content
        assert "Page 3 was empty this is page 4" in documents[0].content
