import os 
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader

class Ingestion:
    """ Class to load data automatically from different file formats."""
    def __init__(self, input_data: str):
        self.input_data = input_data
        self.class_loader = [""]
    
    def _check_extension(self, file_path: str):
        """ Checks the file extension and returns the appropriate loader type. """
        _, ext = os.path.splitext(file_path)
        if ext == '.txt':
            return TextLoader(file_path, encoding = "utf-8")
        elif ext == '.pdf':
            return PyPDFLoader(file_path)
        elif ext == '.docx':
            return Docx2txtLoader(file_path)
        else:
            print(f"Unsupported file format: {ext}")
            return None
    
    def load_data(self, chunk_size = 1500, chunk_overlap = 20):
        """ 
        Loads data in txt, pdf, and docx formats.
        Splits the document(s) into chunks of the specified size.
        Args:
            - chunk_size (int): Size of the chunk.
            - chunk_overlap (int): Overlap between chunks.
        """
        docs = []
        if os.path.isfile(self.input_data):
            loader = self._check_extension(self.input_data)
            docs = loader.load()
        elif os.path.isdir(self.input_data):
            for file in tqdm(os.listdir(self.input_data)):
                file_path = os.path.join(self.input_data, file)
                if os.path.isfile(file_path):
                    loader = self._check_extension(file_path)
                    if loader is None:
                        continue
                    else:
                        doc =  loader.load()
                        docs.extend(doc)
        else:
            raise ValueError("The input path must be a file or directory.")
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
            separators = ["\n\n", "\n", " ", ""]
        )
        return text_splitter.split_documents(docs)

