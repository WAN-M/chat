import os
from typing import Type
from .base_parser import BaseParser
from .pdf_parser import PDFParser

class ParserFactory:
    @staticmethod
    def get_parser(file_path: str) -> Type[BaseParser]:
        # 获取文件扩展名
        file_extension = os.path.splitext(file_path)[1].lower()

        # 根据文件扩展名选择对应的Parser
        if file_extension == '.pdf':
            return PDFParser
        else:
            raise ValueError(f"不支持的文件类型: {file_extension}")
