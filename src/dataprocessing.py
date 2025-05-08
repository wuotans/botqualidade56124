import os
import sys
import pandas as pd
import re
from dataprocess import dataprocessing as hd
import pandas as pd
from priority_classes.database.database import Postgresql
import re
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def detect_colspecs_plus(file_path, header_line):
    # Detecta os limites das colunas com base nos sinais de '+' em uma linha do cabeçalho...
    with open(file_path, 'r') as file:
        lines = file.readlines()
        header = lines[header_line]  # Linha do cabeçalho com '+'
    
    # Detectar os índices dos '+' e criar os limites das colunas (colspecs)
    indices = [m.start(0) for m in re.finditer(r'\+', header)]
    
    if not indices:
        raise ValueError(f"Nenhum sinal '+' encontrado na linha {header_line}. Verifique o conteúdo da linha de cabeçalho.")
    
    # Criar os intervalos (colspecs) a partir dos índices dos sinais '+'
    colspecs = [(0, 30)]  # Intervalo fixo inicial de [0, 30]
    colspecs += [(indices[i] + 1, indices[i + 1]) for i in range(len(indices) - 1)]
    
    # Acrescenta o intervalo final após o último '+', caso haja texto restante
    colspecs.append((indices[-1] + 1, len(header)))
    
    print(f"Intervalos de colunas detectados: {colspecs}")  # Exibe os intervalos de colunas
    return colspecs

def read_fwf_dynamic_plus(file_path, header_line, data_start_line):
    # Lê um arquivo de largura fixa com base nos limites de colunas criados pelos sinais '+'
    colspecs = detect_colspecs_plus(file_path, header_line)
    
    # Ler o arquivo com as especificações de colunas
    df = pd.read_fwf(file_path, colspecs=colspecs, header=data_start_line)
    
    return df

def excluir_linhas_com_traco(df):
    # Excluir todas as linhas que contêm o sinal '-'
    df_filtrado = df[~df.apply(lambda row: row.astype(str).str.contains('-').any(), axis=1)].reset_index(drop=True)
    return df_filtrado

def excluir_linhas_com_nro_map(df):
    # Excluir todas as linhas que contêm "NRO MAP"
    df_filtrado = df[~df.apply(lambda row: row.astype(str).str.contains('NRO MAP').any(), axis=1)].reset_index(drop=True)
    return df_filtrado

def excluir_linhas_com_kg(df):
    # Excluir todas as linhas que contêm "Kg"
    df_filtrado = df[~df.apply(lambda row: row.astype(str).str.contains('Kg').any(), axis=1)].reset_index(drop=True)
    return df_filtrado

def excluir_linhas_com_carvalima(df):
    # Excluir todas as linhas que contêm a string "carvalima"
    df_filtrado = df[~df.apply(lambda row: row.astype(str).str.contains('carvalima', case=False).any(), axis=1)].reset_index(drop=True)
    return df_filtrado

def excluir_linhas_com_total(df):
    # Excluir todas as linhas que contêm a string "TOTAL VENDEDOR"
    df_filtrado = df[~df.apply(lambda row: row.astype(str).str.contains('TOTAL VENDEDOR', case=False).any(), axis=1)].reset_index(drop=True)
    return df_filtrado


def contar_caracteres_por_coluna(df):
    # Contar os caracteres em cada célula
    count_chars = df.applymap(lambda x: len(str(x)))
    
    # Somar os caracteres por coluna
    total_chars_per_column = count_chars.sum()
    return total_chars_per_column

def extrair_vendedor(df):
    # Cria uma nova coluna chamada 'VENDEDOR' ao lado de 'COM TOTAL'
    if "COM TOTAL" in df.columns:
        index_col_com_total = df.columns.get_loc("COM TOTAL")
        # Insere uma nova coluna chamada 'VENDEDOR' à direita de 'COM TOTAL'
        df.insert(index_col_com_total + 1, "VENDEDOR", None)
    else:
        print("Coluna 'COM TOTAL' não encontrada. A nova coluna 'VENDEDOR' será adicionada ao final.")
        df["VENDEDOR"] = None
    # Identifica as linhas que contêm 'VENDEDOR' e extrai as informações
    vendedor_info = df.apply(lambda row: row.astype(str).str.contains("VENDEDOR", case=False).any(), axis=1)
    vendedores = df[vendedor_info]
    
    for _, row in vendedores.iterrows():
        # Exemplo: Extrai as informações do nome do vendedor da linha detectada
        vendedor_nome = " ".join(row.dropna().astype(str).values)
        
        # Atualiza as linhas abaixo com o nome do vendedor, na nova coluna 'VENDEDOR'
        vendedor_index = row.name
        df.loc[vendedor_index + 1 :, "VENDEDOR"] = vendedor_nome
     # Ajustar os valores na coluna 'VENDEDOR' para manter apenas os dados após ':'
    df["VENDEDOR"] = df["VENDEDOR"].apply(lambda x: str(x).split(":")[-1].strip() if pd.notna(x) and ":" in str(x) else x)    
        
    return df


def excluir_linhas_com_vendedor(df):
    # Verifica se existe alguma coluna que contenha "VENDEDOR:"
    df_filtrado = df[~df.apply(lambda row: row.astype(str).str.startswith("VENDEDOR").any(), axis=1)].reset_index(drop=True)
    return df_filtrado

def excluir_linhas_com_cliente(df):
    # Excluir todas as linhas que contêm "CLIENTE", exceto o cabeçalho
    df_filtrado = df[~df.apply(lambda row: row.astype(str).str.contains('CLIENTE').any(), axis=1)].reset_index(drop=True)
    return df_filtrado

# Adicionar uma coluna com a data de atualização (data do dia atual)

       

def processamento():
    # Caminho para o arquivo
    file_path = "downloads/56_124.csv"  # Ajuste o caminho conforme necessário

    # Linha do cabeçalho (com '+') e início dos dados
    header_line = 5  # Baseado no exemplo, a linha com '+'
    data_start_line = 0  # Baseado no exemplo, onde os dados começam

    try:
        # Ler o arquivo
        df = read_fwf_dynamic_plus(file_path, header_line, data_start_line)

        # Exibir o DataFrame para inspecionar se a coluna 'cliente' está presente
        print("Primeiras linhas do DataFrame:")
        print(df.head())  # Exibe as primeiras linhas
        print("Nomes das colunas detectadas:")
        print(df.columns)  # Exibe os nomes das colunas
        columns = df.iloc[5]
        print(columns)
        df.columns = columns
        print(df.head())

        # Excluir as linhas que contêm o sinal '-'
        df = excluir_linhas_com_traco(df)
        
        # Excluir as linhas que contêm "NRO MAP"
        df = excluir_linhas_com_nro_map(df)

        # Excluir as linhas que contêm "Kg"
        df = excluir_linhas_com_kg(df)
        
        # Excluir as linhas que contêm "carvalima"
        df = excluir_linhas_com_carvalima(df)
        
        # Excluir as linhas que contêm "TOTAL VENDEDOR"
        df = excluir_linhas_com_total(df)
        
        # Excluir as linhas que contêm "CLIENTE"
        df = excluir_linhas_com_cliente(df)
        
        # Adicionar coluna 'VENDEDOR' e preencher os dados
        df = extrair_vendedor(df)
        
        # Excluir as linhas que começam com "VENDEDOR:"
        df = excluir_linhas_com_vendedor(df)
        
        # Filtrar o DataFrame para excluir todas as linhas após a linha 3681
        df = df.iloc[:3681, :]
        
        # Contar os caracteres por coluna
        total_chars_per_column = contar_caracteres_por_coluna(df)
        print("\nTotal de caracteres por coluna:")
        print(total_chars_per_column)

        # Exibir o DataFrame final
        print("\nDataFrame final:")
        print(df)
        print(df.info())

        os.makedirs('relatorios', exist_ok=True)

        # Salvar arquivo em CSV
        output_csv_path = "relatorios/56_124.csv"
        df.to_csv(output_csv_path, index=False, sep=";", encoding="utf-8")

        print(f"Arquivo CSV salvo em: {output_csv_path}")
    except ValueError as e:
        print(e)

def ler_arquivo():
    
     arquivo_csv = 'relatorios/56_124.csv'
    
     table = hd.import_file(arquivo_csv)
     table = hd.clear_table(table)
     table = hd.convert_table_types(table)
     
    #  print(table['Data de atualizacao'])
     print(table.info())
    #  print(table['Data de atualizacao'])
     return table

def to_db(table):
    db = Postgresql()
    table['Data de atualizacao']=datetime.now()
    dtype = {
        'Data de atualizacao':'TIMESTAMP',
        
    }
    
    db.to_postgresql(
        table, table_name='ssw_op056_124',dtypes_columns=dtype,
        call_procedure=db.create_procedure_to_delete_duplicateds('ssw_op056_124')
    )


# # Chamar a função de processamento
if __name__ == "__main__":

    processamento()
    table = ler_arquivo()
    to_db(table)
