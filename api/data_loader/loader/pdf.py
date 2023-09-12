import logging
from typing import List

from langchain.document_loaders import PyPDFium2Loader
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document
import traceback

logger = logging.getLogger(__name__)


class PdfLoader(BaseLoader):
    """Load pdf files.


    Args:
        file_path: Path to the file to load.
    """

    def __init__(
        self,
        file_path: str,
    ):
        """Initialize with file path."""
        self._file_path = file_path

    def load(self) -> List[Document]:
        # plaintext_file_key = ''
        # plaintext_file_exists = False
        # if self._upload_file:
        #     if self._upload_file.hash:
        #         plaintext_file_key = 'upload_files/' + self._upload_file.tenant_id + '/' \
        #                              + self._upload_file.hash + '.0625.plaintext'
        #         try:
        #             text = storage.load(plaintext_file_key).decode('utf-8')
        #             plaintext_file_exists = True
        #             return [Document(page_content=text)]
        #         except FileNotFoundError:
        #             pass
        try:
            documents = PyPDFium2Loader(file_path=self._file_path).load()
        except Exception as e:
            # print whole traceback
            traceback.print_exc()
            print(str(e))
        # text_list = []
        # for document in documents:
        #     text_list.append(document.page_content)
        # text = "\n\n".join(text_list)

        # save plaintext file for caching
        # if not plaintext_file_exists and plaintext_file_key:
        #     storage.save(plaintext_file_key, text.encode('utf-8'))

        return documents

