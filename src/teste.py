import os
import sys
import pandas as pd
from priority_classes.database.database import Postgresql
import re
from dataprocess import dataprocessing as hd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def detect_colspecs_plus(file_path, header_line):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        header = lines[header_line]
    
    indices = [m.start(0) for m in re.finditer(r'\+', header)]
    
    if not indices:
        raise ValueError(f"Nenhum sinal '+' encontrado na linha {header_line}. Verifique o conteúdo da linha de cabeçalho.")
    
    colspecs = [(0, 30)]
    colspecs += [(indices[i] + 1, indices[i + 1]) for i in range(len(indices) - 1)]
    colspecs.append((indices[-1] + 1, len(header)))
    
    return colspecs

def read_fwf_dynamic_plus(file_path, header_line, data_start_line):
    colspecs = detect_colspecs_plus(file_path, header_line)
    df = pd.read_fwf(file_path, colspecs=colspecs, skiprows=data_start_line)
    return df

def excluir_linhas_com_traco(df):
    return df[~df.apply(lambda row: row.astype(str).str.contains('-').any(), axis=1)].reset_index(drop=True)

def excluir_linhas_com_carvalima(df):
    return df[~df.apply(lambda row: row.astype(str).str.contains('CARVALIMA', case=False).any(), axis=1)].reset_index(drop=True)

def excluir_linhas_com_client(df):
    return df[~df.apply(lambda row: row.astype(str).str.contains('CLIENTE', case=False).any(), axis=1)].reset_index(drop=True)

def excluir_linhas_com_vendedor(df):
    return df[~df.apply(lambda row: row.astype(str).str.startswith("VENDEDOR: "), axis=1)].reset_index(drop=True)

def contar_caracteres_por_coluna(df):
    count_chars = df.applymap(lambda x: len(str(x)))
    total_chars_per_column = count_chars.sum()
    return total_chars_per_column

def extrair_vendedor(df):
    if "TABVENC" in df.columns:
        index_tab_venc = df.columns.get_loc("TABVENC")
        df.insert(index_tab_venc + 1, "VENDEDOR", None)
    else:
        print("Coluna 'TABVENC' não encontrada. A nova coluna 'VENDEDOR' será adicionada ao final.")
        df["VENDEDOR"] = None

    for index, row in df.iterrows():
        for cell in row.dropna():
            if "VENDEDOR: " in str(cell):
                vendedor_nome = str(cell).split("VENDEDOR: ")[-1].strip()
                if index + 1 < len(df):
                    df.at[index + 1, "VENDEDOR"] = vendedor_nome
                break

    df = df[~df.apply(lambda row: row.astype(str).str.contains("VENDEDOR: ", case=False).any(), axis=1)].reset_index(drop=True)
    return df

def processamento():
    file_path = "downloads/536.csv"
    header_line = 3
    data_start_line = 0

    try:
        df = read_fwf_dynamic_plus(file_path, header_line, data_start_line)
        
        df.columns = df.iloc[0].astype(str).tolist()
        df = df[1:].reset_index(drop=True)

        df = excluir_linhas_com_traco(df)
        df = excluir_linhas_com_carvalima(df)
        df = excluir_linhas_com_client(df)
        df = extrair_vendedor(df)

        total_chars_per_column = contar_caracteres_por_coluna(df)
        print("\nTotal de caracteres por coluna:")
        print(total_chars_per_column)
        
        os.makedirs('relatorios', exist_ok=True)
        output_csv_path = "relatorios/536.csv"
        df.to_csv(output_csv_path, index=False, sep=";", encoding="utf-8")
        print(f"Arquivo CSV salvo em: {output_csv_path}")
    except ValueError as e:
        print(e)

def ler_arquivo():
    arquivo_csv = 'relatorios/536.csv'
    table = hd.import_file(arquivo_csv)
    table = hd.clear_table(table)
    table = hd.convert_table_types(table)
    return table

def to_db(table):
    db = Postgresql()
    table['Data de atualizacao'] = datetime.now()
    dtype = {'Data de atualizacao': 'TIMESTAMP'}

    db.to_postgresql(
        table,
        table_name='teste_ssw_536',
        dtypes_columns=dtype,
        call_procedure=db.create_procedure_to_delete_duplicateds('teste_ssw_536')
    )

if __name__ == "__main__":
    processamento()
