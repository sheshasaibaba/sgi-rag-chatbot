# sgi-rag-chatbot

#Activating the virtual environment in linux.
    source python-venv/bin/activate

#Data preparation

Use the pdf_to_text python file to convert the pdf into a text file, once in the same directory as this python file use the following command 
to convert the pdf into a text.

    python pdf_to_text.py

The text file named extracted_text_layout will be saved in the same directory as the python file


#Data cleaning

Remove the text from the file from the very top to the table of contents.
and also the index related text from the very end of the file since both of these are unnecessary data for the RAG model.
