try:
    import yfinance
    import pandas
    import numpy
    import scipy
    import statsmodels
    import matplotlib
    import seaborn
    import google.generativeai
    import langchain
    import chromadb
    import sentence_transformers

    print("Todas as bibliotecas estão OK!")

except ImportError as e:
    print(f"✗ Erro de importação: {e}")
