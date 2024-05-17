import io
import json
import random
import datetime
from time import time
import pandas as pd
pd.options.mode.chained_assignment = None

import tabula
from PyPDF2 import PdfReader



class PrepareDataApontHours:
    """
        Classe para preparação de dados do apontamento de horas.
    """
    def __init__(self):
        self.api = ""
        self.list_months = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

    def convert_xlsx_to_DataFrame(self, file):
        try:
            contents = file.read()
            file_bytes = io.BytesIO(contents)
            file = pd.ExcelFile(file_bytes)
            sheet_name = file.sheet_names[0]
            df = file.parse(sheet_name=sheet_name, dtype='str')
            df.fillna("", inplace=True)
            return df
        except Exception as e:
            print(f"\n\n ### ERROR CONVERT FILE TO DATAFRAME | ERROR: {e} ### ")
            return None
        
    def convert_csv_to_DataFrame(self, file):
        try:
            contents = file.read()
            file_bytes = io.BytesIO(contents)
            df = pd.read_csv(file_bytes, delimiter=";", dtype="str", header=None)
            return df
        except Exception as e:
            print(f"\n\n ### ERROR CONVERT FILE TO DATAFRAME | ERROR: {e} ### ")
            return None

    def convert_query_to_dataframe(self, data, cols_name):
        df = pd.DataFrame(data, columns=cols_name)
        return df

    def segundos_para_tempo(self, segundos):
        minutos = segundos // 60
        segundos %= 60
        horas = minutos // 60
        minutos %= 60
        return f"{horas:02d}:{minutos:02d}"


    def prepare_data_to_create_new_apont_hour(self, username_pk, date_init, hour_init, hour_final, atividade, competencia, username, setor, df_company):
        try:
            username_pk = int(username_pk)
            date_init = datetime.datetime.strptime(date_init, "%Y-%m-%d")
            year = date_init.year
            month = self.list_months[date_init.month-1]
            id_acessorias = df_company["id_acessorias"][0]
            razao_social = df_company["razao_social"][0]
            regime = df_company["regime"][0]

            if hour_init and hour_final != "":
                _date_init = date_init.strftime("%d/%m/%Y")
                _hour_init = datetime.datetime.strptime(f"{_date_init} {hour_init}:00", "%d/%m/%Y %H:%M:%S")
                _hour_final = datetime.datetime.strptime(f"{_date_init} {hour_final}:00", "%d/%m/%Y %H:%M:%S")
                if _hour_final < _hour_init:
                    return {
                        "code": 400,
                        "error": "error hour"
                    }
                tempo = _hour_final - _hour_init
                tempo = self.segundos_para_tempo(segundos=tempo.seconds)

                print(f"""
                    -----------------------------
                    >>>> hour_init: {_hour_init}
                    >>>> hour_final: {_hour_final}
                    >>>> tempo: {tempo}
                """)

            else:
                tempo = "-"

            if "SIMPLES" in regime:
                regime_agrup = "Simples"
            elif "LUCRO REAL" in regime:
                regime_agrup = "Lucro Real"
            elif "LUCRO PRESUMIDO" in regime:
                regime_agrup = "Lucro Presumido"
            elif "MEI" in regime:
                regime_agrup = "MEI"
            else:
                regime_agrup = "Outros"
            # ----
            if "MEI" in regime:
                tipo_empresa = "MEI"
            else:
                tipo_empresa = "Normal"

            return {
                "code": 200,
                "data_apont": date_init.strftime("%d/%m/%Y"),
                "horario_inicio": hour_init,
                "horario_fim": hour_final,
                "competencia": competencia,
                "codigo_empresa": id_acessorias,
                "razao_social": razao_social,
                "atividade": atividade,
                "observacao": "-",
                "username": username,
                "setor": setor,
                "mes": month,
                "ano": year,
                "tempo": tempo,
                "regime": regime,
                "regime_agrup": regime_agrup,
                "tipo_empresa": tipo_empresa,
            }
        except Exception as e:
            print(f"\n\n ### ERROR CREATE DATA TO NEW APONT HOUR | ERROR: {e}")
            return None


class PrepareDataToImportPackage3703:
    """
        Classe para preparação de dados do Pacote 3703 no sistema JB Software.
    """
    
    # def __init__(self):
    #     self.api = ""

    def data_strip(data):
        """ return str: sem espaços no início e fim """
        return str(data).strip()
    
    def create_data_randomic():
        """ return int: valor para complemento do """
        number = random.randint(10**17, 10**18 - 1)
        return number
    
    def create_text_compl_grupo_lancamento(model, dict_data_replace: dict, grupo_lancamento="-", value_generic=None):
        """
            return str: texto que será utilizado no complemento do grupo de lançamento
                - saida esperada, exemplo "model_1":
                - return: "Pgto. Nome do pagador/recebedor - Data Venc: 01/01/2024"
            
            __________________________________________________________________________________________________

            > obtem o modelo (model) da importação e substitui [V 'n'] pelos valores do dict -> dict_data_replace
            - formato esperado de exemplo para o objeto "dict_data_replace" do "model_1": {"v1": "Gaulke Contábil", "v2": "01/01/2024"}
        """
        try:
            if model == "-":
                return model
            else:
                data_model_text = {
                    # exemplo 1: Pgto. [Nome do cliente] - Data Venc: [data completa]
                    "model_1": "Pgto. [v1] - Data Venc: [v2]",
                    # ----
                    # exemplo 2: Pgto. Salários Ref. Mês [mês/ano] - [nome do cliente]
                    "model_2": f"Pgto. Salários Ref. Mês {grupo_lancamento} - [v1]",
                    # ----
                    # exemplo 3: VLR ICMS S/CTE nº [número CTE]
                    "model_3": f"VLR ICMS S/CTE nº [v1]",
                    # ----
                    # exemplo 4: Receb. Dupl [nome cliente] venc [data vencimento]
                    "model_4": f"Receb. Dupl [v1] venc [v2]",
                    # ----
                    # exemplo 5: Entrada Títulos Desc. [nome cliente] venc [data vencimento] [Sicoob, Itau, ...]
                    "model_5": f"Entrada Títulos Desc. {value_generic} Dupl. [v1] - [v2] - venc [v3]",
                    # ----
                    # exemplo 6: Entrada Decorise dd/mm/yyyy
                    "model_6": f"Pgto. Decorise {grupo_lancamento} - Gateway [v1] [v2]",
                    # ----
                    # exemplo 7: Recebimento Dupl. nº NF [v1] - [v2]
                    "model_7": f"Recebimento Dupl. nº NF [v1] - [v2]",

                    # ----
                    # exemplo 8: Nome do Beneficiário Data Venc: dd/mm/yyyy
                    "model_8": f"Pgto. {value_generic} [v1] - Data Venc: [v2]",
                    # ----
                    # exemplo 9: [Nome] NFº [NF] Data Venc. [dd/mm/yyyy]
                    "model_9": "Pgto. [v1] Nº [v2] Data Venc. [v3]",
                    # ----
                    # exemplo 10: [Nome] - Data Venc. [dd/mm/yyyy]
                    "model_10": "Pgto. [v1] - Data Venc. [v2]",
                    # ----
                    # exemplo 10: [Nome] - Data Venc. [dd/mm/yyyy]
                    "model_10.2": "Pgto. [v1] - Data Pagam. [v2]",
                    # ----
                    # exemplo 11: [Nome] - Data Venc. [dd/mm/yyyy]
                    "model_11": "Pgto. Dupl. [v1]",
                    # ----
                    # exemplo 12: [DATA_PAGAMENTO] - [NOME_PAGADOR]
                    "model_12": "RECEB. FAT/CTE [v1] - [v2]",
                    # ----
                    # exemplo 13: [NOME_PAGADOR]
                    "model_13": "PAGAM. [v1]",
                    # ----
                    # exemplo 14: [NOME_PAGADOR]
                    "model_14": "Pagamento Dupl [v1] - [v2]",
                    # ----
                    # exemplo 15: [NFº] [NOME_PAGADOR] [BANCO]
                    "model_15": "Recebimento Dupl [v1] - [v2] - [v3]",
                    # ----
                    # exemplo 16: [NFº] [NOME_PAGADOR] [BANCO]
                    "model_16": "Pagamento Dupl [v1] - [v2] - [v3]",
                    # ----
                    # exemplo 17: [NOME] [VENC] - [BANCO]
                    "model_17": f"Recebimento Dupl [v1] - Doc: [v3] {value_generic}",
                    # ----
                    # exemplo 18: [NOME] [DATA_PAGAMENTO]
                    "model_18": f"Pagamento Dupl [v1] - Doc: [v2] {value_generic}",
                    # ----
                    # exemplo 21: [NOME] [NF]
                    "model_21": f"Recebimento Dupl [v1] NF [v2]",
                }

                text = data_model_text.get(model)
                for k,v in dict_data_replace.items():
                    text = text.replace(k, str(v))
                
                return text
        except Exception as e:
            print(f"\n\n ### ERROR CREATE TEXT COMPL. HOST | ERROR: {e}")
            return None
        
    def create_dict_data_replace(dataframe, list_col_name, index):
        """
            return: texto temporário para utilizar com argumento na função "create_text_compl_grupo_lancamento"
            - valor esperado do parâmetro "list_col_name": ["NF", "VALOR", "outros..."]
            - valor esperado do parâmetro "index": posição do elemento do DataFrame com as informações das respectivas colunas "list_col_name"
            _______________________________________________________________
            exemplo:
            - list_col_name = ["NF", "DATA"]
            - DataFrame[ posição do item na list_col_name = "NF" ][posição do elemento do DataFrame = index]
            - return: {"v1": "123456", "v2": "01/01/2024", ...}     
        """

        dict_data_replace=dict()
        for i in range(len(list_col_name)):
            print(f" -----------> COLS: {list_col_name}")
            data_aux =  dataframe[list_col_name[i]][index]
            value = {f"[v{i+1}]": data_aux}
            print(f" ****** {value}")
            dict_data_replace.update(value)

        return dict_data_replace
        
    def create_layout_JB(dataframe, model="-", grupo_lancamento="", value_generic=None, cod_empresa=""):
        """
            return: Objeto DataFrame com dados para os lançamentos contábeis no sistema JB Software, de acordo com o Layout 3703.
            - esperado de "model" str: "model_1"
            - esperado do "grupo_lancamento" str: mês e ano neste, recomendável neste formato "mm/yyyy" para manter o padrão
            - esperado de "value_generic": qualquer valor para utilização no final do texto do complemento de histórico.
            - esperado de "cod_empresa": código da empresa JB Software
        """
        LIST_TP_REGISTRO = list()
        LIST_EMPRESA = list()
        LIST_COD_EMPRESA = list()
        LIST_FILIAL = list()
        LIST_DATA = list()
        LIST_NR_L_CTO_ERP = list()
        LIST_TP = list()
        LIST_CONTA = list()
        LIST_SUBCONTA = list()
        LIST_VALOR = list()
        LIST_ACAO = list()
        LIST_PRIMEIRO_HIST_CTA = list()
        LIST_COD_HISTORICO = list()
        LIST_COMPL_HISTORICO = list()
        LIST_GRUPO_LCTO = list()
        LIST_CNPJ = list()
        LIST_IESTADUAL = list()
        LIST_TP_CNPJ = list()
        LIST_CONTA_ORIGEM = list()
        LIST_CNPJ_EMPRESA = list()
        LIST_IE_EMPRESA = list()
        LIST_TYPE_PROCESS = list()

        tt_index = len(dataframe.index)
        for i in dataframe.index:
            print(f" INDEX JB: {i}/{tt_index}")
            LIST_TP_REGISTRO.append("00")
            LIST_EMPRESA.append("") # MANUAL
            LIST_COD_EMPRESA.append(cod_empresa)
            # LIST_FILIAL.append("") # MANUAL
            LIST_DATA.append("-")
            LIST_NR_L_CTO_ERP.append("-") # GERAR ALFANUMERICO
            LIST_TP.append("D") # CRIAR LINHAS ---> D e C (débito/crédito)
            LIST_CONTA.append("-") # MANUAL)
            LIST_SUBCONTA.append("0")
            LIST_VALOR.append("-")
            LIST_ACAO.append("0")
            LIST_COD_HISTORICO.append("0")
            # LIST_PRIMEIRO_HIST_CTA.append("2")
            
            filial = ""
            text = "-"
            value_primeiro_hist_cta = ""
            value_tp_cnpj = ""
            value_cnpj = ""
            try:
                if model == "model_1":
                    # modelo: ?
                    value_primeiro_hist_cta = "2"
                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["nome_beneficiario", "data_de_vencimento"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace)

                elif model == "model_2":
                    # modelo: ?
                    value_primeiro_hist_cta = "2"
                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["NOME_TEMP"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, grupo_lancamento=grupo_lancamento)

                elif model == "model_3":
                    # modelo: ?
                    value_primeiro_hist_cta = "2"
                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["CTE"], index=i)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace)

                elif model == "model_4":
                    # modelo: ?
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "1"
                    value_cnpj = dataframe["CNPJ"][i]
                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["Nome Cliente", "Vencimento"], index=i)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace)

                elif model == "model_5":
                    # modelo: SICOOB
                    value_primeiro_hist_cta = "2"
                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["SEU_NUMERO", "NOME", "DATA_VENCIMENTO"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")

                elif model == "model_6":
                    # modelo: DECORISE
                    value_primeiro_hist_cta = "2"
                    # dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["Conf. Gateway", "DATA_TEMP"], index=i)
                    # text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, grupo_lancamento=grupo_lancamento, value_generic=value_generic)
                    text = "Recebimento ref. e-commerce Megapay"
                    # print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")

                elif model == "model_7":
                    # modelo: Arão dos Santos

                    filial = dataframe["Filial"][i]
                    value_primeiro_hist_cta = "2"
                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["Nº NF", "Nome Cliente"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                
                elif model == "model_8":
                    # modelo: Extrato Bradesco
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "2"
                    
                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["nome_beneficiario", "data_de_vencimento"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    grupo_lancamento = "0"
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                
                elif model == "model_9":
                    # modelo: Extrato Grupo DAB RN
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "2"
                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["NOME_ORIGIN", "NOTA_FISCAL", "DATA_VENC"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                
                elif model == "model_10":
                    # modelo: Extrato Bradesco
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "2"

                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["nome_beneficiario", "data_de_vencimento"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                
                elif model == "model_10.2":
                    # modelo: Comprov. Pag. Tit. Itaú
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "2"

                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["nome_pagador", "data_de_pagamento"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                
                elif model == "model_11":
                    # modelo: Extrato Bradesco
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "2"

                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["nome_beneficiario"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                
                elif model == "model_12":
                    # modelo: Importação contas a receber - INOVA
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "1"

                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["Título-Dpl.", "nome_pagador"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                
                elif model == "model_13":
                    # modelo: Importação contas a pagar - PONTO CERTO
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "2"
                    
                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["nome_pagador"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                
                elif model == "model_14":
                    # modelo: Importação contas a pagar - GARRA
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "2"

                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["NF-e", "nome_pagador"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                
                elif model == "model_15":
                    # modelo: Importação contas a receber - TELL
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "1"

                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["Número", "nome_pagador", "Descrição"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")

                elif model == "model_16":
                    # modelo: Importação contas a pagar - TELL
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "2"

                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["Número", "nome_pagador", "Descrição"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")

                elif model == "model_17":
                    # modelo: Importação relatório do beneficiário Civia
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "1"

                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["nome_beneficiario", "data_de_vencimento", "N_Documento"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                
                elif model == "model_18":
                    # modelo: Importação comprovantes de pagamentos ABBRACCIO
                    value_primeiro_hist_cta = "2"
                    value_tp_cnpj = "1"

                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["nome_beneficiario", "data_de_debito"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                
                elif model == "model_21":
                    # modelo: Importação Liquidação Títulos Descontados Sicoob
                    value_primeiro_hist_cta = "2"
                    
                    dict_data_replace = PrepareDataToImportPackage3703.create_dict_data_replace(dataframe=dataframe, list_col_name=["nome_beneficiario", "seu_numero_original"], index=i)
                    text = PrepareDataToImportPackage3703.create_text_compl_grupo_lancamento(model=model, dict_data_replace=dict_data_replace, value_generic=value_generic)
                    print("\n\n >>>>>>> DICT DATA TO REPLACE:  ", dict_data_replace)
                    print(f">>>>>>>>>>>>>>>> TEXT: {text}")
                

                
            except Exception as e:
                print(f"\n\n\n -------------->>>> ERROR : {e}")
                return
            
            LIST_FILIAL.append(filial) # MANUAL
            LIST_PRIMEIRO_HIST_CTA.append(value_primeiro_hist_cta)
            LIST_COMPL_HISTORICO.append(text) # TEXTO ALTERNATIVO --> CONCATENAR COM?

            # ----
            LIST_GRUPO_LCTO.append(PrepareDataToImportPackage3703.create_data_randomic()) # CÓDIGO ÚNICO DE ATÉ 18 CARACTERES
            LIST_CNPJ.append(value_cnpj)
            LIST_IESTADUAL.append("")
            LIST_TP_CNPJ.append(value_tp_cnpj)
            LIST_CONTA_ORIGEM.append("")
            LIST_CNPJ_EMPRESA.append("")
            LIST_IE_EMPRESA.append("")
            LIST_TYPE_PROCESS.append("comum")


        dataframe["TP_REGISTRO"] = LIST_TP_REGISTRO
        dataframe["NOME"] = LIST_EMPRESA
        dataframe["COD_EMPRESA"] = LIST_COD_EMPRESA
        dataframe["FILIAL"] = LIST_FILIAL
        dataframe["DATA"] = LIST_DATA
        dataframe["NR_L_CTO_ERP"] = LIST_NR_L_CTO_ERP
        dataframe["TP"] = LIST_TP
        dataframe["CONTA"] = LIST_CONTA
        dataframe["SUBCONTA"] = LIST_SUBCONTA
        dataframe["VALOR"] = LIST_VALOR
        dataframe["ACAO"] = LIST_ACAO
        dataframe["PRIMEIRO_HIST_CTA"] = LIST_PRIMEIRO_HIST_CTA
        dataframe["COD_HISTORICO"] = LIST_COD_HISTORICO
        dataframe["COMPL_HISTORICO"] = LIST_COMPL_HISTORICO
        dataframe["GRUPO_LCTO"] = LIST_GRUPO_LCTO
        dataframe["CNPJ"] = LIST_CNPJ
        dataframe["IESTADUAL"] = LIST_IESTADUAL
        dataframe["TP_CNPJ"] = LIST_TP_CNPJ
        dataframe["CONTA_ORIGEM"] = LIST_CONTA_ORIGEM
        dataframe["CNPJ_EMPRESA"] = LIST_CNPJ_EMPRESA
        dataframe["IE_EMPRESA"] = LIST_IE_EMPRESA
        dataframe["TYPE_PROCESS"] = LIST_TYPE_PROCESS

        # print( "\n\n\n\n ################################################# ")
        # print(dataframe)

        return dataframe
    
    # ----

    def create_additional_columns(dataframe, column_name, default_value):
        """
            return: DataFrame com nova coluna e valor padrão para todas as linhas
            exemplo:
            - esperado de "column_name": "NOME DA NOVA COLUNA"
            - esperado de "default_value": "VALOR PADRÃO PARA TODAS AS LINHAS DA NOVA COLUNA"
        """
        dataframe[f"{column_name}"] = default_value
        return dataframe
        
    # ----
    
    def drop_columns_dataframe(dataframe, list_columns: list):
        """" return: Deleta as colunas [list_columns] do DataFrame """
        if len(list_columns) > 0:
            try:
                for col_name in list_columns:
                    dataframe = dataframe.drop(labels=col_name, axis=1)
            except:
                pass
        return dataframe
    
    # ----
    
    def transpose_values(dataframe, dict_cols_transpose):
        """
            return: Copia valores de uma coluna para outra.\n
            exemplo:\n
                - Coluna "CNPJ_ORIGIN" contém dados originais\n
                - Coluna "CNPJ" recebe os dados da coluna "CNPJ_ORIGIN"
                - objeto esperado de exemplo: {"CNPJ": "CNPJ_ORIGIN"}
                - saída esperada: DataFrame["CNPJ"] --> recebe dados da coluna "CNPJ_ORIGIN"
        """
        if len(dict_cols_transpose.keys()) > 0:
            for k,v in dict_cols_transpose.items():
                dataframe[k] = dataframe[v]
        return dataframe
    
    # ----
    
    def rename_columns_dataframe(dataframe, dict_replace_names):
        """
            return: DataFrame com colunas renomeadas.\n
                - dict_replace_names: {"nome_antigo": "novo_nome"}
        """
        dataframe = dataframe.rename(columns=dict_replace_names)
        return dataframe
    
    # ----
    
    def duplicate_dataframe_rows(dataframe, TP_account="C"):
        """"
            return: DataFrame atualizado com linhas duplicadas.\n
            - será atualizado apenas os valoes de "TP" de lançamento.\n
            - exemplo de uso: quando necessário criar duplicatas simples para DÉBITO E CRÉDITO.
        """
        
        df_copy = dataframe.copy()
        df_copy.loc[:, 'TP'] = TP_account
        new_dataframe = pd.concat([dataframe, df_copy])
        return new_dataframe
    
    # ----
    
    def duplicate_dataframe_rows_lote(dataframe, list_update_cols=list):
        """
            return: DataFrame atualizado com linhas duplicadas em lote. Serão atualizados os valoes de "TP" e "TYPE_PROCESS".
        """

        new_dataframe = None
        list_dataframes = list()
        for x in list_update_cols:
            df_copy = dataframe.copy()
            print(f"""\n
                ----> TP: {x["TP"]}
                ----> TYPE_PROCESS: {x["TYPE_PROCESS"]}
            """)
            df_copy.loc[:, 'TP'] = x["TP"]
            df_copy["TYPE_PROCESS"] = x["TYPE_PROCESS"]
            list_dataframes.append(df_copy)

        list_dataframes.append(dataframe)
        new_dataframe = pd.concat(list_dataframes)

        return new_dataframe
    
    # ----
    def check_discount_or_fees(document_value, amount_paid):
        document_value = float(str(document_value).replace(".", "").replace(",", "."))
        amount_paid = float(str(amount_paid).replace(".", "").replace(",", "."))
        print(f"""\n
            ---------------------------------------------------------
            -----> document_value: {document_value}
            -----> amount_paid: {amount_paid}
        """)
        if amount_paid > document_value:
            return "fees"
        elif amount_paid < document_value:
            return "discount"
        
        return "normal"
    

    # ----
    def create_dataframe_discount_and_fees_cobrancas_pagas(dataframe):
        print("\n\n ----------------------- CRIA DATAFRAME DE JUTOS E DESCONTOS -----------------------  ")
        print("\n\n -------- JUROS -------- ")

        list_data_calculate = list()
        for i in dataframe.index:
            valor = float(dataframe["Valor"][i].values[0])
            valor_pago = float(dataframe["Valor pago"][i].values[0])
            dataframe["Valor"][i] = valor
            dataframe["Valor pago"][i] = valor_pago
            calculate = abs( valor_pago - valor )
            list_data_calculate.append(calculate)
        
        dataframe["calculo"] = list_data_calculate
        
        dataframe_juros = dataframe.copy()
        dataframe_juros = dataframe_juros[ (dataframe_juros["calculo"] > 0) & (dataframe_juros["TP"] == "D") ]

        dataframe_juros.index = list(range(0, len(dataframe_juros.index)))
        if len(dataframe_juros.index) >= 1:
            for i in dataframe_juros.index:
                dataframe_juros["TP"][i] == "C"
                dataframe_juros["TYPE_PROCESS"][i] = "process_juros"

                new_value = str(round(dataframe_juros["Valor pago"][i] - (dataframe_juros["Valor pago"][i] - dataframe_juros["calculo"][i]), 2))
                dataframe_juros["VALOR_PAGO"][i] = new_value

        print(dataframe_juros)
        
        print("\n\n\n -------- DESCONTO -------- ")
        dataframe_desconto = dataframe.copy()
        dataframe_desconto = dataframe_desconto[ (dataframe_desconto["calculo"] < 0) & (dataframe_desconto["TP"] == "C") ]

        if len(dataframe_desconto.index) >= 1:
            for i in dataframe_desconto.index:
                dataframe_desconto["TYPE_PROCESS"][i] = "process_desconto"
                new_value = str(round(dataframe_juros["Valor pago"][i] - (dataframe_juros["Valor pago"][i] - dataframe_juros["calculo"][i]), 2))
                dataframe_juros["VALOR_PAGO"][i] = new_value

    
        print(dataframe_desconto)

        dataframe = pd.concat([dataframe, dataframe_juros, dataframe_desconto])
        # for i in dataframe.index:
        #     dataframe
        return dataframe

    # ----
    def create_dataframe_discount_and_fees(dataframe):
        df_discount = dataframe[dataframe["tipo_registro"] == "discount"].drop_duplicates(subset=["GRUPO_LCTO"])
        df_fees = dataframe[dataframe["tipo_registro"] == "fees"].drop_duplicates(subset=["GRUPO_LCTO"])
        
        if len(df_discount) > 0:
            df_discount.loc[:, 'TYPE_PROCESS'] = 'process_discount'
            dataframe = pd.concat([dataframe, df_discount])
        elif len(df_fees) > 0:
            df_fees.loc[:, 'TYPE_PROCESS'] = 'process_fess'
            dataframe = pd.concat([dataframe, df_fees])    
        return dataframe

    # ----
    
    def convert_dataframe_to_excel(dataframe, file_name):
        try:
            return dataframe.to_excel(file_name)
        except:
            return
    
    # ----
    
    def readjust_values_dataframe(dataframe):
        for i in dataframe.index:
            dataframe["NR_L_CTO_ERP"][i] = f"COD{i}TM{int(time())}"
            if dataframe["TYPE_PROCESS"][i] in ["process_discount" , "process_fess"]:
                dataframe["VALOR"][i] = dataframe["valor_dif"][i]
                dataframe["VALOR"][i-2] = dataframe["valor_documento"][i-2]
                dataframe["VALOR"][i-1] = dataframe["valor_cobrado"][i-1]
            else:
                dataframe["VALOR"][i] = dataframe["valor_cobrado"][i]
        return dataframe
    
    # ----
    
    def create_cod_erp_to_dataframe(dataframe, index_default=0):
        """
            return: DataFrame com valores da colunas "NR_L_CTO_ERP" atualizados com valores randômicos.\n
                - index_default int: deve um valor inteiro (int) para iteração com i (index) do DataFrame;\n
                - exemplo:

                    valor de "index_default" passado na função com 2.\n
                    porém, já está definido valor padrão como 0 (ZERO).\n
                    -   for i in dataframe.index:\n
                            ... --> equação: i + index_default ==> é o mesmo que i + 2
        """
        
        for i in dataframe.index:
            # print("\n --------------  ")
            # print(f">>>> COD{i+index_default}TM{int(time())}")
            numero_lanc_cto_erp = f"COD{i+index_default}TM{int(time())}"
            dataframe["NR_L_CTO_ERP"][i] = numero_lanc_cto_erp
        # print(" ------ DF ERP FINISH ------ ")
        # print(dataframe)
        return dataframe
    
    # ----
    
    def filter_columns_dataframe(daraframe, list_columns: list):
        """
            return: DataFrame com colunas exclusivas.\n
                - list_columns list: deve ser uma lista Python (list) com nomes das colunas a serem indexadas ao DataFrame;\n
                - exemplo:
                    -   list_columns = ["VALOR", "CNPJ", "NOME"];
        """
        return daraframe[list_columns]
    
    # ----
    
    def filter_data_dataframe(daraframe, name_column: str, list_remove_values: list):
        """
            return: DataFrame com valores filtrados.\n
                - name_column str: deve ser o nome (str) da coluna do DF;\n
                - list_remove_values list: deve ser uma lista (list) Python com os valores a serem removidos do DF;\n\n
                - exemplo:
                    -   name_column = "VALOR";
                    -   list_remove_values = ["0.00", "0,00", 0.00];

        """
        daraframe = daraframe[~daraframe[name_column].isin(list_remove_values)]
        return daraframe
    
    # ----
    
    def readjust_values_dataframe_decimal(dataframe, list_cols_name: list, replace_values_list=True):
        for col in list_cols_name:
            dataframe[col] = dataframe[col].str.replace('.', '').str.replace(',', '.')
        if replace_values_list:
            for i in dataframe.index:
                for col in list_cols_name:
                    dataframe[col][i] = dataframe[col][i].split()[1]
        return dataframe
    
    def adjust_value_to_decimal_string(dataframe, column_name: str, replace_caract = False, replace_from_format_BRL=False):
        """
            --> dataframe: DataFrame com index de 0 a (n).
            --> column_name: nome da coluna com valores a serem ajustados
            --> return: DataFrame[NAME_COLUMN] -> "###.##" (valor decimal em string).

            Resumo:\n
                * será verificado a posição no separador decimal (.) e ajustado conforme a necessidade para 2 (duas) casas decimais.\n
        """
        for i in dataframe.index:
            dataframe[column_name][i] = str(dataframe[column_name][i])

            if replace_caract:
                dataframe[column_name][i] = dataframe[column_name][i].replace(",", ".")

            elif replace_from_format_BRL:
                dataframe[column_name][i] = dataframe[column_name][i].replace(".", "").replace(",", ".")
            

            if len(dataframe["CNPJ"][i]) == 12:
                dataframe["CNPJ"][i] = "00" + dataframe["CNPJ"][i]
            elif len(dataframe["CNPJ"][i]) == 13:
                dataframe["CNPJ"][i] = "0" + dataframe["CNPJ"][i]

            if dataframe[column_name][i] == "0":

                dataframe[column_name][i] = "0.00"
                # print(f"\n\n >> INDEX: {i} | VALOR: {dataframe[column_name][i]} | valor decimal ajustado")

            elif "." in dataframe[column_name][i]:
                
                if dataframe[column_name][i][-2] == ".":

                    dataframe[column_name][i] = dataframe[column_name][i] + "0"
                    # print(f"\n\n >> INDEX: {i} | VALOR: {dataframe[column_name][i]} | valor decimal incorreto (01) ajustado")
                
                elif dataframe[column_name][i][-3] == ".":
                    pass
                    # print(f"\n\n >> INDEX: {i} | VALOR: {dataframe[column_name][i]} | valor decimal correto")

            else:
                dataframe[column_name][i] = dataframe[column_name][i] + ".00"
                # print(f"\n\n >> INDEX: {i} | VALOR: {dataframe[column_name][i]} | valor decimal incorreto (02) ajustado")
            
            if dataframe[column_name][i].count(".") == 2:
                dataframe[column_name][i] = dataframe[column_name][i].replace(".", "", 1)



        return dataframe
    
    def calculate_discount_or_fees(dataframe, col_name_valor_pago, col_name_valor_doc):
        try:
            dataframe["juros"] = "0.00"
            dataframe["desconto"] = "0.00"
            print(dataframe)
            print(dataframe.info())
            for i in dataframe.index:
                valor_pago  = float(dataframe[col_name_valor_pago][i])
                valor_doc   = float(dataframe[col_name_valor_doc][i])

                print(f"""
                    -------------------------------
                    >>> valor_pago: {valor_pago}
                    >>> valor_doc: {valor_doc}
                """)

                if valor_pago > valor_doc:
                    dataframe["juros"][i] = round(valor_pago - valor_doc, 2)
                elif valor_pago < valor_doc:
                    dataframe["desconto"][i] = round(valor_doc - valor_pago, 2)
            return dataframe
        except Exception as e:
            print(f"\n\n ### ERRO AO CALCULAR JUTOS E DESCONTO | ERROR: {e}")
            return e


    # ----
    # versão descontinuada 01/02/2024 ---> desenvolvido novo modelo (V2). Mais otimizado.
    def read_pdf_comprovante_banco_do_brasil(file, company_session):
        
        contents = file.read()
        pdf_bytes = io.BytesIO(contents)
        pdf_reader = PdfReader(pdf_bytes)

        list_data_pages = list()
        list_page_erros = list()
        index_page = 0
        print(f" TT PAGES: {len(pdf_reader.pages)}")

        for index_page in range(len(pdf_reader.pages)):
            try:
                print(f"\n\n\n ---- INDEX PAGE: {index_page}")
                
                page = pdf_reader.pages[index_page]
                
                
                data_page = page.extract_text()
                print(data_page)

                data_extract = {
                    "index": {"text": 0},
                    "beneficiario_final": {"data_init": 0, "data_final": 0, "text": ""},
                    "cnpj": {"text": ""},
                    "data_vencimento": {"text": ""},
                    "data_pagamento": {"text": ""},
                    "valor_documento": {"text": ""},
                    "valor_cobrado": {"text": ""},
                    "valor_dif": {"text": ""},
                    "tipo_registro": {"text": "normal"},
                }
                if "COMPROVANTE DE PAGAMENTO DE TITULOS" in data_page[0: 300]:

                    
                    for i in range(len(data_page)):
                        
                        index_aux = 0
                        check_aux = False
                        if data_page[i: i+18] == "BENEFICIARIO FINAL":
                            check_aux = True
                        elif data_page[i: i+13] == "NOME FANTASIA":
                            check_aux = True
                        
                        if check_aux:
                            data_aux = data_page[i: i+18]

                            print( data_aux )
                            index_aux = i+21
                            data_extract["beneficiario_final"]["data_init"] = index_aux
                            data_temp = data_page[i:]
                            
                            for j in range(len(data_temp)):
                                if "CPF" in data_temp[j:j+5]:
                                    index_aux = j-1
                                    data_extract["beneficiario_final"]["data_final"] = i + index_aux
                                    init = data_extract["beneficiario_final"]["data_init"]
                                    final = data_extract["beneficiario_final"]["data_final"]
                                    data_extract["beneficiario_final"]["text"] = data_page[ init: final ].strip()
                                    cnpj_aux = data_page[ final-5: final+35 ].strip().split(":")[1].strip()
                                    data_extract["cnpj"]["text"] = cnpj_aux
                                    break
                                elif "CNPJ" in data_temp[j:j+5]:
                                    index_aux = j-1
                                    data_extract["beneficiario_final"]["data_final"] = i + index_aux
                                    init = data_extract["beneficiario_final"]["data_init"]
                                    final = data_extract["beneficiario_final"]["data_final"]
                                    data_extract["beneficiario_final"]["text"] = data_page[ init: final ].strip()
                                    cnpj_aux = data_page[ final-5: final+35 ].strip().split(":")[1].strip()
                                    data_extract["cnpj"]["text"] = cnpj_aux
                                    data_extract["index"]["text"] = index_page
                                    break

                        elif "DATA DE VENCIMENTO" in data_page[i: i+18]:
                            data_extract["data_vencimento"]["text"] = data_page[i+38: i+48]
                            data_extract["data_pagamento"]["text"]  = data_page[i+87: i+97]
                            # ----
                            valor_documento = PrepareDataToImportPackage3703.data_strip(data_page[i+130: i+146])
                            valor_cobrado = PrepareDataToImportPackage3703.data_strip(data_page[i+170: i+195])

                            if valor_documento != valor_cobrado:
                                
                                data_extract["valor_dif"]["text"] = PrepareDataToImportPackage3703.data_strip(data_page[i+170: i+195])
                                # ----
                                valor_cobrado = PrepareDataToImportPackage3703.data_strip(data_page[i+230: i+245])
                                data_extract["tipo_registro"]["text"] = PrepareDataToImportPackage3703.check_discount_or_fees(
                                    document_value=valor_documento,
                                    amount_paid=valor_cobrado)

                            data_extract["valor_documento"]["text"] = PrepareDataToImportPackage3703.data_strip(valor_documento)
                            data_extract["valor_cobrado"]["text"] = PrepareDataToImportPackage3703.data_strip(valor_cobrado)

                            list_data_pages.append(data_extract)
                            print(f"\n\n\n ---------------- { index_page }")
                            print(data_extract)
                            index_page += 1
                            break
                else:
                    list_page_erros.append(index_page)


            except Exception as e:
                print(f" ### ERROR EXTRACT DATA PDF | ERROR: {e}")
                list_page_erros.append({index_page: e})
            
        print(list_data_pages)

        data_to_dataframe = list()
        for data in list_data_pages:
            data_to_dataframe.append({
                "beneficiario_final": data["beneficiario_final"]["text"],
                "cnpj": data["cnpj"]["text"],
                "data_vencimento": data["data_vencimento"]["text"],
                "data_pagamento": data["data_pagamento"]["text"],
                "valor_documento": data["valor_documento"]["text"],
                "valor_cobrado": data["valor_cobrado"]["text"],
                "valor_dif": data["valor_dif"]["text"],
                "tipo_registro": data["tipo_registro"]["text"],
            })
        
        # -------------- CRIAÇÃO DA BASE EM DATAFRAME --------------
        df = pd.DataFrame(data_to_dataframe)

        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_1", cod_empresa=company_session)

        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "CNPJ": "cnpj",
            "NOME": "beneficiario_final",
            "DATA": "data_pagamento",
            })
        df = PrepareDataToImportPackage3703.drop_columns_dataframe(dataframe=df, list_columns=["cnpj", "beneficiario_final", "data_pagamento"])
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows(dataframe=df)

        df.to_excel("comprovante_banco_do_brasil.xlsx")


        df = PrepareDataToImportPackage3703.create_dataframe_discount_and_fees(dataframe=df)

        print(df)
        print(f"\n\n\ {list_page_erros}")
        print(f" TT PAGES: {len(pdf_reader.pages)}")
        df = df.sort_values(by=[ "NOME", "GRUPO_LCTO", "TP" ])
        df.index = list(range(0, len(df.index)))

        df = PrepareDataToImportPackage3703.readjust_values_dataframe(dataframe=df)
        
        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        
        # file_name = r"I:\\1. Gaulke Contábil\\Administrativo\\9. TI\\1. Projetos\\7.  Importação Comp. - Banco do Brasil\\base_extrato_banco_do_brasil.xlsx"
        # PrepareDataToImportPackage3703.convert_dataframe_to_excel(dataframe=df, file_name=file_name)
        data_json = json.loads(df.to_json(orient="table"))
        print(data_json)

        return {
            "data_table": data_json,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
             }
    

    # ----
    # nova versão --> mais otimizada.
    def read_pdf_comprovante_banco_do_brasil_v2(file, company_session):

        print(f"\n\n ----- Arquivo informado comprovante Bradesco V2 | arquivo: {file}")

        contents = file.read()
        pdf_bytes = io.BytesIO(contents)
        pdf_reader = PdfReader(pdf_bytes)

        list_data_pages = list()
        list_page_erros = list()
        index_page = 0
        print(f" TT PAGES: {len(pdf_reader.pages)}")


        data_to_table = {
            # # ---------- IDENTIFICADORES
            "nome_beneficiario": list(),
            "cnpj_beneficiario": list(),

            # "nome_pagador": list(),
            # "cnpj_pagador": list(),

            # # # ---------- DATAS
            "data_de_debito": list(),
            "data_de_vencimento": list(),

            # # ---------- VALORES
            "valor": list(),
            # "desconto": list(),
            # "abatimento": list(),
            # "bonificacao": list(),
            # "multa": list(),
            # "juros": list(),
            "valor_total": list(),

        }

        list_errors = list()
        list_ignore_CPF = list()
        dict_tags_to_text = dict()

        for index_page in range(len(pdf_reader.pages)):
            try:
                print(f"\n\n\n ---- INDEX PAGE: {index_page}")
                

                # dict_tags_to_text = PrepareDataToImportPackage3703.check_text_to_tag(data=data_page, dict_tags_to_text=dict_tags_to_text)
                # print(dict_tags_to_text)

                check_cnpj = 1
                comprovante_pagador = False
                page = pdf_reader.pages[index_page]
                data_page = page.extract_text()

                if "CPF:" in data_page:
                    list_ignore_CPF.append(index_page+1)

                if "COMPROVANTE DE PAGAMENTO DE TITULOS" in data_page and "CPF:" not in data_page:

                    print("\n\n ----------------------- DATA EXTRACT ----------------------- ")
                    print(data_page)
                    
                    for i in range(len(data_page)):
                        
                        # -------------------------- NOME BENEFICIARIO --------------------------
                        if "BENEFICIARIO:" == data_page[i:i+13]:
                            data_temp = data_page[i+14:i+90].split("\n")[1].strip()
                            print(f"\n\n ---------->> NOME BENEFICIARIO")
                            data_to_table["nome_beneficiario"].append( data_temp )

                        if "BENEFICIARIO.:" == data_page[i:i+14]:
                            comprovante_pagador = True
                            data_temp = data_page[i+15:i+90].split("\n")[1].strip()
                            print(f"\n\n ---------->> NOME PAGADOR")
                            data_to_table["nome_beneficiario"].append( data_temp )

                        
                        if "CNPJ:" == data_page[i:i+5]:
                
                            if check_cnpj == 1 and "PAGADOR.:" not in data_page:
                                data_temp = data_page[i+5:i+40].strip()
                                print(f"\n\n ---------->> CNPJ BENEFICIARIO")
                                data_to_table["cnpj_beneficiario"].append( data_temp )
                                check_cnpj += 1
                            
                            elif check_cnpj == 1:
                                data_cnpj = data_page[i+5:i+40].strip()
                                print(f"\n\n\n ------------------------------------ data_cnpj")
                                print(data_cnpj)
                                data_to_table["cnpj_beneficiario"].append( data_cnpj )
                                check_cnpj += 1

                            check_cnpj += 1
                       

                        if "DATA DE VENCIMENTO" == data_page[i:i+18]:
                            data_temp = data_page[i+19:i+48].strip()
                            print(f"\n\n ---------->> DATA DE VENCIMENTO")
                            data_to_table["data_de_vencimento"].append( data_temp[0:] )

                        if "DATA DO PAGAMENTO" == data_page[i:i+17]:
                            data_temp = data_page[i+18:i+48].strip()
                            print(f"\n\n ---------->> DATA DO PAGAMENTO")
                            data_to_table["data_de_debito"].append( data_temp )
                            if comprovante_pagador:
                                data_to_table["data_de_vencimento"].append( data_temp )

                        if "VALOR DO DOCUMENTO" == data_page[i:i+18]:
                            data_temp = data_page[i+19:i+48].strip()
                            print(f"\n\n ---------->> VALOR DO DOCUMENTO")
                            data_to_table["valor"].append( data_temp[0:].replace(".", "").replace(",", ".") )

                        if "VALOR COBRADO" == data_page[i:i+13]:
                            data_temp = data_page[i+13:i+48].strip()
                            print(f"\n\n ---------->> VALOR COBRADO")
                            data_to_table["valor_total"].append( data_temp[0:].replace(".", "").replace(",", ".") )

            except Exception as e:
                print(f" ### ERROR EXTRACT DATA PDF | ERROR: {e}")
                list_page_erros.append({index_page: e})

        print(data_to_table)
        print(f' >>>> nome_beneficiario: {len(data_to_table["nome_beneficiario"])}')
        print(f' >>>> cnpj_beneficiario: {len(data_to_table["cnpj_beneficiario"])}')
        print(f' >>>> data_de_debito: {len(data_to_table["data_de_debito"])}')
        print(f' >>>> data_de_vencimento: {len(data_to_table["data_de_vencimento"])}')
        print(f' >>>> valor: {len(data_to_table["valor"])}')
        print(f' >>>> valor_total: {len(data_to_table["valor_total"])}')
        print(f"\n\n >>>>>>>>>>>>> list_errors: {list_errors}\n\n")
    
        df = pd.DataFrame.from_dict(data_to_table)
        df["valor_doc_decimal"] = df['valor'].astype(float)
        df["valor_pago_decimal"] = df['valor_total'].astype(float)
        df["juros"] = "0.00"
        df["desconto"] = "0.00"
        print(df)
        print(df.info())
        # return {}
        
        for i in df.index:
            try:
                if df["valor_pago_decimal"][i] > df["valor_doc_decimal"][i]:
                    calc = df["valor_pago_decimal"][i] - df["valor_doc_decimal"][i]
                    df["juros"][i] = str(round(calc, 2))
                                    
                elif df["valor_pago_decimal"][i] < df["valor_doc_decimal"][i]:
                    calc = df["valor_doc_decimal"][i] - df["valor_pago_decimal"][i]
                    df["desconto"][i] = str(round(calc, 2))

            except Exception as e:
                print(f" ### ERROR CALC JUROS/DESCONTO: {e}")

        
        print(df)
        print(df.info())

        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_8", value_generic="Banco do Brasil", cod_empresa=company_session)
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "data_de_debito",
            "CNPJ": "cnpj_beneficiario",
            "NOME": "nome_beneficiario",
            "VALOR": "valor",
        })
        # print(df)

        # desconto
        # juros
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "C", "TYPE_PROCESS": "desconto"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
        ])

        df.sort_values(by=["nome_beneficiario", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))

        count_aux = 0
        for i in df.index:

            if count_aux == 0:
                df["TYPE_PROCESS"][i] = "account_code_credit"
                df["VALOR"][i] = df["valor_total"][i]
                count_aux += 1
            elif count_aux == 1:
                df["VALOR"][i] = df["desconto"][i]
                df["CONTA"][i] = "936"
                count_aux += 1
            elif count_aux == 2:
                df["VALOR"][i] = df["juros"][i]
                df["CONTA"][i] = "947"
                count_aux += 1
            elif count_aux == 3:
                df["TYPE_PROCESS"][i] = "account_code_debit"
                df["VALOR"][i] = df["valor"][i]
                df["CONTA"][i] = ""
                count_aux = 0

        df = PrepareDataToImportPackage3703.adjust_value_to_decimal_string(dataframe=df, column_name="VALOR", replace_caract=True)
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])

        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

        print("\n\n\n ------------ DF LAYOUT JB ------------ ")
        print(df)
        print(df.info())

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))
        print(dict_tags_to_text)

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        print(f"\n\n ---------- list_ignore_CPF ---------- ")
        print(f">> list_ignore_CPF: {list_ignore_CPF}")
        show_ignore_CPF = False
        if len(list_ignore_CPF) > 0:
            show_ignore_CPF = True
        
        return {
            "data_table": data_json,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_ignore_CPF": list_ignore_CPF,
            "show_ignore_CPF": show_ignore_CPF,
            "list_page_erros": [],
        }


    # ----
    
    def read_pdf_relacao_folha_por_empregado(file, grupo_lancamento, company_session):
        try:
            print(f"\n\n ----- Arquivo informado folha de pagamento: {file}")
            contents = file.read()
            pdf_bytes = io.BytesIO(contents)      

            data = tabula.read_pdf(pdf_bytes, pages="all")
            print(" <<<< ----------------- >>>> ")
            print(data)
            print(" <<<< ----------------- >>>> ")
            list_df = list()

            for i in range(len(data)):
                # contrib = data[i][ data[i]["Código Nome do empregado"] == "Contribuintes" ]
                df_aux = data[i]
                

                for j in df_aux.index:
                    index = 0
                    if "Contribuintes:" in df_aux["Código Nome do empregado"][j]:
                        index = j
                        df_aux = df_aux[df_aux.index < index]
                        print(f" \n\n ---------------- FILTER df_aux CONTRIBUINTES ---------------- INDEX: {index} \n\n")
                        break
                    elif "Empregados:" in df_aux["Código Nome do empregado"][j]:
                        index = j
                        df_aux = df_aux[df_aux.index < index]
                        print(f" \n\n ---------------- FILTER df_aux EMPREGADOS ---------------- INDEX: {index} \n\n")
                        break
                
                print(f"\n\n ----> INDEX LIST: {i}")
                print(df_aux)
                list_df.append(df_aux)
                print(f"\n\n ------------------------- LIST DF: {len(list_df)}")
            
            print(list_df)
            df = pd.concat(list_df)
            
            df.index = list(range(0, len(df.index)))
            
            # df.dropna(subset=["Líquido"],  inplace=True)
            
            df[['ID', 'NOME_TEMP']] = df['Código Nome do empregado'].str.split(' ', n=1, expand=True)

            # ----
            df = PrepareDataToImportPackage3703.drop_columns_dataframe(dataframe=df, list_columns=["Unnamed: 0", "Código Nome do empregado"])
            print("\n\n ******************************************** ")
            print(df)
            
            df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_2", grupo_lancamento=grupo_lancamento, cod_empresa=company_session)
            df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
                "VALOR": "Líquido",
                })

            df = PrepareDataToImportPackage3703.filter_data_dataframe(
                daraframe=df,
                name_column="VALOR",
                list_remove_values=["0.00", "0,00"])
            df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
                "NOME": "NOME_TEMP",
            })
            
            # df = PrepareDataToImportPackage3703.drop_columns_dataframe(dataframe=df, list_columns=["NOME_TEMP"])

            df = PrepareDataToImportPackage3703.duplicate_dataframe_rows(dataframe=df)
            df = df.sort_values(by=[ "NOME", "GRUPO_LCTO", "TP" ])
            print(" ***** ---------------------------- ***** ")

            df.index = list(range(0, len(df.index)))
            df = df.dropna(subset=["VALOR"])
            df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

            count = 0
            for i in df.index:
                if count == 0:
                    df["TYPE_PROCESS"][i] = "account_code_credit"
                    count += 1
                elif count == 1:
                    df["TYPE_PROCESS"][i] = "account_code_debit"
                    count = 0
                

                df["VALOR"][i] = df["VALOR"][i].replace(".", "").replace(",", ".")
                if df["VALOR"][i] == "0":
                    df["VALOR"][i] = "0.00"
                elif "." in df["VALOR"][i]:
                    if df["VALOR"][i][-2] == ".":
                        df["VALOR"][i] = df["VALOR"][i] + "0"
                    elif df["VALOR"][i][-3] == ".":
                        pass
                else:
                    df["VALOR"][i] = df["VALOR"][i] + ".00"



            print(df)

            tt_rows = len(df)
            tt_debit    = len(df[df["TP"] == "D"])
            tt_credit   = len(df[df["TP"] == "C"])

            print(f"""
                --------- CONFIG CONTAS
                tt_rows: {tt_rows}
                tt_debit: {tt_debit}
                tt_credit: {tt_credit}
            """)
            
            # df.to_excel("df_folha_pagamento.xlsx")
            data_json = json.loads(df.to_json(orient="table"))
            # print(data_json)

            return {
                "data_table": data_json,
                "tt_rows": tt_rows,
                "tt_debit": tt_debit,
                "tt_credit": tt_credit,
                "list_page_erros": [],
                }
        except Exception as e:
            print(f"\n\n ### ERROR CREATE DF IMPORT JB | ERROR: {e}")
            return None
      

    # ----
    
    def read_xlsx_relacao_gnre(file, data_contas, company_session):

        print(f"\n\n ----- Arquivo informado GNRE: {file}")
        contents = file.read()
        xlsx_bytes = io.BytesIO(contents)

        print("\n\n ---------------------------------------------- DF READ - STEP 1 ")

        file = pd.ExcelFile(xlsx_bytes)
        sheet_name = file.sheet_names[0]

        print("\n\n ---------------------------------------------- DF READ - STEP 2 ")

        df = file.parse(sheet_name=sheet_name, dtype='str')

        print("\n\n ---------------------------------------------- DF READ - STEP 3 ")
        print(df)

        print("\n\n ---------------------------------------------- DF READ - STEP 4 ")
        df = pd.read_excel(xlsx_bytes)
        df.rename(columns={
            "C笈_UF_IN沊IO_PREST": "UF_INÍCIO",
            "C笈_UF_FIM_PREST": "UF_FIM",
            "N渧ERO_CTE": "CTE",
            "DATA_EMISS鬃": "DATA_EMISSÃO"
        }, inplace=True)
        
        print("\n\n ---------------------------------------------- DF READ - STEP 5 ")

        df = df[(df["UF_INÍCIO"] != "SC") & (df["SITUACAO"] != "CANCELADO")]

        print("\n\n ---------------------------------------------- DF READ - STEP 6 ")

        df = df[["CTE", "DATA_EMISSÃO", "VALOR_ICMS", "UF_INÍCIO", "UF_FIM"]]

        print("\n\n ---------------------------------------------- DF READ - STEP 6 ")


        df = PrepareDataToImportPackage3703.filter_columns_dataframe(daraframe=df, list_columns=["CTE", "DATA_EMISSÃO","VALOR_ICMS", "UF_INÍCIO", "UF_FIM"])

        print("\n\n ---------------------------------------------- DF READ - STEP 7 ")

        df['VALOR_ICMS'] = df['VALOR_ICMS'].round(2)
        df["VALOR_ICMS"] = df['VALOR_ICMS'].astype(str)

        print(df.info())
        
        for i in df.index:
            if "." not in df["VALOR_ICMS"][i]:
                df["VALOR_ICMS"][i] = df["VALOR_ICMS"][i] + ".00"
            elif df["VALOR_ICMS"][i].split(".")[1] in ['0','1','2','3','4','5','6','7','8','9']:
                print(" -------------- SPLIT ")
                df["VALOR_ICMS"][i] = df["VALOR_ICMS"][i] + "0"
            
            print(">>>>> ", df["VALOR_ICMS"][i], type( df["VALOR_ICMS"][i] ) )
        
        df.dropna(subset=["CTE"], inplace=True)
        df["CTE"] = list(map(lambda x: int(x), df["CTE"].values))
        

        print(" ----------------  STEP ADJUST DT ---------------- ")
        print(df.info())
        dt = pd.to_datetime(df['DATA_EMISSÃO'])
        formatted_date = dt.dt.strftime("%d/%m/%Y")
        df['DATA_EMISSÃO'] = formatted_date
        

        print(df)
        
        file.close()

        print(" <<<< --------- GNRE --------- >>>> ")
        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_3", cod_empresa=company_session)
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "VALOR": "VALOR_ICMS",
            "DATA": "DATA_EMISSÃO",
            })
        # ----
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00", "0,00"])
        # ----
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows(dataframe=df)
        df = PrepareDataToImportPackage3703.create_additional_columns(dataframe=df, column_name="NUMERO_CONTA_CONTABIL", default_value="-")

        df = df.sort_values(by=[ "CTE", "TP" ])
        print(" <<<< ---------------------------- >>>> ")

        df.index = list(range(0, len(df.index)))

        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

        for i in range(len(df.index)):

            uf_inicio = df["UF_INÍCIO"][i]
            print(f" ----> INDEX REPLACE ACCOUNTS VALUES: {i} | uf_inicio: {uf_inicio}")

            conta_debito = data_contas.get(uf_inicio)["conta_debito"]
            conta_credito = data_contas.get(uf_inicio)["conta_credito"]

            print(f"""
                --------- CONFIG CONTAS POR UF
                --> uf_inicio: {uf_inicio}
                --> conta_debito: {conta_debito}
                --> conta_credito: {conta_credito}
            """)
            
            if df["TP"][i] == "C":
                df["NUMERO_CONTA_CONTABIL"][i] = conta_credito
            elif df["TP"][i] == "D":
                df["NUMERO_CONTA_CONTABIL"][i] = conta_debito

        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "CONTA": "NUMERO_CONTA_CONTABIL",
        })

        print(df)
        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])


        print(f"""
            --------- CONFIG CONTAS POR UF
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        # file_name = r"I:\\1. Gaulke Contábil\\Administrativo\\9. TI\\1. Projetos\\2. Importação GNRE\NOVO MODELO AUTOMACAO\\base_GNRE.xlsx"
        # PrepareDataToImportPackage3703.convert_dataframe_to_excel(dataframe=df, file_name=file_name)
        print(" <<<< ----------------- >>>> ")

        data_json = json.loads(df.to_json(orient="table"))
        # print(data_json)

        return {
            "data_table": data_json ,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
             }
    
    # ----
    
    def read_pdf_relacao_entrada_titulos_desc_sicoob(file, company_session):
        try:
            print(f"\n\n ----- Arquivo informado SICOOB: {file}")

            contents = file.read()
            pdf_bytes = io.BytesIO(contents)
            dataframes = tabula.read_pdf( pdf_bytes, pages="all" )

            list_df = list()
            for df in dataframes:
                # print(" ------------------------ df ------------------------ ")
                # print(df)
                list_df.append(df)
            
            df = pd.concat(list_df)
            df.index = list(range(0, len(df.index)))

            print(" <<<< ----------------- >>>> ")

            print(df)

            df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
                "NOME": "Sacado",
                "VALOR": "Valor (R$)",
                "DATA_VENCIMENTO": "Vencimento",
                "DT_LIMITE_PGTO": "Dt. Limite Pgto",
                "NOSSO_NUMERO": "Nosso Número",
                "SEU_NUMERO": "Seu Número",
                })
            df = PrepareDataToImportPackage3703.readjust_values_dataframe_decimal(dataframe=df, list_cols_name=["VALOR"], replace_values_list=False)
            df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_5", value_generic="Sicoob", cod_empresa=company_session)
            df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
                "DATA": "Entrada",
                "VALOR": "Valor (R$)",
                })
            
            df = PrepareDataToImportPackage3703.duplicate_dataframe_rows(dataframe=df)
            df.index = list(range(0, len(df.index)))
            for i in df.index:
                if df["TP"][i] == "C":
                    print(df["TP"][i], "524")
                    df["CONTA"][i] = "524"
                elif df["TP"][i] == "D":
                    print(df["TP"][i], "11")
                    df["CONTA"][i] = "11"
            

            df = df.sort_values(by=[ "NOME", "NOSSO_NUMERO", "TP" ])

            # file_name = "base_entrada_titulos_desc_sicoob.xlsx"
            # PrepareDataToImportPackage3703.convert_dataframe_to_excel(dataframe=df, file_name=file_name)
            df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)
            
            tt_rows = len(df)
            tt_debit    = len(df[df["TP"] == "D"])
            tt_credit   = len(df[df["TP"] == "C"])
            data_json = json.loads(df.to_json(orient="table"))
            print(data_json)
            print(f"""
                --------- CONFIG CONTAS POR UF
                --> tt_rows: {tt_rows}
                --> tt_debit: {tt_debit}
                --> tt_credit: {tt_credit}
            """)

            return {
                "data_table": data_json ,
                "tt_rows": tt_rows,
                "tt_debit": tt_debit,
                "tt_credit": tt_credit,
                "list_page_erros": [],
                }
        except Exception as e:
            print(f" ### ERROR GENERATE DATAFRAME | ERROR: {e}")

    # ----
          
    def read_pdf_relacao_liquidacao_titulos_desc_sicoob(file, file_2, company_session):
        try:
            print(f"\n\n ----- Arquivo informado Liquid. Títulos Desc. SICOOB: {file} | file_2 (S@T): {file_2}")

            contents = file.read()
            pdf_bytes = io.BytesIO(contents)
            dataframes = tabula.read_pdf( pdf_bytes, pages="all" )
            df = pd.concat(dataframes)

            type_09 = False
            if "Unnamed: 9" in df.columns:
                type_09 = True
                df_temp = df.dropna(subset=["Unnamed: 9"])
                print(" ----------------- df_temp | Unnamed: 9 ----------------- ")
                print(df_temp)
                for i in df.index:
                    try:
                        df["Unnamed: 0"][i] = df_temp["Unnamed: 0"][i]
                        df["Unnamed: 1"][i] = df_temp["Unnamed: 2"][i]
                        df["Unnamed: 2"][i] = df_temp["Unnamed: 3"][i]
                        df["Unnamed: 3"][i] = df_temp["Unnamed: 4"][i]
                        df["Dt. Previsão"][i] = None
                        df["Unnamed: 4"][i] = df_temp["Unnamed: 5"][i]
                        df["Dt. Limite"][i] = None
                        df["Unnamed: 5"][i] = df_temp["Unnamed: 6"][i]
                        df["Unnamed: 6"][i] = df_temp["Unnamed: 7"][i]
                        df["Unnamed: 7"][i] = df_temp["Unnamed: 8"][i]
                        df["Vlr. Outros"][i] = None
                        df["Unnamed: 8"][i] = df_temp["Unnamed: 9"][i]
                    except:
                        pass
                df.drop(columns=['Unnamed: 9'], inplace=True)



            df = df.dropna(subset=["Unnamed: 2"])
            df = df[ df["Unnamed: 1"] != "Nosso Número" ]
            df["Vlr. Outros"].fillna("0,00", inplace=True)
            df.index = list(range(0, len(df.index)))

            df.columns = [
                "nome_beneficiario", "nosso_numero", "seu_numero", "dt_previsao_credito", "vencimento", "dt_limite_pag", "valor", "mora", "desconto", "outros_valores", "dt_liquidacao", "valor_cobrado"
            ]
            df["seu_numero_original"] =  df["seu_numero"]

            if type_09:
                df["col1"] = df["outros_valores"]
                df["col2"] = df["dt_liquidacao"]
                df["dt_liquidacao"] = df["col1"]
                df["outros_valores"] = df["col2"]
                df["valor"] = df["dt_limite_pag"]
                df["dt_limite_pag"] = None


            # df.to_excel("base_type_09.xlsx")
            # return {}
            
            # --------------------------------------------------------------
            contents = file_2.read()
            xlsx_bytes = io.BytesIO(contents)
            file_2 = pd.ExcelFile(xlsx_bytes)
            sheet_name = file_2.sheet_names[0]
            df_SAT = file_2.parse(sheet_name=sheet_name, dtype='str')[["CnpjOuCpfDoDestinatario", "NomeDestinatario", "NumeroDocumento"]]
            
            print("\n\n ----------------- df ----------------- ")
            print(df)
            print("\n\n ----------------- df_SAT ----------------- ")
            print(df_SAT)
            # df.to_excel("df.xlsx")
            # df_SAT.to_excel("df_SAT.xlsx")
            # return {}

            for i in df.index:
                if "MN" in df["seu_numero"][i]:
                    df["seu_numero"][i] = str(df["seu_numero"][i].replace("MN", ""))
                else:
                    df["seu_numero"][i] = str(df["seu_numero"][i][1: len(df["seu_numero"][i])-1])
            
            print(" -------------------------------------- df | FINAL -------------------------------------- ")
            
            df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_21", value_generic="Sicoob", cod_empresa=company_session)
            df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
                "DATA": "dt_liquidacao",
                "VALOR": "valor",
                "NOME": "nome_beneficiario",
                })
            
            df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
                {"TP": "D", "TYPE_PROCESS": "comum"},
                {"TP": "C", "TYPE_PROCESS": "mora"},
                {"TP": "C", "TYPE_PROCESS": "juros"},
                {"TP": "D", "TYPE_PROCESS": "desconto"},
            ])

            df.sort_values(by=["nome_beneficiario", "GRUPO_LCTO", "TP"], inplace=True)
            df.index = list(range(0, len(df.index)))

            # df.to_excel("base_liquidacao_titulos_desc_sicoob - consolidado.xlsx")
            # return {}

            count_aux = 0
            for i in df.index:
                
                if count_aux == 0:
                    df["TP"][i] = "D"
                    df["TYPE_PROCESS"][i] = "account_code_debit"
                    df["VALOR"][i] = df["valor_cobrado"][i]
                    count_aux += 1
                elif count_aux == 1:
                    df["TP"][i] = "D"
                    df["TYPE_PROCESS"][i] = "desconto"
                    df["VALOR"][i] = df["desconto"][i]
                    df["CONTA"][i] = "1686"
                    count_aux += 1
                elif count_aux == 2:
                    df["TP"][i] = "C"
                    df["TYPE_PROCESS"][i] = "mora"
                    df["VALOR"][i] = df["mora"][i]
                    df["CONTA"][i] = "1663"
                    count_aux += 1
                elif count_aux == 3:
                    df["TP"][i] = "C"
                    df["TYPE_PROCESS"][i] = "juros"
                    df["VALOR"][i] = df["outros_valores"][i] # juros
                    df["CONTA"][i] = "1663"
                    count_aux += 1
                elif count_aux == 4:
                    df["TP"][i] = "C"
                    df["TYPE_PROCESS"][i] = "comum"
                    df["VALOR"][i] = df["valor"][i]
                    df["CONTA"][i] = ""
                    count_aux = 0
                

                if df["VALOR"][i] == None:
                    df["VALOR"][i] = "0.00"
                else:
                    df["VALOR"][i] = df["VALOR"][i].replace(".", "").replace(",", ".")
                # --------------------------------------------------------------------------------------------------------------
                numeroNF = df["seu_numero"][i]
                try:
                    CnpjOuCpfDoDestinatario = df_SAT[df_SAT["NumeroDocumento"] == numeroNF]["CnpjOuCpfDoDestinatario"].values[0]
                    NomeDestinatario        = df_SAT[df_SAT["NumeroDocumento"] == numeroNF]["NomeDestinatario"].values[0]
                    # NumeroDocumento         = df_SAT[df_SAT["NumeroDocumento"] == numeroNF]["NumeroDocumento"].values[0]
                    
                    df["NOME"][i] = NomeDestinatario
                    df["CNPJ"][i] = CnpjOuCpfDoDestinatario

                except Exception as e:
                    # print(f"\n\n ### ERROR GET NF | ERROR: {e}")
                    pass

            # print(df)
            # print(df.info())
            # return{}
                        
            df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])
            df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

            # df.to_excel("base_liquidacao_titulos_desc_sicoob - consolidado.xlsx")
            # df.sort_values(by=["NOME", "GRUPO_LCTO", "TP"], inplace=True)
            # df.index = list(range(0, len(df.index)))

            print("\n\n ------------------------ df_JB ------------------------ ")
            print(df)
            print(df.info())


            # -------------------------
            print("\n\n ------------------------ df_SAT ------------------------ ")
            print(df_SAT)
            print(df_SAT.info())

            tt_rows = len(df)
            tt_debit    = len(df[df["TP"] == "D"])
            tt_credit   = len(df[df["TP"] == "C"])
            data_json = json.loads(df.to_json(orient="table"))
            # print(data_json)
            print(f"""
                --------- CONFIG CONTAS POR UF
                --> tt_rows: {tt_rows}
                --> tt_debit: {tt_debit}
                --> tt_credit: {tt_credit}
            """)

            return {
                "data_table": data_json,
                "tt_rows": tt_rows,
                "tt_debit": tt_debit,
                "tt_credit": tt_credit,
                "list_page_erros": [],
                }
        except Exception as e:
            print(f" ### ERROR GENERATE DATAFRAME | ERROR: {e}")
        
    
    # ----
    
    def read_pdf_relacao_relatorio_beneficiario_CIVIA(file, company_session):

        print(f"\n\n ----- Arquivo informado relatório beneficiário CIVIA: {file}")

        contents = file.read()
        pdf_bytes = io.BytesIO(contents)
        pdf_reader = PdfReader(pdf_bytes)

        list_data_pages = list()
        list_page_erros = list()
        index_page = 0
        print(f" TT PAGES: {len(pdf_reader.pages)}")


        data_to_table = {
            # # ---------- IDENTIFICADORES
            "nome_beneficiario": list(),
            "cnpj_beneficiario": list(),

            # "nome_pagador": list(),
            # "cnpj_pagador": list(),

            # # # ---------- DATAS
            "data_de_debito": list(),
            "data_de_vencimento": list(),

            # # ---------- VALORES
            "valor": list(),
            "desconto": list(),
            # "abatimento": list(),
            # "bonificacao": list(),
            # "multa": list(),
            "juros": list(),
            "valor_total": list(),
            "N_Documento": list(),

        }

        list_errors = list()
        list_ignore_CPF = list()
        dict_tags_to_text = dict()

        for index_page in range(len(pdf_reader.pages)):
            try:

                page = pdf_reader.pages[index_page]
                data_page = page.extract_text()

                print(f"\n\n\n ---- DATA EXTRACT | INDEX PAGE: {index_page}")
                # print(data_page)
                
                for i in range(len(data_page)):
                    
                    # -------------------------- NOME BENEFICIARIO --------------------------

                    if "CPF/CNPJ:" == data_page[i:i+9]:
                        print(f"\n\n ---------->> CPF/CNPJ BENEFICIARIO | i: {i}")
                        data_aux = data_page[i:]
                        print(data_aux)
                        
                        delimiter_row = 0
                        for j in range(len(data_aux)):
                            if "DIFERENÇA" == data_aux[j:j+9]:
                                delimiter_row += j
                                break
                        
                        print("\n\n início --------------------------------------- ", i, " / ", delimiter_row + i)
                        data_temp = data_page[ i: delimiter_row + i].strip()
                        print(data_temp)
                        data_split = data_temp.split("\n")
                        nome = data_split[0].replace("CPF/CNPJ:", "")
                        cnpj = data_split[1]
                        data_values = data_split[3:]

                        for values in data_values:
                            data = values.split()
                            print(f" >>> nome: {nome}")
                            print(f" >>> cnpj: {cnpj}")
                            Nosso_Numero    = data[0]
                            N_Documento     = data[1]
                            Situacao        = data[2]
                            Emis_Bco_Age    = data[3]

                            if "LIQUIDADO" in Situacao.upper():
                                Emissao = data[4]
                                Documento       = data[5]
                                Vencimento      = data[6]
                                Pagto_Baixa     = data[7]
                                Valor_Nominal   = data[8].replace(".", "").replace(",", ".")
                                Valor_Liquidado = data[9].replace(".", "").replace(",", ".")
                                Diferença       = data[10].replace(".", "").replace(",", ".")

                            else:
                                Emissao = data[4+2]
                                Documento       = data[5+2]
                                Vencimento      = data[6+2]
                                Pagto_Baixa     = data[7+2]
                                Valor_Nominal   = data[8+2].replace(".", "").replace(",", ".")
                                Valor_Liquidado = data[9+2].replace(".", "").replace(",", ".")
                                Diferença       = data[10+2].replace(".", "").replace(",", ".")

                            if Situacao.upper() == "LIQUIDADO":

                                desconto = "0.00"
                                juros = "0.00"


                                # print(data)

                                # print(f""""
                                #     ----------------------------
                                #     Nosso_Numero: {Nosso_Numero}
                                #     N_Documento: {N_Documento}
                                #     Situacao: {Situacao}
                                #     Emis_Bco_Age: {Emis_Bco_Age}
                                #     Emissao: {Emissao}
                                #     Documento: {Documento}
                                #     Vencimento: {Vencimento}
                                #     Pagto_Baixa: {Pagto_Baixa}
                                # """)



                                if float(Diferença) > 0:
                                    juros = Diferença
                                elif float(Diferença) < 0:
                                    desconto = Diferença

                                data_to_table["nome_beneficiario"].append(nome)
                                data_to_table["cnpj_beneficiario"].append(cnpj)
                                data_to_table["data_de_debito"].append(Emissao)
                                data_to_table["data_de_vencimento"].append(Documento)
                                data_to_table["valor"].append(Valor_Nominal)
                                data_to_table["desconto"].append(desconto)
                                data_to_table["juros"].append(juros)
                                data_to_table["valor_total"].append(Valor_Liquidado)
                                data_to_table["N_Documento"].append(N_Documento)

                            print(" --------------------------------------- final \n\n")

                        
                        

            except Exception as e:
                print(f" ### ERROR EXTRACT DATA PDF | ERROR: {e}")
                list_page_erros.append({index_page: e})       
    
        df = pd.DataFrame.from_dict(data_to_table)
        print(df)
        print(df.info())


        # return {}
    
        try:
            df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_17", value_generic="Civia", cod_empresa=company_session)
            df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
                "DATA": "data_de_debito",
                "CNPJ": "cnpj_beneficiario",
                "NOME": "nome_beneficiario",
                "VALOR": "valor",
            })
        except Exception as e:
            print(f" ### ERROR: {e} ###")
            return {}


        try:
            df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
                {"TP": "C", "TYPE_PROCESS": "comum"},
                {"TP": "C", "TYPE_PROCESS": "desconto"},
                {"TP": "D", "TYPE_PROCESS": "juros"},
            ])
        except Exception as e:
            print(f" ### ERROR: {e} ###")
            return {}

        df.sort_values(by=["nome_beneficiario", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))


        count_aux = 0
        for i in df.index:

            if count_aux == 0:
                df["VALOR"][i] = df["valor_total"][i]
                df["TP"][i] = "D"
                count_aux += 1
            elif count_aux == 1:
                df["VALOR"][i] = df["desconto"][i]
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("Recebimento Dupl", "Desconto Concedido na Dupl ")
                df["TP"][i] = "D"
                df["CONTA"][i] = "1686"
                count_aux += 1
            elif count_aux == 2:
                df["VALOR"][i] = df["juros"][i]
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("Recebimento Dupl", "Juros/Mora Recebidos na Dupl ")
                df["TP"][i] = "C"
                df["CONTA"][i] = "1663"
                count_aux += 1
            elif count_aux == 3:
                df["VALOR"][i] = df["valor"][i]
                df["TP"][i] = "C"
                df["CONTA"][i] = ""
                count_aux = 0

        # df = PrepareDataToImportPackage3703.adjust_value_to_decimal_string(dataframe=df, column_name="VALOR", replace_caract=True)
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

        # df.to_excel("teste.xlsx")


        print("\n\n\n ------------ DF LAYOUT JB ------------ ")
        try:
            df = PrepareDataToImportPackage3703.check_date_business_day(dataframe=df, column_date="DATA", addition=0)
            print(df)
            print(df.info())
        except Exception as e:
            print(f" ### ERROR: {e} ###")
            return {}

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])
        

        data_json = json.loads(df.to_json(orient="table"))
        print(dict_tags_to_text)

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        print(f"\n\n ---------- list_ignore_CPF ---------- ")
        print(f">> list_ignore_CPF: {list_ignore_CPF}")
        show_ignore_CPF = False
        if len(list_ignore_CPF) > 0:
            show_ignore_CPF = True
        
        return {
            "data_table": data_json,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_ignore_CPF": list_ignore_CPF,
            "show_ignore_CPF": show_ignore_CPF,
            "list_page_erros": [],
        }

    def check_date_business_day(dataframe, column_date, addition=0):
        

        print(" ------------------------ dataframe ------------------------ ")
        dataframe["ADJUSTED_DATE"] = pd.to_datetime(dataframe[column_date], format="%d/%m/%Y")
        dataframe['day_of_week'] = pd.to_datetime(dataframe['ADJUSTED_DATE']).dt.dayofweek
        print(dataframe)

        for i in dataframe.index:
            addition = 0
            try:
                if dataframe["day_of_week"][i] == 4:
                    addition = 3
                elif dataframe["day_of_week"][i] == 5:
                    addition = 2
                elif dataframe["day_of_week"][i] == 6:
                    addition = 1
                else:
                    addition = 1
                dt_adj = dataframe["ADJUSTED_DATE"][i] + pd.Timedelta(days=addition)
                dt_adj = datetime.datetime.strftime(dt_adj, "%d/%m/%Y")
                dataframe["DATA"][i] = dt_adj
                print(f'{dataframe["ADJUSTED_DATE"][i]} >>> dia da semana: {dataframe["day_of_week"][i]} | dt_adj: {dt_adj} | addition: {addition} ')

            except Exception as e:
                print(f" ### ERROR GET DAY OF WEEK | ERROR: {e}")    


        return dataframe
            
    
    # ----
    
    def read_xlsx_relacao_cobrancas_pagas(file, company_session):
        try:
            print(f"\n\n ----- Arquivo informado cobranças pagas: {file}")
            contents = file.read()
            xlsx_bytes = io.BytesIO(contents)

            file = pd.ExcelFile(xlsx_bytes)
            sheet_name = file.sheet_names[0]
            df = file.parse(sheet_name=sheet_name)
            df = df.rename(columns=df.iloc[0]).drop(df.index[0])
            df.index = list(range(0, len(df.index)))

            df = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df, dict_replace_names={
                "CPF/CNPJ": "CNPJ",
                })
            df = PrepareDataToImportPackage3703.readjust_values_dataframe_decimal(dataframe=df, list_cols_name=["Valor", "Valor pago"])
            df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_4", cod_empresa=company_session)


            df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
                "VALOR": "Valor",
                "VALOR_PAGO": "Valor pago",
                })
            
            df = PrepareDataToImportPackage3703.duplicate_dataframe_rows(dataframe=df)
                       
            df = PrepareDataToImportPackage3703.create_dataframe_discount_and_fees_cobrancas_pagas(dataframe=df)

            df.index = list(range(0, len(df.index)))

            for i in df.index:
                if df["TP"][i] == "C" and df["TYPE_PROCESS"][i] == "comum":
                    df["VALOR"][i]  = str(df["VALOR"][i])
                # ----
                elif df["TP"][i] == "D" and df["TYPE_PROCESS"][i] == "comum":
                    df["VALOR"][i]  = str(df["VALOR_PAGO"][i])
                # ----
                elif df["TYPE_PROCESS"][i] != "comum":
                    value_aux = float(df["VALOR_PAGO"][i])
                    if value_aux < 1:
                        value_aux = str(value_aux).replace(",", ".")
                    else:
                        value_aux = str(value_aux).replace(".", "").replace(",", ".")
                    
                    df["VALOR"][i]  = value_aux
            
            df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)
            df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
                "DATA": "Vencimento",
                "NOME": "Nome Cliente",
            })

            df.to_excel("df_wb_telecom.xlsx")

            for i in df.index:
                if df["TYPE_PROCESS"][i] == "process_juros":
                    df["TYPE_PROCESS"][i] = "account_code_debit_juros"
                elif df["TYPE_PROCESS"][i] == "process_desconto":
                    df["TYPE_PROCESS"][i] = "account_code_credit_desconto"
                elif df["TYPE_PROCESS"][i] == "comum" and df["TP"][i] == "D":
                    df["TYPE_PROCESS"][i] = "account_code_debit"
                elif df["TYPE_PROCESS"][i] == "comum" and df["TP"][i] == "C":
                    df["TYPE_PROCESS"][i] = "account_code_credit"
                

                df["VALOR"][i] = str(df["VALOR"][i])
                if df["VALOR"][i] == "0":
                    df["VALOR"][i] = "0.00"
                elif "." in df["VALOR"][i]:
                    
                    if df["VALOR"][i][-2] == ".":
                        df["VALOR"][i] = df["VALOR"][i] + "0"
                    
                    elif df["VALOR"][i][-3] == ".":
                        pass
                else:
                    df["VALOR"][i] = df["VALOR"][i] + ".00"

            df.sort_values(by=["COMPL_HISTORICO", "VALOR"], inplace=True)

            tt_rows = len(df)
            tt_debit    = len(df[df["TP"] == "D"])
            tt_credit   = len(df[df["TP"] == "C"])
            data_json = json.loads(df.to_json(orient="table"))
            # print(data_json)

            print(f"""
                --------- CONFIG CONTAS
                --> tt_rows: {tt_rows}
                --> tt_debit: {tt_debit}
                --> tt_credit: {tt_credit}
            """)

            return {
                "data_table": data_json ,
                "tt_rows": tt_rows,
                "tt_debit": tt_debit,
                "tt_credit": tt_credit,
                "list_page_erros": [],
                }

            
        except Exception as e:
            print(f" \n\n ERROR GENERATE COBRANÇAS PAGAS | ERROR: {e}")
            return {"code": 500, "msg": "erro ao gerar pacote cobranças pagas.", "error": e}
    
    # ----
    
    def read_xlsx_decorise(file, grupo_lancamento, company_session):
        try:
            print(f"\n\n ----- Arquivo informado decorise: {file} | grupo_lancamento: {grupo_lancamento}")
            contents = file.read()
            xlsx_bytes = io.BytesIO(contents)

            file = pd.ExcelFile(xlsx_bytes)
            sheet_name = file.sheet_names[-1]
            df = file.parse(sheet_name=sheet_name)
            print(df.columns)
            df = PrepareDataToImportPackage3703.filter_columns_dataframe(daraframe=df, list_columns=[
                "Conf. Gateway",
                "Id",
                "Valor Recebível",
                "Valor Total",
                "Comissão Paga",
                "Data/Hora",
                "Data Esperada",
            ])

            # df["Data/Hora"] = pd.to_datetime(df["Data/Hora"].values, errors="raise", format="%d/%m/%Y %H:%M:%S")
            df["Data/Hora"] = list(map(lambda x: x.split()[0], df["Data/Hora"].values ))
            df = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df, dict_replace_names={
                "Data/Hora": "DATA_TEMP"
            })
            df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_6", grupo_lancamento=grupo_lancamento, cod_empresa=company_session)

            #  ----------------------- necessário para criar o Dataframe de Commissões -----------------------
            df_commission  = df.copy()
            df_commission = df_commission[ df_commission["TP"] == "D" ]
            df = PrepareDataToImportPackage3703.duplicate_dataframe_rows(dataframe=df)
            df = pd.concat([df, df_commission])
            # ------------------------------------------------------------------------------------------------

            df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
                "DATA": "DATA_TEMP",
                "VALOR": "Valor Recebível",
            })


            df.sort_values(by=["Id", "VALOR", "TP"], inplace=True)
            df.index = list( range(0, len(df.index)) )

            # df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

            #  REAJUSTE DO VALOR DE COD_HISTORICO, necessário para não ser enviado com o valor de grupo_lancamento.
            df = PrepareDataToImportPackage3703.create_additional_columns(dataframe=df, column_name="COD_HISTORICO", default_value="")

            cont_aux = 0
            for i in df.index:

                print(f' ------ INDEX LOOP VALUES: {i}| {df["VALOR"][i]}')
                if cont_aux == 0:
                    df["CONTA"][i] = "2245"
                    df["VALOR"][i] = df["Valor Total"][i]
                    df["TYPE_PROCESS"][i] = "account_code_credit"
                    cont_aux += 1
                elif cont_aux == 1:
                    df["CONTA"][i] = "353"
                    df["VALOR"][i] = df["Valor Recebível"][i]
                    df["TYPE_PROCESS"][i] = "account_code_debit_recebivel"
                    cont_aux += 1
                elif cont_aux == 2:
                    df["CONTA"][i] = "946"
                    df["VALOR"][i] = df["Comissão Paga"][i]
                    df["TYPE_PROCESS"][i] = "account_code_debit_comissao"
                    cont_aux = 0

            
            df['VALOR'] = df['VALOR'].round(2)
            df["VALOR"] = df['VALOR'].astype(str)

            for i in df.index:
                if "." not in df["VALOR"][i]:
                    df["VALOR"][i] = df["VALOR"][i] + ".00"
                elif df["VALOR"][i].split(".")[1] in ['0','1','2','3','4','5','6','7','8','9']:
                    print(" -------------- SPLIT ")
                    df["VALOR"][i] = df["VALOR"][i] + "0"
                
                print(">>>>> ", df["VALOR"][i], type( df["VALOR"][i] ) )


            # file_name = r"I:\\1. Gaulke Contábil\\Administrativo\\9. TI\\1. Projetos\\6. Importação DECORISE\\base_test_Leonardo.xlsx"
            # PrepareDataToImportPackage3703.convert_dataframe_to_excel(dataframe=df, file_name=file_name)

            print(df.info())
            print(df)

            tt_rows = len(df)
            tt_debit    = len(df[df["TP"] == "D"])
            tt_credit   = len(df[df["TP"] == "C"])

            data_json = json.loads(df.to_json(orient="table"))
            # print(data_json)

            print(f"""
                --------- CONFIG CONTAS
                --> tt_rows: {tt_rows}
                --> tt_debit: {tt_debit}
                --> tt_credit: {tt_credit}
            """)

            return {
                "data_table": data_json ,
                "tt_rows": tt_rows,
                "tt_debit": tt_debit,
                "tt_credit": tt_credit,
                "list_page_erros": [],
                }

            
        except Exception as e:
            print(f" \n\n ERROR GENERATE COBRANÇAS PAGAS | ERROR: {e}")
            return {"code": 500, "msg": "erro ao gerar pacote cobranças pagas.", "error": e}

    # ----
    
    # 
    #  ----------------------------------- ETL ARAO DOS SANTOS -----------------------------------
    #  file_populate: Base Arão dos Santos -> Para preenchimento
    #  file_base_query: Base Arão dos Santos -> Base de consulta

    def read_Excel_File(contents):
        xlsx_bytes = io.BytesIO(contents)
        file = pd.ExcelFile(xlsx_bytes)
        sheet_name = file.sheet_names[0]
        df = file.parse(sheet_name=sheet_name)
        return df
    
    # ----

    def read_xlsx_arao_dos_santos(file_contabil, file_consulta, modelo, company_session):
        try:
            print(f"\n\n ----- Arquivo informado arão dos santos | file_contabil: {file_contabil} | file_consulta: {file_consulta}")
            
            # contents = file_populate.read()
            # xlsx_bytes = io.BytesIO(contents)
            # file = pd.ExcelFile(xlsx_bytes)
            # sheet_name = file.sheet_names[-1]
            # df = file.parse(sheet_name=sheet_name)
            # df_temp_consulta = PrepareDataToImportPackage3703.read_Excel_File(contents=file_consulta)
            # df_temp_contabil = PrepareDataToImportPackage3703.read_Excel_File(contents=file_contabil)

            contents = file_consulta.read()
            
            df_temp_consulta = PrepareDataToImportPackage3703.read_Excel_File(contents=contents)
            df_temp_consulta["index_aux"] = list(range(0, len(df_temp_consulta.index)))
            df_temp_consulta_copy = df_temp_consulta.copy()
            try:

                df_temp_consulta['Data'] = pd.to_datetime(df_temp_consulta['Data'])
                df_temp_consulta['Data'] = df_temp_consulta['Data'].dt.strftime('%d/%m/%Y')
                df_temp_consulta["Nota Fiscal"] = pd.to_numeric(df_temp_consulta['Nota Fiscal'].values)

            except:
                df_temp_consulta['Data Emissão'] = pd.to_datetime(df_temp_consulta['Data Emissão'])
                df_temp_consulta['Data Emissão'] = df_temp_consulta['Data Emissão'].dt.strftime('%d/%m/%Y')
                df_temp_consulta["Nº Nota"] = pd.to_numeric(df_temp_consulta['Nº Nota'].values)



            print("\n\n ------------------------ df_temp_consulta ------------------------ ")
            print(df_temp_consulta)


            contents = file_contabil.read()
            df_temp_contabil = PrepareDataToImportPackage3703.read_Excel_File(contents=contents)
            df_temp_contabil["NAME_AUX"] = "-"
            print("\n\n ------------------------ df_temp_contabil ------------------------ ")
            print(df_temp_contabil)


            # df_temp_contabil []

            list_pendencias = list()
            list_nomes_encontrados = list()
            # return {}

            for i in df_temp_contabil.index:
                
                nf = df_temp_contabil["Nº NF"][i]
                print(f"\n\n\n ************** NF CONTABIL ====> {nf}")
        
                if modelo == "modelo_fiscal":
                    query_df_contabil = df_temp_consulta[df_temp_consulta["Nota Fiscal"] == nf ][["Data", "Nota Fiscal", "Cliente/Fornecedor"]]
                    print(f"\n\n -------------------> QUERY Nota Fiscal (modelo_fiscal):\n{query_df_contabil}")
                    
                    if len(query_df_contabil) >= 1:
                        df_temp_contabil["Data Recebim. NF"][i] = query_df_contabil["Data"].values[0]
                        print(" ------------------ NOME FORNECEDOR (FORMATO MANUAL) ------------------ ")
                        print(query_df_contabil["Cliente/Fornecedor"].values[0])
                        list_nomes_encontrados.append(query_df_contabil["Cliente/Fornecedor"].values[0])
                    else:
                        list_pendencias.append(nf)

                if modelo == "modelo_email":
                    query_df_contabil = df_temp_consulta[df_temp_consulta["Nº Nota"] == nf ][["Data Emissão", "Nº Nota"]]
                    print(f"\n\n -------------------> QUERY Nº Nota (modelo_email): {query_df_contabil}")
                
                    if len(query_df_contabil) >= 1:
                        df_temp_contabil["Data Recebim. NF"][i] = query_df_contabil["Data Emissão"].values[0]
                        print(" ------------------ NOME FORNECEDOR (FORMATO EMAIL) ------------------ ")
                        print(query_df_contabil["Cliente/Fornecedor"].values[0])
                        list_nomes_encontrados.append(query_df_contabil["Cliente/Fornecedor"].values[0])
                    else:
                        list_pendencias.append(nf)

            
                print(f" -------------------- QUERY RESULT -------------------- NF: {nf}")
                print(query_df_contabil)

            #
            # 
            #  ------------------------------------------------- DF PENDÊNCIAS -------------------------------------------------
            print("\n\n ------------------------ query_df_contabil TRATADO ------------------------ ")
            df_temp_contabil.index = list(range(0, len(df_temp_contabil)))
            print(df_temp_contabil)
            print(df_temp_contabil.info())
            # return {}

            

            
            df_temp_contabil = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df_temp_contabil, dict_replace_names={
                "CNPJ": "CNPJ_ORIGIN"
            })

            df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df_temp_contabil, model="model_7", cod_empresa=company_session)

            print("\n\n\n -------------------------- DATAFRAME ")
            print(df)





            # -------------------------------------------------------------- REPLACE NAMES COLS
            # if modelo == "modelo_email":
            #     df = PrepareDataToImportPackage3703.rename_columns_dataframe(
            #         dataframe=df, dict_replace_names={
            #             "CNPJ"
            #             "Valor Serviço": "Valor Bruto NF",
            #             "Valor IRRF": "IRPJ Retido",
            #             "Valor CSLL": "CSLL Retida",
            #             "": "Cofins Retido",
            #             "Valor PIS/PASEP": "PIS Retido",

            #         }
            #     )


            df["VALOR_NF_LIQ"] = df["Valor Bruto NF"] - df["IRPJ Retido"]
            df["VLR_LIQUIDO"] = df["VALOR_NF_LIQ"] - df["CSLL Retida"] - df["Cofins Retido"] - df["PIS Retido"]

            df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
                {"TP": "C", "TYPE_PROCESS": "comum"},
                {"TP": "D", "TYPE_PROCESS": "debit_PIS"},
                {"TP": "D", "TYPE_PROCESS": "debit_CSLL"},
                {"TP": "D", "TYPE_PROCESS": "debit_COFINS"},
            ])

            df.sort_values(by=["Nº NF", "Nome Cliente", "TP", "TYPE_PROCESS"], inplace=True)
            df.index = list(range(0, len(df.index)))
            
            
            #  ------------------------------------------------- CÁLCULO DE IMPOSTOS -------------------------------------------------
            # TP | CONTA
            # -- - --------------
            # C  | crédito
            # D  | débito
            # D  | Cofins Retido
            # D  | CSLL Retida
            # D  | PIS Retido

            cont_aux = 0
            for i in df.index:
                
                # df["COMPL_HISTORICO"][i] = f"Recebimento dupl. nr {numero_NF} - {nome_cliente}"

                if cont_aux == 0:

                    df["VALOR"][i] = df["VALOR_NF_LIQ"][i]
                    df["CONTA"][i] = ""
                    cont_aux += 1

                elif cont_aux == 1:

                    df["TYPE_PROCESS"][i] = "account_code_debit"
                    df["VALOR"][i] = df["VLR_LIQUIDO"][i]
                    df["CONTA"][i] = "-"
                    cont_aux += 1

                elif cont_aux == 2:

                    df["VALOR"][i] = df["Cofins Retido"][i]
                    df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("Recebimento", "COFINS")
                    df["CONTA"][i] = "88"
                    cont_aux += 1

                elif cont_aux == 3:

                    df["VALOR"][i] = df["CSLL Retida"][i]
                    df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("Recebimento", "CSLL")
                    df["CONTA"][i] = "94"
                    cont_aux += 1

                elif cont_aux == 4:

                    df["VALOR"][i] = df["PIS Retido"][i]
                    df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("Recebimento", "PIS")
                    df["CONTA"][i] = "87"
                    cont_aux = 0
            
            df.to_excel("df_arao_dos_santos.xlsx")
            # ------------------------------------------------------------------------
                        
            print(" \n\n ---------------------- TRANSPOSE VALUES DATAFRAME ---------------------- ")

            df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
                "CNPJ": "CNPJ_ORIGIN",
                "DATA": "Data Recebim. NF",
                "NOME": "Nome Cliente",

            })

            df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

            print(df)
            print(df.info())

            # ------------------------------------------------------------------------------------
            # ---------------------- AJUSTE PARA MODELO TP_REGISTRO ===> 03 ----------------------
            # ------------------------------------------------------------------------------------

            df_tp_registro_03 = df.copy()

            list_remove = [0, 0.0, "0.0", "0.00", "0.00", "0,00"]
            df_tp_registro_03 = df_tp_registro_03[~df_tp_registro_03['VALOR'].isin(list_remove)]
            df_tp_registro_03 = df_tp_registro_03.dropna(subset=['DATA'])
            

            df_tp_registro_03 = df_tp_registro_03[  df_tp_registro_03["TYPE_PROCESS"] != "comum"  ]
            df_tp_registro_03["TP_REGISTRO"] = "03"

            df_tp_registro_03 = PrepareDataToImportPackage3703.create_additional_columns(dataframe=df_tp_registro_03, column_name="IMPOSTO", default_value="")
            df_tp_registro_03["CODIGO_IMPOSTO"] = "5952"
            df_tp_registro_03["BC_IMPOSTO"] = df_tp_registro_03["Valor Bruto NF"]
            df_tp_registro_03["ALIQUOTA"] = "-"
            df_tp_registro_03["VALOR_IMPOSTO"] = "-"
            df_tp_registro_03["TP_RETENCAO"] = "3"
            df_tp_registro_03["COD_MINICIPIO_DEVIDO_ISS"] = ""
            df_tp_registro_03["NAT_RETENCAO"] = "3"
            df_tp_registro_03["TP_RECEITA"] = "1"
            df_tp_registro_03["CNPJ_EMPRESA_03"] = ""
            df_tp_registro_03["IE_EMPRESA_03"] = ""

            for i in df_tp_registro_03.index:
                if df_tp_registro_03["TYPE_PROCESS"][i] == "debit_COFINS":
                    df_tp_registro_03["IMPOSTO"][i] = "1102"
                    df_tp_registro_03["ALIQUOTA"][i] = "3,00"
                    df_tp_registro_03["VALOR_IMPOSTO"][i] = df_tp_registro_03["VALOR"][i]

                # ----
                elif df_tp_registro_03["TYPE_PROCESS"][i] == "debit_PIS":
                    df_tp_registro_03["IMPOSTO"][i] = "1101"
                    df_tp_registro_03["ALIQUOTA"][i] = "0,65"
                    df_tp_registro_03["VALOR_IMPOSTO"][i] = df_tp_registro_03["VALOR"][i]
                # ----
                elif df_tp_registro_03["TYPE_PROCESS"][i] == "debit_CSLL":
                    df_tp_registro_03["IMPOSTO"][i] = "1103"
                    df_tp_registro_03["ALIQUOTA"][i] = "1,00"
                    df_tp_registro_03["VALOR_IMPOSTO"][i] = df_tp_registro_03["VALOR"][i]


            #  --------------------------------------

            df_tp_registro_03 = PrepareDataToImportPackage3703.create_additional_columns(dataframe=df_tp_registro_03, column_name="COL_AUX__18", default_value="")
            df_tp_registro_03 = PrepareDataToImportPackage3703.create_additional_columns(dataframe=df_tp_registro_03, column_name="COL_AUX__19", default_value="")
            df_tp_registro_03 = PrepareDataToImportPackage3703.create_additional_columns(dataframe=df_tp_registro_03, column_name="COL_AUX__20", default_value="")
            df_tp_registro_03 = PrepareDataToImportPackage3703.create_additional_columns(dataframe=df_tp_registro_03, column_name="COL_AUX__21", default_value="")
            
            # df_tp_registro_03 = df_tp_registro_03[[
                
            #     # ------------------ BASE LAYOUT JB 03 ------------------

            #     "TP_REGISTRO", # 01
            #     "NOME",
            #     "COD_EMPRESA", # 02
            #     "FILIAL", # 03
            #     "NR_L_CTO_ERP", # 04
            #     "TP", # 05
            #     "CNPJ", # 06
            #     "IMPOSTO", # 07
            #     "CODIGO_IMPOSTO", # 08
            #     "BC_IMPOSTO", # 09
            #     "ALIQUOTA", # 10
            #     "VALOR_IMPOSTO", # 11
            #     "TP_RETENCAO", # 12
            #     "COD_MINICIPIO_DEVIDO_ISS", # 13
            #     "NAT_RETENCAO", # 14
            #     "TP_RECEITA", # 15
            #     "CNPJ_EMPRESA_03", # 16
            #     "IE_EMPRESA_03", # 17

            #     "COL_AUX__18",
            #     "COL_AUX__19",
            #     "COL_AUX__20",
            #     "COL_AUX__21",
                
            #     "TYPE_PROCESS",    
            # ]]

            tt_index_00 = len(df.index)
            tt_index_03 = len(df_tp_registro_03.index)

            # df_tp_registro_03["NR_L_CTO_ERP"] = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df_tp_registro_03, index_default=tt_index_00)

            print(df_tp_registro_03)


            
            list_remove = [0, 0.0, "0.0", "0.00", "0.00", "0,00"]

            df = df.dropna(subset=['DATA'])
            df = df[~df['VALOR'].isin(list_remove)]

            df_tp_registro_03 = df_tp_registro_03[~df_tp_registro_03['VALOR_IMPOSTO'].isin(list_remove)]
            
            print("\n\n -------------- DF 00 -------------- ")
            print(df)
            print(df.info())

            print("\n\n -------------- DF 03 -------------- ")
            print(df_tp_registro_03)
            print(df_tp_registro_03.info())

            data_json = json.loads(df.to_json(orient="table"))
            data_json_03 = json.loads(df_tp_registro_03.to_json(orient="table"))
            # print(data_json)


            tt_rows = len(df)
            tt_debit    = len(df[df["TP"] == "D"])
            tt_credit   = len(df[df["TP"] == "C"])

            # ------------

            tt_rows_03 = len(df_tp_registro_03)
            tt_debit_03    = len(df_tp_registro_03[df_tp_registro_03["TP"] == "D"])
            tt_credit_03   = len(df_tp_registro_03[df_tp_registro_03["TP"] == "C"])

            print(f"""
                --------- CONFIG CONTAS
                --> tt_rows: {tt_rows}
                --> tt_debit: {tt_debit}
                --> tt_credit: {tt_credit}

                --> tt_index_00: {tt_index_00}
                --> tt_index_03: {tt_index_03}

                --> tt_rows_03: {tt_rows_03}
                --> tt_debit_03: {tt_debit_03}
                --> tt_credit_03: {tt_credit_03}
            """)

            # file_name = r"I:\\1. Gaulke Contábil\\Administrativo\\9. TI\\1. Projetos\\8. Importação Arão dos Santos Recebimentos\\00_base_tratada_arao_dos_santos.xlsx"
            # PrepareDataToImportPackage3703.convert_dataframe_to_excel(dataframe=df, file_name=file_name)

            # file_name = r"I:\\1. Gaulke Contábil\\Administrativo\\9. TI\\1. Projetos\\8. Importação Arão dos Santos Recebimentos\\03_base_tratada_arao_dos_santos.xlsx"
            # PrepareDataToImportPackage3703.convert_dataframe_to_excel(dataframe=df_tp_registro_03, file_name=file_name)


            #
            # 
            # ------------------------------------------------- DF PENDÊNCIAS -------------------------------------------------
            print(" \n\n ----------------- DF PENDÊNCIAS ----------------- ")
            # print(sorted(list_nomes_encontrados))
            df_pendencias = df_temp_consulta_copy[~df_temp_consulta_copy["Cliente/Fornecedor"].isin(list_nomes_encontrados)]
            df_pendencias.dropna(subset=["Cliente/Fornecedor"], inplace=True)
            df_pendencias.index = list(range(0, len(df_pendencias)))

            

            tt_pendencias = len(df_pendencias.index)
            if tt_pendencias > 0:
                btn_pendencias = True
            else:
                btn_pendencias = False
            

            # df_pendencias.to_excel("df_pendencias_araos_dos_santos.xlsx")
            df_pendencias = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df_pendencias, dict_replace_names={
                "Data": "DATA",
                "Compet.": "COMPET",
                "Origem": "ORIGEM",
                "Nota Fiscal": "NOTA_FISCAL",
                "Cliente/Fornecedor": "CLIENTE_FORNECEDOR",
                "Descrição": "DESCRICAO",
                "Classificação": "CLASSIFICACAO",
                "Valor": "VALOR",
                "Centro Custo": "CENTRO_CUSTO",
                "Nº Pasta": "N_PASTA",
                "Cliente Pasta ": "CLIENTE_PASTA",
            })
            df_pendencias['DATA']= pd.to_datetime(df_pendencias['DATA'])
            print(df_pendencias)
            print(df_pendencias.info())

            df_json_pendencias = json.loads(df_pendencias.to_json(orient="table"))
            

            print(f"\n\n ----------- TT Pendências: {tt_pendencias} -----------")

            return {
                "data_table": data_json,
                "data_json_03": data_json_03,
                "df_json_pendencias": df_json_pendencias,
                "btn_pendencias": btn_pendencias,
                "tt_pendencias": tt_pendencias,
                "tt_rows": tt_rows,
                "tt_debit": tt_debit,
                "tt_credit": tt_credit,
                "tt_rows_03": tt_rows_03,
                "tt_debit_03": tt_debit_03,
                "tt_credit_03": tt_credit_03,
                "list_page_erros": [],
                }
            
        except Exception as e:
            print(f" \n\n ERROR GENERATE ARÃO DOS SANTOS | ERROR: {e}")
            return {"code": 500, "msg": "erro ao gerar pacote Arão dos Santos.", "error": e}
        
    # ----
    
    def read_pdf_comprovante_banco_bradesco(file, company_session):

        print(f"\n\n ----- Arquivo informado comprovante Bradesco | arquivo: {file}")

        contents = file.read()
        pdf_bytes = io.BytesIO(contents)
        pdf_reader = PdfReader(pdf_bytes)

        list_data_pages = list()
        list_page_erros = list()
        index_page = 0
        print(f" TT PAGES: {len(pdf_reader.pages)}")


        data_to_table = {
            # ---------- IDENTIFICADORES
            "nome_beneficiario": list(),
            "cnpj_beneficiario": list(),

            "nome_pagador": list(),
            "cnpj_pagador": list(),

            # # ---------- DATAS
            "data_de_debito": list(),
            "data_de_vencimento": list(),

            # ---------- VALORES
            "valor": list(),
            "desconto": list(),
            "abatimento": list(),
            "bonificacao": list(),
            "multa": list(),
            "juros": list(),
            "valor_total": list(),

        }

        dict_tags_to_text = dict()

        for index_page in range(len(pdf_reader.pages)):
            try:
                print(f"\n\n\n ---- INDEX PAGE: {index_page}")
                
                page = pdf_reader.pages[index_page]
                
                
                data_page = page.extract_text()
                print("\n\n ----------------------- DATA EXTRACT ----------------------- ")
                print(data_page)

                dict_tags_to_text = PrepareDataToImportPackage3703.check_text_to_tag(data=data_page, dict_tags_to_text=dict_tags_to_text)
                print(dict_tags_to_text)
                
                for i in range(len(data_page)):
                    
                    # -------------------------- NOME PAGADOR --------------------------
                    if "Código de barras:" == data_page[i:i+17]:
                        data_temp = data_page[i+17:i+90]
                        print(f"\n\n ---------->> NOME PAGADOR")
                        for j in range(len(data_temp)):
                            if "CNPJ:" == data_temp[j:j+5]:
                                print(f">>>>>>>>>>>>> INDEX J: {j}")
                                # data_to_table["nome_pagador"].append( data_temp[0:j-3] )
                                data_to_table["nome_beneficiario"].append( data_temp[0:j-3] )

                    # -------------------------- NOME BENEFIARIO --------------------------
                    if "CPF/CNPJ Beneficiário:" == data_page[i:i+22]:
                        data_temp = data_page[i+22:i+90].split("Nome Fantasia")[0].strip()
                        # data_to_table["nome_beneficiario"].append( data_temp )
                        data_to_table["nome_pagador"].append( data_temp )
                        print(f"\n\n ---------->> NOME BENEFIARIO")
                        print(f">>>>>>>>>>>>>> {data_temp}")
                        
                    
                    if "Beneficiário Final" in data_page[i:i+18]:
                        print(f" << {data_page[i:i+18]} >>")
                        print(f" ---> CNPJ BENEFICIARIO {i} / {data_page[i+19:i+38]}")
                        data_to_table["cnpj_beneficiario"].append( data_page[i+1+19:i+38] )
                        # data_to_table["cnpj_pagador"].append( data_page[i+1+19:i+38] )

                    if data_page[ i : i+23 ] == "CPF/CNPJ Beneficiário:":
                        print(f" << {data_page[i+22 : i+50]} >>")
                        data_temp = data_page[i+22 :]
                        
                        for j in range(len(data_temp)):
                            if "Nome" in data_temp[j:j+5]:
                                print(f"\n ---> NOME BENEFICIARIO {i} / {data_page[i+j+8:i+(j+20)]}")
                                break
                            
                    
                    if data_page[i:i+2] == "R$":
                        value_aux = data_page[i:i+15]
                        print(f" -------------->>>> {value_aux}")
                        index_fim = None

                        data_aux = data_page[i:i+18]
                        for j in range(len(data_aux)):
                            if data_aux[j] == ",":
                                index_fim = i + (j+3)
                                break
                        value = data_page[i:index_fim].split("R$ ")[1].strip().replace(".", "").replace(".", "").replace(",", ".")
                        print(f" ---> VALOR: {value}")
                        
                        if " V" in value_aux:
                            data_to_table["valor_total"].append(value)

                        elif "Va" in value_aux:
                            data_to_table["valor"].append(value)
                            data_de_vencimento = data_page[index_fim+5:index_fim+15]
                            cnpj_pagador = data_page[index_fim+61:index_fim+80]

                            data_de_debito = data_page[index_fim+35:index_fim+45]
                            data_to_table["data_de_debito"].append(data_de_debito)
                            data_to_table["data_de_vencimento"].append(data_de_vencimento)

                            data_to_table["cnpj_pagador"].append( cnpj_pagador )
                            # data_to_table["cnpj_beneficiario"].append( cnpj_pagador )
                        
                        elif "Descont" in data_aux:
                            data_to_table["desconto"].append(value)

                        elif "Abatime" in data_aux:
                            data_to_table["abatimento"].append(value)

                        elif "Bonific" in data_aux:
                            data_to_table["bonificacao"].append(value)

                        elif "Multa" in data_aux:
                            data_to_table["multa"].append(value)

                        elif "Juros" in data_aux:
                            data_to_table["juros"].append(value)
                        

                    
            except Exception as e:
                print(f" ### ERROR EXTRACT DATA PDF | ERROR: {e}")
                list_page_erros.append({index_page: e})
            


        print("\n\n ------------------------------ dict_tags_to_text ------------------------------ ")
        print(dict_tags_to_text)
        df_tags = pd.DataFrame.from_dict(dict_tags_to_text, orient="index", columns=["Qte"])
        df_tags.reset_index(inplace=True)
        df_tags.rename(columns={'index': 'tag'}, inplace=True)
        df_tags = df_tags.loc[~df_tags["tag"].isin(["", " "])]
        df_tags.sort_values(by="Qte", inplace=True, ascending=False)
        df_tags.index = list(range(0, len(df_tags.index)))
        # print(df_tags)
    
        print(data_to_table)
        df = pd.DataFrame.from_dict(data_to_table)
        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_8", value_generic="Bradesco", cod_empresa=company_session)
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "data_de_debito",
            "CNPJ": "cnpj_beneficiario",
            "NOME": "nome_pagador",
            "VALOR": "valor",
        })
        # print(df)

        # desconto
        # abatimento
        # bonificacao
        # multa
        # juros
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "D", "TYPE_PROCESS": "desconto"},
            {"TP": "D", "TYPE_PROCESS": "abatimento"},
            {"TP": "D", "TYPE_PROCESS": "bonificacao"},
            {"TP": "D", "TYPE_PROCESS": "multa"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
        ])

        df.sort_values(by=["nome_beneficiario", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))

        count_aux = 0
        for i in df.index:

            if count_aux == 0:
                df["TYPE_PROCESS"][i] = "account_code_credit"
                df["VALOR"][i] = df["valor_total"][i]
                count_aux += 1
            elif count_aux == 1:
                df["VALOR"][i] = df["desconto"][i]
                df["CONTA"][i] = "936"
                count_aux += 1
            elif count_aux == 2:
                df["VALOR"][i] = df["abatimento"][i]
                df["CONTA"][i] = "936"
                count_aux += 1
            elif count_aux == 3:
                df["VALOR"][i] = df["bonificacao"][i]
                df["CONTA"][i] = "936"
                count_aux += 1
            elif count_aux == 4:
                df["VALOR"][i] = df["multa"][i]
                df["CONTA"][i] = "947"
                count_aux += 1
            elif count_aux == 5:
                df["VALOR"][i] = df["juros"][i]
                df["CONTA"][i] = "947"
                count_aux += 1
            elif count_aux == 6:
                df["VALOR"][i] = df["valor"][i]
                df["CONTA"][i] = ""
                count_aux = 0
        
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

        print(df.info())
        print(df)
        print(df[["COD_EMPRESA", "NOME"]])

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))
        df_tags_json = json.loads(df_tags.to_json(orient="table"))
        print(dict_tags_to_text)

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        # try:
        #     df.to_excel("data_bradesco.xlsx")
        # except Exception as e:
        #     print(f"\n\n ### ERROR CONVERT DATAFRAME TO EXCEL | ERROR: {e} ### ")

        return {
            "data_table": data_json,
            "df_tags_json": df_tags_json,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
        }
    
    # ----
    
    def read_pdf_comprovante_banco_sicredi(file, company_session):

        print(f"\n\n ----- Arquivo informado comprovante Sicredi | arquivo: {file}")

        contents = file.read()
        pdf_bytes = io.BytesIO(contents)
        pdf_reader = PdfReader(pdf_bytes)

        list_data_pages = list()
        list_page_erros = list()
        index_page = 0
        print(f" TT PAGES: {len(pdf_reader.pages)}")


        data_to_table = {
            # ---------- IDENTIFICADORES
            "nome_beneficiario": list(),
            "cnpj_beneficiario": list(),

            "nome_pagador": list(),
            "cnpj_pagador": list(),

            # # # ---------- DATAS
            "data_de_debito": list(),
            "data_de_vencimento": list(),

            # # ---------- VALORES
            "valor": list(),
            "desconto": list(),
            "abatimento": list(),
            # "bonificacao": list(),
            "multa": list(),
            "juros": list(),
            "valor_total": list(),

        }

        for index_page in range(len(pdf_reader.pages)):
            try:
                print(f"\n\n\n ---- INDEX PAGE: {index_page}")
                
                page = pdf_reader.pages[index_page]
                
                
                data_page = page.extract_text()
                if "Valor Pago (R$):" in data_page:
                # if "boleto" in data_page:
                    print("\n\n ----------------------- DATA EXTRACT ----------------------- ")
                    print(data_page)
                    
                    for i in range(len(data_page)):
                        
                        # 
                        # 
                        # -------------------------- CNPJ PAGADOR / NOME BENEFICIARIO --------------------------
                        # CPF/CNPJ do Pagador: ---> 20 caract.
                        if "CPF/CNPJ do Pagador:" == data_page[i:i+20]:
                            # ----------------------------------------------------------------------------- CNPJ PAGADOR
                            data_temp = data_page[i-20:i-1].split(":")[-1]
                            data_to_table["cnpj_pagador"].append(data_temp)
                            print(f"\n\n ---------->> CNPJ PAGADOR")
                            print(f">>>>>>>> {data_temp}\n\n")
                        # --------------------------------------------------------------------------------- NOME BENEFICIARIO
                            data_temp = data_page[i+20:i+120].split("Nome")[0]
                            data_to_table["nome_beneficiario"].append( data_temp )
                            print(f"\n\n ---------->> NOME PAGADOR")
                            print(f">>>>>>>>>>>>>> {data_temp}")
                        
                        # 
                        # 
                        # -------------------------- CNPJ BENEFIARIO / NOME PAGADOR -------------------------- 
                        if "CPF/CNPJ do Beneficiário:" == data_page[i:i+25]:
                            data_temp = data_page[i-22:i].split(":")[-1] # CNPJ PAGADOR
                            data_to_table["cnpj_beneficiario"].append( data_temp )
                            print(f"\n\n ---------->> CNPJ BENEFIARIO")
                            print(f">>>>>>>>>>>>>> {data_temp}")

                            data_temp = data_page[i+25:i+100].split("Razão")[0].split("Nome")[0] # NOME PAGADOR
                            data_to_table["nome_pagador"].append( data_temp )
                            print(f"\n\n ---------->> NOME BENEFIARIO")
                            print(f">>>>>>>>>>>>>> {data_temp}")

                        
                        # 
                        # 
                        # -------------------------- DATA DE VENCIMENTO E PAGAMENTO -------------------------- 
                        if "Data da Transação:" == data_page[i:i+18]:
                            # print(f"\n\n -------------------------- DATA DEBITO -------------------------- ")
                            data_temp = data_page[i-11:i].strip()
                            data_to_table["data_de_debito"].append( data_temp )
                            # print(f">>>>>>>>>>>>>> {data_temp}")
                        
                            # print(f"\n\n -------------------------- DATA CREDITO -------------------------- ")
                            data_temp = data_page[i+18:i+29].strip()
                            data_to_table["data_de_vencimento"].append( data_temp )
                            # print(f">>>>>>>>>>>>>> {data_temp}")
                        # 
                        # 
                        # -------------------------- VALORES (R$) -------------------------- 

                        # Nº Ident. DDA: --> 14 caract.

                        if data_page[i:i+14] == "Nº Ident. DDA:":
                            data_temp = data_page[i+14:i+28].split(" ")[0].strip().replace(".", "").replace(".", "").replace(",", ".")
                            if "." in data_temp:
                                data_to_table["valor"].append( data_temp )
                                print(f"\n\n\n\n  -------------->>>> VALOR 1-1 {data_temp}")

                        if data_page[i:i+23] == "Descrição do Pagamento:":
                            data_temp = data_page[i+23:i+36].split(" ")[0].strip().replace(".", "").replace(".", "").replace(",", ".")
                            if "." in data_temp:
                                data_to_table["valor"].append( data_temp )
                                print(f"\n\n\n\n  -------------->>>> VALOR 1-2 {data_temp}")

                        if data_page[i:i+23] == "Valor do Desconto (R$):":
                            data_temp = data_page[i+23:i+38].split(" ")[0].strip().replace(".", "").replace(".", "").replace(",", ".")
                            data_to_table["valor_total"].append( data_temp )
                            print(f"\n\n\n\n  -------------->>>> VALOR 2 {data_temp}")

                            # ----------------------- OUTROS VALORES -----------------------
                            cont_aux = 0
                            name_aux = None
                            for j in range(len(data_page)):
                                if cont_aux < 4:
                                    if data_page[j:j+5] == "(R$):":
                                        if cont_aux == 0:
                                            name_aux = "desconto"
                                        if cont_aux == 1:
                                            name_aux = "juros"
                                        if cont_aux == 2:
                                            name_aux = "multa"
                                        if cont_aux == 3:
                                            name_aux = "abatimento"

                                        data_aux_valores = data_page[j+5:j+10]
                                        data_to_table[name_aux].append( data_aux_valores )
                                        print(f"\n\n\n\n ------------------------------------------> name_aux: {name_aux} | data_aux_valores: {data_aux_valores}\n\n\n\n")
                                        cont_aux += 1

            
            except Exception as e:
                print(f" ### ERROR EXTRACT DATA PDF | ERROR: {e}")
                list_page_erros.append({index_page: e})
            
        
        df = pd.DataFrame.from_dict(data_to_table)
        
        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_8", value_generic="Sicredi", cod_empresa=company_session)
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "data_de_debito",
            "CNPJ": "cnpj_beneficiario",
            "NOME": "nome_pagador",
            "VALOR": "valor",
        })

        # # desconto
        # # abatimento
        # # bonificacao | neste caso não possui
        # # multa
        # # juros
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "D", "TYPE_PROCESS": "desconto"},
            {"TP": "D", "TYPE_PROCESS": "abatimento"},
            # {"TP": "D", "TYPE_PROCESS": "bonificacao"},
            {"TP": "D", "TYPE_PROCESS": "multa"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
        ])

        df.sort_values(by=["nome_beneficiario", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))


        count_aux = 0
        for i in df.index:

            if count_aux == 0:
                df["TYPE_PROCESS"][i] = "account_code_credit"
                df["VALOR"][i] = df["valor_total"][i].strip().replace(",", ".") # .strip().replace(".", "").replace(".", "").replace(",", ".")
                count_aux += 1
            elif count_aux == 1:
                df["VALOR"][i] = df["desconto"][i].strip().replace(",", ".") # .strip().replace(".", "").replace(".", "").replace(",", ".")
                df["CONTA"][i] = "936"
                count_aux += 1
            elif count_aux == 2:
                df["VALOR"][i] = df["abatimento"][i].strip().replace(",", ".") # .strip().replace(".", "").replace(".", "").replace(",", ".")
                df["CONTA"][i] = "936"
                count_aux += 1
            elif count_aux == 3:
                df["VALOR"][i] = df["multa"][i].strip().replace(",", ".") # .strip().replace(".", "").replace(".", "").replace(",", ".")
                df["CONTA"][i] = "947"
                count_aux += 1
            elif count_aux == 4:
                df["VALOR"][i] = df["juros"][i].strip().replace(",", ".") # .strip().replace(".", "").replace(".", "").replace(",", ".")
                df["CONTA"][i] = "947"
                count_aux += 1
            elif count_aux == 5:
                df["VALOR"][i] = df["valor"][i].strip().replace(",", ".") # .strip().replace(".", "").replace(".", "").replace(",", ".")
                df["CONTA"][i] = ""
                count_aux = 0
        
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

        print("\n\n ---------------------------- DF LAYOUT JB ---------------------------- ")
        print(df.info())
        print(df)

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))
        # print(data_json)

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        try:
            df.to_excel("data_sicredi.xlsx")
        except Exception as e:
            print(f"\n\n ### ERROR CONVERT DATAFRAME TO EXCEL | ERROR: {e} ### ")

        return {
            "data_table": data_json ,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
        }
        # return {}
    
    # ----
    
    def read_pdf_comprovante_banco_sicoob(file, company_session):
        print(f"\n\n ----- Arquivo informado comprovante Sicoob | arquivo: {file}")

        contents = file.read()
        pdf_bytes = io.BytesIO(contents)
        pdf_reader = PdfReader(pdf_bytes)

        list_data_pages = list()
        list_page_erros = list()
        index_page = 0
        print(f" TT PAGES: {len(pdf_reader.pages)}")


        data_to_table = {
            # ---------- IDENTIFICADORES
            "nome_beneficiario": list(),
            "cnpj_beneficiario": list(),

            "nome_pagador": list(),
            "cnpj_pagador": list(),

            # # # # ---------- DATAS
            "data_de_debito": list(),
            "data_de_vencimento": list(),

            # # # ---------- VALORES
            "valor": list(),
            "desconto": list(),
            # "abatimento": list(),
            # "bonificacao": list(),
            # "multa": list(),
            "juros": list(),
            "valor_total": list(),

        }

        for index_page in range(len(pdf_reader.pages)):
            try:
                print(f"\n\n\n ---- INDEX PAGE: {index_page}")
                
                page = pdf_reader.pages[index_page]
                
                
                data_page = page.extract_text()
                print(data_page)
                
                if "CPF/CNPJ Beneficiário:" in data_page:
                # if "boleto" in data_page:
                    print("\n\n ----------------------- DATA EXTRACT ----------------------- ")
                    print(data_page)
                    
                    for i in range(len(data_page)):
                        
                        # 
                        # -------------------------- CNPJ PAGADOR / NOME BENEFICIARIO --------------------------
                        # CPF/CNPJ do Pagador: ---> 20 caract.
                        if "CPF/CNPJ Pagador:" in data_page[i:i+18]:
                            # ----------------------------------------------------------------------------- CNPJ PAGADOR
                            data_temp = data_page[i+18:i+38].split("\n")[0].strip() # 
                            data_to_table["cnpj_pagador"].append(data_temp)
                            print(f"\n\n>>>>>>>> CNPJ PAGADOR: {data_temp}\n\n")
                        # # # --------------------------------------------------------------------------------- NOME PAGADOR
                            data_temp = data_page[i+-125:i].split("Pagador:")[1].split("\n")[0] #.strip()
                            data_to_table["nome_pagador"].append( data_temp )
                            print(f"\n\n ---------->> NOME PAGADOR: {data_temp}\n\n")

                        if "CPF/CNPJ Beneficiário:" in data_page[i:i+23]:
                            # ----------------------------------------------------------------------------- CNPJ BENEFICIÁRIO
                            data_temp = data_page[i+23:i+42].split("\n")[0].strip() # 
                            data_to_table["cnpj_beneficiario"].append(data_temp)
                            print(f"\n\n>>>>>>>> CNPJ BENEFICIÁRIO: {data_temp}\n\n")

                        # # --------------------------------------------------------------------------------- NOME BENEFICIARIO
                        if "Nome/Razão Social do Beneficiário:" in data_page[i:i+35]:
                            data_temp = data_page[i+35:i+120].split("\n")[0].strip()
                            data_to_table["nome_beneficiario"].append( data_temp )
                            print(f"\n\n ---------->> NOME BENEFICIARIO: {data_temp}\n\n")

                        
                        # # --------------------------------------------------------------------------------- DATA PAGAMENTO
                        if "Data Pagamento:" in data_page[i:i+16]:
                            data_temp = data_page[i+16:i+28].split("\n")[0].strip()
                            data_to_table["data_de_debito"].append( data_temp )
                            print(f"\n\n ---------->> DATA PAGAMENTO: {data_temp}\n\n")
                        # # --------------------------------------------------------------------------------- DATA VENCIMENTO
                        if "Data Vencimento:" in data_page[i:i+17]:
                            data_temp = data_page[i+17:i+28].split("\n")[0].strip()
                            data_to_table["data_de_vencimento"].append( data_temp )
                            print(f"\n\n ---------->> DATA VENCIMENTO: {data_temp}\n\n")
                        
                        # # --------------------------------------------------------------------------------- VALOR DOCUMENTO
                        if "Valor Documento:" in data_page[i:i+17]:
                            data_temp = data_page[i+17:i+28].split("\n")[0].strip()
                            data_to_table["valor"].append( data_temp )
                            print(f"\n\n ---------->> VALOR DOCUMENTO: {data_temp}\n\n")
                        # # --------------------------------------------------------------------------------- VALOR DESCONTO / ABATIMENTO
                        if "(-) Desconto / Abatimento:" in data_page[i:i+27]:
                            data_temp = data_page[i+27:i+40].split("\n")[0].strip()
                            data_to_table["desconto"].append( data_temp )
                            print(f"\n\n ---------->> VALOR DESCONTO: {data_temp}\n\n")
                        # # --------------------------------------------------------------------------------- VALOR JUROS / ACRÉSCIMOS
                        if "(+) Outros acréscimos:" in data_page[i:i+23]:
                            data_temp = data_page[i+23:i+42].split("\n")[0].strip()
                            data_to_table["juros"].append( data_temp )
                            print(f"\n\n ---------->> VALOR JUROS: {data_temp}\n\n")
                        # # --------------------------------------------------------------------------------- VALOR PAGO / TOTAL
                        if "Valor Pago:" in data_page[i:i+12]:
                            data_temp = data_page[i+12:i+42].split("\n")[0].strip()
                            data_to_table["valor_total"].append( data_temp )
                            print(f"\n\n ---------->> VALOR TOTAL: {data_temp}\n\n")

            
            except Exception as e:
                print(f" ### ERROR EXTRACT DATA PDF | ERROR: {e}")
                list_page_erros.append({index_page: e})
            
        
        df = pd.DataFrame.from_dict(data_to_table)
        print(df)


        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_8", value_generic="Sicoob", cod_empresa=company_session)
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "data_de_debito",
            "CNPJ": "cnpj_beneficiario",
            "NOME": "nome_beneficiario",
            "VALOR": "valor",
        })
        # print(df)

        # # desconto
        # # abatimento  | neste caso não possui
        # # bonificacao | neste caso não possui
        # # multa       | neste caso não possui
        # # juros
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "D", "TYPE_PROCESS": "desconto"},
            # {"TP": "D", "TYPE_PROCESS": "abatimento"},
            # {"TP": "D", "TYPE_PROCESS": "bonificacao"},
            # {"TP": "D", "TYPE_PROCESS": "multa"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
        ])

        df.sort_values(by=["nome_beneficiario", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))


        count_aux = 0
        for i in df.index:

            if count_aux == 0:
                df["TYPE_PROCESS"][i] = "account_code_credit"
                df["VALOR"][i] = df["valor_total"][i].strip().replace(".", "").replace(".", "").replace(",", ".")
                count_aux += 1
            elif count_aux == 1:
                df["VALOR"][i] = df["desconto"][i].strip().replace(".", "").replace(".", "").replace(",", ".")
                df["CONTA"][i] = "936"
                count_aux += 1
            # elif count_aux == 2:
            #     df["VALOR"][i] = df["abatimento"][i].strip().replace(".", "").replace(".", "").replace(",", ".")
            #     df["CONTA"][i] = "936"
            #     count_aux += 1
            # elif count_aux == 3:
            #     df["VALOR"][i] = df["multa"][i].strip().replace(".", "").replace(".", "").replace(",", ".")
            #     df["CONTA"][i] = "947"
            #     count_aux += 1
            elif count_aux == 2:
                df["VALOR"][i] = df["juros"][i].strip().replace(".", "").replace(".", "").replace(",", ".")
                df["CONTA"][i] = "947"
                count_aux += 1
            elif count_aux == 3:
                df["VALOR"][i] = df["valor"][i].strip().replace(".", "").replace(".", "").replace(",", ".")
                df["CONTA"][i] = ""
                count_aux = 0
        
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

        df = df.drop_duplicates(subset=["cnpj_beneficiario", "COMPL_HISTORICO", "DATA", "VALOR", "TP"], keep="last")
        df.to_excel("comprovantes_bancario_sicoob.xlsx")

        print("\n\n ---------------------------- DF LAYOUT JB ---------------------------- ")
        print(df.info())
        print(df)

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))
        # print(data_json)

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        try:
            df.to_excel("data_sicoob.xlsx")
        except Exception as e:
            print(f"\n\n ### ERROR CONVERT DATAFRAME TO EXCEL | ERROR: {e} ### ")

        return {
            "data_table": data_json ,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
        }
        # return {}
    
    # ----

    def read_pdf_comprovante_banco_itau(file, company_session):
        print(f"\n\n ----- Arquivo PDF informado comprovante ITAÚ | arquivo: {file}")

        contents = file.read()
        pdf_bytes = io.BytesIO(contents)
        pdf_reader = PdfReader(pdf_bytes)

        list_data_pages = list()
        list_page_erros = list()
        index_page = 0
        print(f" TT PAGES: {len(pdf_reader.pages)}")


        data_to_table = {
            # # # # ---------- IDENTIFICADORES
            "nome_beneficiario": list(),
            "cnpj_beneficiario": list(),

            # # # # ---------- DATAS
            "data_de_debito": list(),
            "data_de_vencimento": list(),

            # # # ---------- VALORES
            "valor": list(),
            "desconto": list(),
            "juros": list(),
            "valor_total": list(),

     
        }

        for index_page in range(len(pdf_reader.pages)):
            try:
                print(f"\n\n\n ---- INDEX PAGE: {index_page}")
                
                page = pdf_reader.pages[index_page]
                
                data_page = page.extract_text()
                
                if "Comprovante de pagamento de boleto" in data_page:
                    print("\n\n ----------------------- DATA EXTRACT ----------------------- ")
                    print(data_page)
                    
                    for i in range(len(data_page)):
                        
                        # # # --------------------------------------------------------------------------------- VALOR DOCUMENTO
                        if "Valor do documento (R$);" in data_page[i:i+24]:
                            print("\n\n ---------------------------- DATA RETROACTIVE ---------------------------- ")
                            data_temp_retroactive = data_page[i-150:i].strip().split()

                            data_vencimento_fist = data_temp_retroactive[-1]
                            cnpj_cpf_beneficiario_fist = data_temp_retroactive[-2]
                            nome_beneficiario_first = " ".join(data_temp_retroactive[:-2]).split("Social:")[1].strip()

                            print(data_temp_retroactive)
                            print(f"--> data_vencimento_fist: {data_vencimento_fist}")
                            print(f"--> cnpj_cpf_beneficiario_fist: {cnpj_cpf_beneficiario_fist}")
                            print(f"--> nome_beneficiario_first: {nome_beneficiario_first}")
                            print(" ----------------------------------------------------------------------------- \n")

                            data_temp = data_page[i+24:i+450].strip().split()
                            
                            print(f"\n\n ---------->> VALOR DOCUMENTO: {data_temp}\n\n")
                            valor_documento = data_temp[0]
                            valor_desconto = data_temp[4]
                            valor_juros_multa = data_temp[7]

                            print(f' TT CATACT: {  data_temp  }')
                            print("\n ----------------------- ")
                            print(f"valor_documento: {valor_documento}")
                            print(f"valor_desconto: {valor_desconto}")
                            print(f"valor_juros_multa: {valor_juros_multa}")

                           
                            for i in range(len(data_temp)):
                                if data_temp[i] == "Sacador":
                                    valor_pagamento = data_temp[i-1]

                                if data_temp[i] == "Autenticação":
                                    data_pagamento = data_temp[i-1]
                                    print(f"Data do Pagamento: { data_pagamento }")
                                    print(f"Valor Pagamento: { valor_pagamento }")


                                    if data_temp[i-2].count(".") > 0:
                                        cnpj_cpf_beneficiario = data_temp[i-2]
                                        nome_beneficiario = ' '.join(data_temp[i-10: i-2]).split("pagamento:")[1].strip()
                                        print(f'CNPJ/CPF Beneficiário: { cnpj_cpf_beneficiario } | { len(cnpj_cpf_beneficiario) } | { cnpj_cpf_beneficiario.count(".") }')
                                        print(f"Nome Beneficiário: { nome_beneficiario }")

                                        data_to_table["nome_beneficiario"].append(nome_beneficiario)
                                        data_to_table["cnpj_beneficiario"].append(cnpj_cpf_beneficiario)
                                    
                                    else:
                                        print(f"--> CNPJ/CPF Beneficiário: {cnpj_cpf_beneficiario_fist}")
                                        print(f"--> Nome Beneficiário: {nome_beneficiario_first}")

                                        data_to_table["nome_beneficiario"].append(nome_beneficiario_first)
                                        data_to_table["cnpj_beneficiario"].append(cnpj_cpf_beneficiario_fist)

                            data_to_table["valor"].append(valor_pagamento)
                            data_to_table["desconto"].append(valor_desconto)
                            data_to_table["juros"].append(valor_juros_multa)
                            data_to_table["valor_total"].append(valor_documento)
                            data_to_table["data_de_debito"].append(data_pagamento)
                            data_to_table["data_de_vencimento"].append(data_vencimento_fist)


            
            except Exception as e:
                print(f" ### ERROR EXTRACT DATA PDF | ERROR: {e}")
                list_page_erros.append({index_page: e})
            
        
        # print("\n\n ---------------- DATAFRAME EXTRACT ---------------- ")
        # print(data_to_table)
        df = pd.DataFrame.from_dict(data_to_table)
        # print(df)

        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_10", cod_empresa=company_session)

        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "data_de_debito",
            "CNPJ": "cnpj_beneficiario",
            "NOME": "nome_beneficiario",
            "VALOR": "valor",
        })
        # print("\n ----------------- LAYOUT JB ----------------- ")
        # print(df)

        # # # desconto
        # # # abatimento  | neste caso não possui
        # # # bonificacao | neste caso não possui
        # # # multa
        # # # juros
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "D", "TYPE_PROCESS": "desconto"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
        ])

        df.sort_values(by=["nome_beneficiario", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))

        count_aux = 0
        for i in df.index:
            print(f" ----> INDEX: {i} | count_aux: {count_aux}")

            if count_aux == 0:
                df["TYPE_PROCESS"][i] = "account_code_credit"
                df["VALOR"][i] = df["valor_total"][i]
                count_aux += 1

            elif count_aux == 1:
                df["VALOR"][i] = df["desconto"][i]
                df["CONTA"][i] = "936"
                count_aux += 1

            elif count_aux == 2:
                df["VALOR"][i] = df["juros"][i]
                df["CONTA"][i] = "947"
                count_aux += 1

            elif count_aux == 3:
                df["VALOR"][i] = df["valor"][i]
                df["CONTA"][i] = ""
                count_aux = 0
        
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00", "0,00"])

        df.index = list(range(0, len(df.index)))
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

        print("\n\n ---------------------------- DF LAYOUT JB ---------------------------- ")
        print(df.info())
        print(df)

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))
        # print(data_json)

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        # try:
        #     df.to_excel("data_itau.xlsx")
        # except Exception as e:
        #     print(f"\n\n ### ERROR CONVERT DATAFRAME TO EXCEL | ERROR: {e} ### ")

        return {
            "data_table": data_json ,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
        }
        # return {}
    
    def read_xls_comprovante_banco_itau(file, company_session):

        print(f"\n\n ----- Arquivo XLS informado comprovante ITAÚ | file: {file}")

        # --------------- READ SUPPLIERS ---------------
        contents = file.read()
        xlsx_bytes = io.BytesIO(contents)
        file = pd.ExcelFile(xlsx_bytes)
        sheet_name = file.sheet_names[0]
        print(f"\n ---> sheet_name: {sheet_name}\n\n")
        df = file.parse(sheet_name=sheet_name, dtype='str')
        df.dropna(subset=["Unnamed: 6"], inplace=True)
        df.index = list(range(0, len(df.index)))
        df = df[1:]

        df = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df, dict_replace_names={
            "Unnamed: 0": "nome_pagador",
            "Unnamed: 1": "CNPJ_ORIGIN",
            "Unnamed: 2": "TIPO_PAGAMENTO",
            "Unnamed: 3": "REFERENCIA_EMPRESA",
            "Unnamed: 4": "data_de_pagamento",
            "Unnamed: 5": "VALOR_PAGO",
            "Unnamed: 6": "STATUS_PAGAMENTO",
        })

        df_pendencias = df.copy()
        df = df[~df['CNPJ_ORIGIN'].str.contains('\*')]
        df_pendencias = df_pendencias[df_pendencias['CNPJ_ORIGIN'].str.contains('\*')]

        df.index = list(range(0, len(df.index)))
        df_pendencias.index = list(range(0, len(df_pendencias.index)))

        print(f"\n\n ------------------ DF PENDÊNCIAS ------------------  ")
        print(df_pendencias)
        print("\n ----------------------------------------------------- \n")


        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_10.2", cod_empresa=company_session)
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "data_de_pagamento",
            "CNPJ": "CNPJ_ORIGIN",
            "NOME": "nome_pagador",
            "VALOR": "VALOR_PAGO",
        })

        
        # # desconto    | neste caso não possui
        # # abatimento  | neste caso não possui
        # # bonificacao | neste caso não possui
        # # multa       | neste caso não possui
        # # juros       | neste caso não possui
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            # {"TP": "D", "TYPE_PROCESS": "desconto"},
            # {"TP": "D", "TYPE_PROCESS": "abatimento"},
            # # {"TP": "D", "TYPE_PROCESS": "bonificacao"},
            # {"TP": "D", "TYPE_PROCESS": "multa"},
            # {"TP": "D", "TYPE_PROCESS": "juros"},
        ])

        print(f"\n\n ------------------ DF LAYOUT DUPLICADO EM LOTE FINALIZADO ------------------  ")
        print(df)
        print("\n ----------------------------------------------------- \n")

        df.sort_values(by=["nome_pagador", "GRUPO_LCTO", "TP"], inplace=True)
        df = df[~df["VALOR"].isin( ["0,00", "0.00"] )]

        df.loc[df['TP'] == 'C', 'TYPE_PROCESS'] = "account_code_credit"
        df.loc[df['TP'] == 'C', 'CONTA'] = "-"
        df.loc[df['TP'] == 'D', 'CONTA'] = ""
        
        # cont_aux = 0
        for i in df.index:
            v = df["VALOR"][i].values[0]
            print(f'-----------------> VALOR: {v}')

            if "." in v:
                if v[-3] != ".":
                    df["VALOR"][i] = df["VALOR"][i] + "0"
            else:
                df["VALOR"][i] = df["VALOR"][i] + ".00"


        df.index = list(range(0, len(df.index)))
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)
        
        print(df)
        # df.to_excel("data_itau.xlsx")

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))
    

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        

        return {
            "data_table": data_json ,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
            }

    # ----
    
    def read_pdf_comprovante_banco_civia(file, company_session):
        print(f"\n\n ----- Arquivo informado comprovante CIVIA | arquivo: {file}")

        contents = file.read()
        pdf_bytes = io.BytesIO(contents)
        pdf_reader = PdfReader(pdf_bytes)

        list_data_pages = list()
        list_page_erros = list()
        index_page = 0
        print(f" TT PAGES: {len(pdf_reader.pages)}")


        data_to_table = {
            # ---------- IDENTIFICADORES
            "nome_beneficiario": list(),
            # "cnpj_beneficiario": list(),

            # "nome_pagador": list(),
            # "cnpj_pagador": list(),

            # # # # ---------- DATAS
            "data_de_debito": list(),
            # "data_de_vencimento": list(),

            # # # ---------- VALORES
            "valor": list(),
            "desconto": list(),
            # "abatimento": list(),
            # "bonificacao": list(),
            # "multa": list(),
            "juros": list(),
            "valor_total": list(),

        }

        for index_page in range(len(pdf_reader.pages)):
            try:
                print(f"\n\n\n ---- INDEX PAGE: {index_page}")
                
                page = pdf_reader.pages[index_page]
                
                
                data_page = page.extract_text()
                print(data_page)
                
                if "COMPROVANTE DE PAGAMENTO" in data_page:
                    print("\n\n ----------------------- DATA EXTRACT ----------------------- ")
                    print(data_page)
                    
                    for i in range(len(data_page)):
                        
                        # # --------------------------------------------------------------------------------- NOME BENEFICIARIO
                        if "DADOS DO BENEFICIÁRIO" in data_page[i:i+21]:
                            data_temp = data_page[i+21:i+420].split()
                            print("\n\n ------------------------------------------------------------------------")
                            print(f"\n ---------->> DADOS DO BENEFICIÁRIO:\n{data_temp}\n\n")

                            index_aux = 0
                            for j in range(len(data_temp)):
                                if data_temp[j] == "Beneficiário":
                                    index_aux = j
                                if data_temp[j] == "CPF/CNPJ":
                                    nome_beneficiario = " ".join(data_temp[index_aux+1 : j])
                                    # print(f"\n\n -----> nome_beneficiario: {nome_beneficiario}")
                                    # data_to_table["nome_beneficiario"].append(nome_beneficiario)

                                if data_temp[j] == "Vencimento":
                                    valor = data_temp[j+3].replace(".", "").replace(",", ".")
                                    juros = "0.00"
                                    descontos = "0.00"
                                    data_pagamento = data_temp[j+15]
                                    valor_pagamento = data_temp[j+17].replace(".", "").replace(",", ".")


                                    # ----------------------------------------------------------------------------------------
                                    # -------------------------- VALIDAÇÃO DE JUROS/DESCONTO MANUAL --------------------------
                                    # -------------------------- NÃO É REGISTRADO CORRETAMENTE NO EXTRATO CIVIA. -------------
                                    # ----------------------------------------------------------------------------------------
                                    _v1 = float(valor)
                                    _v2 = float(valor_pagamento)
                                    # check_value = round( _v2 -_v1 , 2)
                                    check_value = round(_v2 -_v1, 2)
                                  
                                    if check_value > 0:
                                        check_value = str(abs(check_value))
                                        if check_value[-2] == ".":
                                            check_value = check_value + "0"
                                        juros = check_value

                                    elif check_value < 0:
                                        descontos = str(abs(check_value))
                                        if descontos[-2] == ".":
                                            descontos = descontos + "0"
                                    
                                    # print(f"\n\n -----> nome_beneficiario: {nome_beneficiario}")
                                    # print(f"\n -----> valor: {valor}")
                                    # print(f"\n -----> juros: {juros}")
                                    # print(f"\n -----> descontos: {descontos}")
                                    # print(f"\n -----> data pagamento: {data_pagamento}")
                                    # print(f"\n -----> valor pagamento: {valor_pagamento}")
                                    # print(f"\n -----> check_value: {check_value}")


                                    data_to_table["nome_beneficiario"].append(nome_beneficiario)
                                    # data_to_table["cnpj_beneficiario"].append()
                                    data_to_table["data_de_debito"].append(data_pagamento)
                                    # data_to_table["data_de_vencimento"].append()
                                    data_to_table["valor"].append(valor)
                                    data_to_table["desconto"].append(descontos)
                                    data_to_table["juros"].append(juros)
                                    data_to_table["valor_total"].append(valor_pagamento)
                                    

                                    
                            print("\n ------------------------------------------------------------------------\n\n")
            
            except Exception as e:
                print(f" ### ERROR EXTRACT DATA PDF | ERROR: {e}")
                list_page_erros.append({index_page: e})
            
        df = pd.DataFrame.from_dict(data_to_table)
        # print(df)

        # return {}
        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_11", cod_empresa=company_session)
        
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "data_de_debito",
            # "CNPJ": "cnpj_beneficiario",
            "NOME": "nome_beneficiario",
            "VALOR": "valor",
        })

        # # desconto
        # # abatimento  | neste caso não possui
        # # bonificacao | neste caso não possui
        # # multa       | neste caso não possui
        # # juros
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "D", "TYPE_PROCESS": "desconto"},
            # {"TP": "D", "TYPE_PROCESS": "abatimento"},
            # {"TP": "D", "TYPE_PROCESS": "bonificacao"},
            # {"TP": "D", "TYPE_PROCESS": "multa"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
        ])

        df.sort_values(by=["nome_beneficiario", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))


        count_aux = 0
        for i in df.index:

            if count_aux == 0:
                df["TYPE_PROCESS"][i] = "account_code_credit"
                df["VALOR"][i] = df["valor_total"][i]
                count_aux += 1
            elif count_aux == 1:
                df["VALOR"][i] = df["desconto"][i]
                df["CONTA"][i] = "1664"
                count_aux += 1

            elif count_aux == 2:
                df["VALOR"][i] = df["juros"][i]
                df["CONTA"][i] = "1688"
                count_aux += 1
            elif count_aux == 3:
                df["VALOR"][i] = df["valor"][i]
                df["CONTA"][i] = ""
                count_aux = 0
        
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

        list_names = list(df.drop_duplicates(subset=["NOME"], keep="last")["NOME"].values)
        print(list_names)

        # print("\n\n ---------------------------- DF LAYOUT JB ---------------------------- ")
        # print(df.info())
        # print(df)

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))
        # print(data_json)

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        try:
            df.to_excel("data_civia.xlsx")
        except Exception as e:
            print(f"\n\n ### ERROR CONVERT DATAFRAME TO EXCEL | ERROR: {e} ### ")

        return {
            "data_table": data_json ,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_names": list_names,
            "list_page_erros": [],
        }
        # return {}
    
    # ----
    
    def read_xls_comprovante_grupo_DAB(file_suppliers, file_payments, company_session):

        print(f"\n\n ----- Arquivo informado comprovante Grupo DAB RN | file_suppliers: {file_suppliers} | file_payments: {file_payments}")

        # --------------- READ SUPPLIERS ---------------
        contents = file_suppliers.read()
        xlsx_bytes = io.BytesIO(contents)
        file = pd.ExcelFile(xlsx_bytes)
        sheet_name = file.sheet_names[0]
        print(f"\n ---> sheet_name: {sheet_name}")
        df_suppliers = file.parse(sheet_name=sheet_name, dtype='str')[["Código", "C.N.P.J", "Descrição"]]
        df_suppliers = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df_suppliers, dict_replace_names={
            "Código": "CODIGO",
            "C.N.P.J": "CNPJ",
            "Descrição": "NOME",
        })
        # --------------- READ PAYMENTS ---------------
        contents = file_payments.read()
        xlsx_bytes = io.BytesIO(contents)
        file = pd.ExcelFile(xlsx_bytes)
        sheet_name = file.sheet_names[0]
        print(f"\n ---> sheet_name: {sheet_name}")
        df_payments = file.parse(sheet_name=sheet_name, dtype='str')
        df_payments = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df_payments, dict_replace_names={
            "Código": "CODIGO",
            "Fornecedor": "NOME",
            "N.F": "NOTA_FISCAL",
            "Data Venc.": "DATA_VENC",
            "Data Pgto": "DATA_PAG",
            "Desconto": "DESCONTO",
            "Devolução": "DEVOLUCAO",
            "Juros": "JUROS",
            "Valor Pago": "VALOR_PAGO",
            "Loja": "LOTE",
        })
        df_payments = PrepareDataToImportPackage3703.create_additional_columns(dataframe=df_payments, column_name="CNPJ", default_value="-")
        df_payments = df_payments[~df_payments["CODIGO"].isin(["0", "Código"])]
        print("\n\n ------------------ df_suppliers ------------------ ")
        print(df_suppliers)
        print("\n\n ------------------ df_payments ------------------ ")
        print(df_payments)


        # ------------------ CREATE DATAFRAME 
        for i in df_payments.index:
            try:
                code = int(df_payments["CODIGO"][i])
                query_code = df_suppliers[df_suppliers["CODIGO"] == str(code)][["CNPJ"]].values[0][0]
                data_aux = query_code.split()[-1][-2:]
                print("\n\n --------------------------------------------- ")
                print(f" ----> CODE: {code} | RESULT QUERY: {query_code}")
                try:
                    data_aux = int(data_aux)
                    if data_aux > -1:
                        print(">>>>>>>>>>>>>>>>>>>>>>  ", data_aux)
                        df_payments["CNPJ"][i] = query_code
                except:
                    pass

            except:
                pass
        
        print("\n ------------------ df_payments ------------------ ")
        df_payments = df_payments[~df_payments["CNPJ"].isin(["-"])]
        df_payments = df_payments.sort_values(by=["CNPJ"])
        df_payments.index = list(range(0, len(df_payments)))

        df_payments = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df_payments, dict_replace_names={
            "NOME": "NOME_ORIGIN",
            "CNPJ": "CNPJ_ORIGIN",
        })
        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df_payments, model="model_9", cod_empresa=company_session)

        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "NOME": "NOME_ORIGIN",
            "CNPJ": "CNPJ_ORIGIN",
            "DATA": "DATA_PAG",
        })

        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
                {"TP": "C", "TYPE_PROCESS": "comum"},
                {"TP": "C", "TYPE_PROCESS": "DESCONTO"},
                {"TP": "C", "TYPE_PROCESS": "DEVOLUCAO"},
                {"TP": "D", "TYPE_PROCESS": "JUROS"},
            ])
        
        
        print("\n\n reajustando valores: juros, desconto, devolução, débito/crédito comum...\n\n")
        df = df.sort_values(by=["NOME", "GRUPO_LCTO", "TP"])
        df.index = list(range(0, len(df.index)))

        cont_aux = 0
        for i in df.index:

            if cont_aux == 0: # Débito comum
                df["TYPE_PROCESS"][i] = "account_code_debit"
                df["CONTA"][i] = ""
                df["TP"][i] = "D"
                df["VALOR"][i] = df["a Pagar"][i]
                
            elif cont_aux == 1: # Desconto - Crédito
                df["TYPE_PROCESS"][i] = "account_code_credit_desconto"
                df["CONTA"][i] = "1664"
                df["VALOR"][i] = df["DESCONTO"][i]
                
            elif cont_aux == 2: # Devolução - Crédito
                df["TYPE_PROCESS"][i] = "account_code_credit_devolucao"
                df["CONTA"][i] = "126"
                df["VALOR"][i] = df["DEVOLUCAO"][i]
                
            elif cont_aux == 3: # Juros - Débito
                df["TYPE_PROCESS"][i] = "account_code_debit_juros"
                df["CONTA"][i] = "1688"
                df["VALOR"][i] = df["JUROS"][i]
                
            elif cont_aux == 4: # Crédito - comum
                df["TYPE_PROCESS"][i] = "account_code_credit"
                df["CONTA"][i] = "5"
                df["TP"][i] = "C"
                df["VALOR"][i] = df["VALOR_PAGO"][i]

            if cont_aux == 4:
                cont_aux = 0
            else:
                cont_aux += 1

            df["VALOR"][i] = df["VALOR"][i].replace(".", "").replace(".", "").replace(",", ".")

        
        df = df[~df["VALOR"].isin( ["0,00", "0.00"] )]
        df.index = list(range(0, len(df.index)))
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)
        

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))
        # print(data_json)

        print(df)
        # df.to_excel("df_payments.xlsx")

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        

        return {
            "data_table": data_json ,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
            }

    # ----
    
    def read_xlsx_contas_a_receber_INOVA(file, company_session):

        print(f"\n\n ----- Arquivo informado contas a pagar - INOVA | arquivo: {file}")

        contents = file.read()
        xlsx_bytes = io.BytesIO(contents)
        file = pd.ExcelFile(xlsx_bytes)
        sheet_name = file.sheet_names[0]

        df = file.parse(sheet_name=sheet_name, dtype='str')
        df = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df, dict_replace_names={
            "Cliente": "CNPJ_ORIGIN",
            "Nome": "nome_pagador",
            "Valor pagamento": "VALOR_PAGAMENTO",
            "Pagamento": "DATA_PAGAMENTO",
            "Valor juros": "juros",
            "Valor desconto": "desconto",
            "Valor abatimento": "abatimento",
            "Valor despesa": "despesa",
        })
        print(df)

        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_12", cod_empresa=company_session)
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "DATA_PAGAMENTO",
            "CNPJ": "CNPJ_ORIGIN",
            "NOME": "nome_pagador",
            "VALOR": "VALOR_PAGAMENTO",
        })
        df = df.dropna(subset=['CNPJ_ORIGIN'])
        print("\n\n ------- DF IMPORTAÇÃO JB ------- ")
        print(df)

        # desconto
        # juros
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "D", "TYPE_PROCESS": "desconto"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
        ])
        
        df.sort_values(by=["nome_pagador", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))

        count_aux = 0
        for i in df.index:
            
            if count_aux == 0:
                df["CONTA"][i] = ""

                try:
                    if float(df["juros"][i]) > 0:
                        df["VALOR"][i] = str( round( ( float(df["VALOR_PAGAMENTO"][i]) + float(df["desconto"][i]) ) - float(df["juros"][i]), 2) )
                        print("\n\n >>>>>>>> ", df["VALOR"][i])
                    elif float(df["desconto"][i]) > 0:
                        df["VALOR"][i] = str( round(( float(df["VALOR_PAGAMENTO"][i]) + float(df["juros"][i]) ) + float(df["desconto"][i]), 2))
                        print("\n\n >>>>>>>> ", df["VALOR"][i])
                except Exception as e:
                    print(f">>>>>>> ERROR CALCULATE | ERROR: {e}")
                count_aux += 1

            elif count_aux == 1:
                
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("RECEB.", "DESCONTO CONCEDIDO ")
                df["VALOR"][i] = df["desconto"][i]
                df["CONTA"][i] = "945"
                count_aux += 1

            elif count_aux == 2:
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("RECEB.", "RECEB. JUROS ")

                df["VALOR"][i] = df["juros"][i]
                df["CONTA"][i] = "935"
                df["TP"][i] = "C"

                count_aux += 1
            elif count_aux == 3:
                df["TYPE_PROCESS"][i] = "account_code_debit"
                df["VALOR"][i] = df["VALOR_PAGAMENTO"][i]
                df["CONTA"][i] = "-"
                count_aux = 0
        
   
        df = PrepareDataToImportPackage3703.adjust_value_to_decimal_string(dataframe=df, column_name="VALOR")
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])

        df.index = list(range(0, len(df.index)))
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

        print("\n\n ------- DataFrame contas a receber INOVA ------- ")
        print(df.info())
        print(df)
        df.to_excel("contas a receber INOVA.xlsx")


        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        return {
            "data_table": data_json,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
        }

    # ----
    
    def read_xlsx_contas_a_pagar_PONTO_CERTO(file, file_2, company_session):

        print(f"\n\n ----- Arquivo informado contas a pagar - PONTO CERTO | arquivo 1: {file}")
        print(f"\n ----- Arquivo informado contas a pagar - PONTO CERTO | arquivo 2: {file_2}\n\n")

       
        contents = file.read()
        contents_2 = file_2.read()
        xlsx_bytes = io.BytesIO(contents)
        xlsx_bytes_2 = io.BytesIO(contents_2)

        df = pd.read_excel(xlsx_bytes, dtype="str")
        df_2 = pd.read_excel(xlsx_bytes_2, dtype="str")

        print("\n\n -------------------- DF 01 -------------------- ")
        df["CNPJ"] = ""
        print(df)
        print(df.info())

        print("\n\n -------------------- DF 02 -------------------- ")
        print(df_2)

        df = df[ df['DATA PGTO'] != "00:00:00" ]
        df['DATA VCTO'] = pd.to_datetime(df['DATA VCTO'])
        df['DATA PGTO'] = pd.to_datetime(df['DATA PGTO'])
        df['DATA LCTO'] = pd.to_datetime(df['DATA LCTO'])

        df['DATA VCTO'] = df['DATA VCTO'].dt.strftime('%d/%m/%Y')
        df['DATA PGTO'] = df['DATA PGTO'].dt.strftime('%d/%m/%Y')
        df['DATA LCTO'] = df['DATA LCTO'].dt.strftime('%d/%m/%Y')
        
        for i in df.index:
            id_parceiro = df["IDFORNECEDOR"][i]
            cnpj_df_2 = df_2[df_2["CODIGO"] == id_parceiro]["CNPJ/CPF"]

            if len(cnpj_df_2) > 0:
                df["CNPJ"][i] = cnpj_df_2.values[0]
                print(f"\n >>> Index: {i} | id_parceiro: {id_parceiro} | CNPJ_2: {cnpj_df_2.values[0]}")
            else:
                print(id_parceiro, " não encontrado")
        
        df_pendencia = df[ df["CNPJ"] == "" ]
        df = df[ df["CNPJ"] != "" ]

        print("\n\n -------------------- DF 01 COM CNPJ AJUSTADO -------------------- ")
        print(df)
        print("\n\n -------------------- DF PENDÊNCIA -------------------- ")
        print(df_pendencia)


        df = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df, dict_replace_names={
            "CNPJ": "CNPJ_ORIGIN",
            "FORNECEDOR": "nome_pagador",
            "VALOR PGTO": "VALOR_PAGAMENTO",
            "DATA PGTO": "DATA_PAGAMENTO",
        })
        df = PrepareDataToImportPackage3703.calculate_discount_or_fees(dataframe=df, col_name_valor_pago="VALOR_PAGAMENTO", col_name_valor_doc="VALOR")

        print("\n\n -------------------------- df - rename columns | calculate values fees and discount -------------------------- ")
        print(df)
        # df.to_excel("contas_a_pagar_ponto_certo.xlsx")
        
        # df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="Filial", list_remove_values=["1"])

        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_13", cod_empresa=company_session)
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "DATA_PAGAMENTO",
            "CNPJ": "CNPJ_ORIGIN",
            "NOME": "nome_pagador",
            "VALOR": "VALOR_PAGAMENTO",
        })
        df = df.dropna(subset=['CNPJ_ORIGIN'])
        print("\n\n ------- DF IMPORTAÇÃO JB ------- ")
        print(df)

        # desconto
        # juros


        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "D", "TYPE_PROCESS": "desconto"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
            # {"TP": "D", "TYPE_PROCESS": "multa"},
        ])
        
        df.sort_values(by=["nome_pagador", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))

        count_aux = 0
        for i in df.index:
            
            if count_aux == 0:
                
                df["TYPE_PROCESS"][i] = "account_code_credit"
                df["CONTA"][i] = "-"
                df["TP"][i] = "C"
                count_aux += 1

            elif count_aux == 1:
                
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("PAGAM.", "DESCONTO CONCEDIDO ")
                df["VALOR"][i] = df["desconto"][i]
                df["CONTA"][i] = "1664"
                df["TP"][i] = "D"
                count_aux += 1

            elif count_aux == 2:
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("PAGAM.", "PAGAM. JUROS ")

                df["VALOR"][i] = df["juros"][i]
                df["CONTA"][i] = "1688"
                df["TP"][i] = "D"
                count_aux += 1

            # elif count_aux == 3:
            #     df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("PAGAM.", "PAGAM. MULTA ")

            #     df["VALOR"][i] = df["multa"][i]
            #     df["CONTA"][i] = "1725"
            #     df["TP"][i] = "D"
            #     count_aux += 1

            elif count_aux == 3:
                try:
                    df["TP"][i] = "D"
                    df["CONTA"][i] = ""
                    v_pag = float(df["VALOR_PAGAMENTO"][i].replace(",", "."))
                    # v_multa = float(df["multa"][i])
                    v_desc = float(df["desconto"][i])
                    v_juros = float(df["juros"][i])
                    valor = None

                    # ------------

                    if float(df["juros"][i]) > 0:
                        valor = str(round((v_pag + v_desc) - v_juros, 2))
                        df["VALOR"][i] = valor
                    
                    elif float(df["desconto"][i]) > 0:
                        valor = str(round((v_pag + v_juros) + v_desc, 2))
                        df["VALOR"][i] = valor
                        
                except Exception as e:
                    print(f">>>>>>> ERROR CALCULATE/CONVERT | ERROR: {e}")
                # df["CONTA"][i] = ""
                count_aux = 0
            
        print("\n\n DF IMPORTAÇÃO COM DE-PARA DE CONTAS ")
        print(df)
        try:
            df = PrepareDataToImportPackage3703.adjust_value_to_decimal_string(dataframe=df, column_name="VALOR", replace_caract=True)
            df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])
        except Exception as e:
            print(f" ### ERROR ADJUST TO DECIMAL STRING | ERROR: {e}")
            return {}
        df.index = list(range(0, len(df.index)))
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)


        print("\n\n ------- DataFrame contas a pagar PONTO CERTO ------- ")
        print(df.info())
        print(df)
        # df.to_excel("contas a pagar - PONTO CERTO.xlsx")

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        return {
            "data_table": data_json,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
        }

    # ----
    
    def read_xlsx_contas_a_pagar_GARRA(file, company_session):

        print(f"\n\n ----- Arquivo informado contas a pagar - PONTO CERTO | arquivo: {file}")

        contents = file.read()
        file_bytes = io.BytesIO(contents)

        df = pd.read_excel(file_bytes, dtype="str")
        df = df.rename(columns=df.iloc[0]).drop(df.index[0])
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="CPF/CNPJ", list_remove_values=[
            "-----", ""
        ])
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="Data de confirmação", list_remove_values=[
            "------", ""
        ])
        df = df.dropna(subset=["CPF/CNPJ"])



        df = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df, dict_replace_names={
            "CPF/CNPJ": "CNPJ_ORIGIN",
            "Destinado à": "nome_pagador",
            "Valor total": "VALOR_PAGAMENTO",
            "Data de confirmação": "DATA_PAGAMENTO",
            "Juros": "juros",
            "Desconto": "desconto",
            "Multa": "multa",
        })
        print("\n\n -------------------- DF -------------------- ")
        print(df)

        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_14", cod_empresa=company_session)
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "DATA_PAGAMENTO",
            "CNPJ": "CNPJ_ORIGIN",
            "NOME": "nome_pagador",
            "VALOR": "VALOR_PAGAMENTO",
        })
        # df = df.dropna(subset=['CNPJ_ORIGIN'])
        print("\n\n ------- DF IMPORTAÇÃO JB ------- ")
        print(df)

        # desconto
        # juros
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "D", "TYPE_PROCESS": "desconto"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
            # {"TP": "D", "TYPE_PROCESS": "multa"},
        ])
        
        df.sort_values(by=["nome_pagador", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))

        count_aux = 0
        for i in df.index:

            # if df["VALOR"][i].count(",") == 1:
            #     df["VALOR"][i] = df["VALOR"][i].replace(",", ".", 1)


            if df["VALOR"][i].count(".") == 2:
                df["VALOR"][i] = df["VALOR"][i].replace(".", "", 1).replace(",", ".")
                print(f' -----> VALOR AJUSTADO: {df["VALOR"][i]} | {type(df["VALOR"][i])}')

            if df["VALOR_PAGAMENTO"][i].count(".") == 2:
                df["VALOR_PAGAMENTO"][i] = df["VALOR_PAGAMENTO"][i].replace(".", "", 1).replace(",", ".")
                print(f' -----> VALOR_PAGAMENTO AJUSTADO: {df["VALOR_PAGAMENTO"][i]}')
            
            print(f"""
                --------------------------------
                -->>>> VALOR: {df["VALOR"][i]}
                -->>>> VALOR_PAGAMENTO: {df["VALOR_PAGAMENTO"][i]}
            """)

            
            if count_aux == 0:
                df["CONTA"][i] = "-"
                df["VALOR"][i] = df["VALOR_PAGAMENTO"][i]
                df["TYPE_PROCESS"][i] = "account_code_credit"
                count_aux += 1

            elif count_aux == 1:
                
                df["TP"][i] = "C"
                df["CONTA"][i] = "936"
                df["VALOR"][i] = df["desconto"][i]
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("Pagamento Dupl", "Desconto Concedido Dupl ")
                count_aux += 1

            elif count_aux == 2:

                df["TP"][i] = "D"
                df["CONTA"][i] = "947"
                df["VALOR"][i] = df["juros"][i]
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("Pagamento Dupl", "Pagamento Juros Dupl ")
                count_aux += 1

            elif count_aux == 3:
                df["CONTA"][i] = ""
                
                try:
                    
                    v_pag = float(df["VALOR"][i].replace(",", "."))
                    v_desc = float(df["desconto"][i].replace(",", "."))
                    v_juros = float(df["juros"][i].replace(",", "."))
                    valor = None


                    # ------------

                    if v_juros > 0:
                        valor = str(round((v_pag + v_desc) - v_juros, 2))
                        df["VALOR"][i] = valor
                    
                    elif v_desc > 0:
                        valor = str(round((v_pag - v_juros) + v_desc, 2))
                        df["VALOR"][i] = valor
                    
                    if valor is not None:
                        print(f"\n ID {i} --------------------------------------------------------")
                        print(f' >>> {df["COMPL_HISTORICO"][i]}')
                        print(f'>>>>>>>>>>> v_pag: {v_pag}')
                        print(f'>>>>>>>>>>> v_desc: {v_desc}')
                        print(f'>>>>>>>>>>> v_juros: {v_juros}')
                        print(f'>>>>>>>>>>> valor: {valor}')
                
                except Exception as e:
                    print(f">>>>>>> ERROR CALCULATE/CONVERT | ERROR: {e}")

                
                count_aux = 0
            
        print("\n\n DF IMPORTAÇÃO COM DE-PARA DE CONTAS ")
        print(df)

        try:
            df = PrepareDataToImportPackage3703.adjust_value_to_decimal_string(dataframe=df, column_name="VALOR", replace_caract=True, replace_from_format_BRL=True)
            df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])
        except Exception as e:
            print(f" ### ERROR ADJUST TO DECIMAL STRING | ERROR: {e}")
            return {}
        df.index = list(range(0, len(df.index)))
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)


        print("\n\n ------- DataFrame contas a pagar PONTO CERTO ------- ")
        print(df.info())
        print(df)

        try:
            df.to_excel("contas a pagar - GARRA.xlsx")
        except:
            pass

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        return {
            "data_table": data_json,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
        }
    
    # ----
    
    def read_xlsx_contas_a_receber_TELL(file, company_session):
        # Pag. Dupl [NFº] [Nome]
        print(f"\n\n ----- Arquivo informado contas a receber - TELL | arquivo: {file}")

        contents = file.read()
        xlsx_bytes = io.BytesIO(contents)
        file = pd.ExcelFile(xlsx_bytes)
        sheet_name = file.sheet_names[0]
        print(f"\n ---> sheet_name: {sheet_name}")
        df = file.parse(sheet_name=sheet_name, dtype='str')
        
        # df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="Situação", list_remove_values=[
        #     "------", ""
        # ])

        df = df.dropna(subset=["CPF/CNPJ"])
        df =  df[ df["Situação"].str.contains("Pago") ]


        df = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df, dict_replace_names={
            "CPF/CNPJ": "CNPJ_ORIGIN",
            "Nome": "nome_pagador",
            "Valor": "VALOR_PAGAMENTO",
            "Recebido": "VALOR_RECEBIDO",
            "Liquidação": "DATA_PAGAMENTO",
            # "Data de vencimento original": "DATA_VENCIMENTO",
            "Juro": "juros",
            "Desconto": "desconto",
            # "Acréscimo": "multa",
        })
        print("\n\n -------------------- DF -------------------- ")
        print(df)


        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_15", cod_empresa=company_session)
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "DATA_PAGAMENTO",
            "CNPJ": "CNPJ_ORIGIN",
            "NOME": "nome_pagador",
            "VALOR": "VALOR_PAGAMENTO",
        })
        # df = df.dropna(subset=['CNPJ_ORIGIN'])
        print("\n\n ------- DF IMPORTAÇÃO JB ------- ")
        print(df)

        # desconto
        # juros
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "D", "TYPE_PROCESS": "desconto"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
            # {"TP": "D", "TYPE_PROCESS": "multa"},
        ])
        
        df.sort_values(by=["nome_pagador", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))

        count_aux = 0
        for i in df.index:

            # if df["VALOR"][i].count(",") == 1:
            #     df["VALOR"][i] = df["VALOR"][i].replace(",", ".", 1)


            if df["VALOR"][i].count(".") == 2:
                df["VALOR"][i] = df["VALOR"][i].replace(".", "", 1).replace(",", ".")
                print(f' -----> VALOR AJUSTADO: {df["VALOR"][i]} | {type(df["VALOR"][i])}')

            if df["VALOR_PAGAMENTO"][i].count(".") == 2:
                df["VALOR_PAGAMENTO"][i] = df["VALOR_PAGAMENTO"][i].replace(".", "", 1).replace(",", ".")
                print(f' -----> VALOR_PAGAMENTO AJUSTADO: {df["VALOR_PAGAMENTO"][i]}')
            
            print(f"""
                --------------------------------
                -->>>> VALOR: {df["VALOR"][i]}
                -->>>> VALOR_PAGAMENTO: {df["VALOR_PAGAMENTO"][i]}
            """)

            
            if count_aux == 0:
                df["TP"][i] = "D"
                df["CONTA"][i] = "-"
                df["VALOR"][i] = df["VALOR_PAGAMENTO"][i]
                count_aux += 1

            elif count_aux == 1:
                
                df["TP"][i] = "D"
                df["CONTA"][i] = "1686"
                df["VALOR"][i] = df["desconto"][i]
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("Recebimento Dupl", "Desconto Concedido Dupl ")
                count_aux += 1

            elif count_aux == 2:

                df["TP"][i] = "C"
                df["CONTA"][i] = "1663"
                df["VALOR"][i] = df["juros"][i]
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("Recebimento Dupl", "Recebimento Juros Dupl ")
                count_aux += 1

            elif count_aux == 3:

                df["TP"][i] = "C"
                df["CONTA"][i] = ""
                
                try:
                    
                    v_pag = float(df["VALOR"][i].replace(",", "."))
                    v_desc = float(df["desconto"][i].replace(",", "."))
                    v_juros = float(df["juros"][i].replace(",", "."))
                    valor = None


                    # ------------

                    if v_juros > 0:
                        valor = str(round((v_pag + v_desc) - v_juros, 2))
                        df["VALOR"][i] = valor
                    
                    elif v_desc > 0:
                        valor = str(round((v_pag - v_juros) + v_desc, 2))
                        df["VALOR"][i] = valor
                    
                    if valor is not None:
                        print(f"\n ID {i} --------------------------------------------------------")
                        print(f' >>> {df["COMPL_HISTORICO"][i]}')
                        print(f'>>>>>>>>>>> v_pag: {v_pag}')
                        print(f'>>>>>>>>>>> v_desc: {v_desc}')
                        print(f'>>>>>>>>>>> v_juros: {v_juros}')
                        print(f'>>>>>>>>>>> valor: {valor}')
                
                except Exception as e:
                    print(f">>>>>>> ERROR CALCULATE/CONVERT | ERROR: {e}")

                
                count_aux = 0
            
        print("\n\n DF IMPORTAÇÃO COM DE-PARA DE CONTAS ")
        print(df)

        try:
            df = PrepareDataToImportPackage3703.adjust_value_to_decimal_string(dataframe=df, column_name="VALOR", replace_caract=True, replace_from_format_BRL=True)
            df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])
        except Exception as e:
            print(f" ### ERROR ADJUST TO DECIMAL STRING | ERROR: {e}")
            return {}
        df.index = list(range(0, len(df.index)))
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)


        print("\n\n ------- DataFrame contas a receber TELL ------- ")
        print(df.info())
        print(df)


        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        return {
            "data_table": data_json,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
        }
    
    # ----
    
    def read_xlsx_contas_a_pagar_TELL(file, company_session):
        # Pag. Dupl [NFº] [Nome]
        print(f"\n\n ----- Arquivo informado contas a pagar - TELL | arquivo: {file}")

        contents = file.read()
        xlsx_bytes = io.BytesIO(contents)
        file = pd.ExcelFile(xlsx_bytes)
        sheet_name = file.sheet_names[0]
        print(f"\n ---> sheet_name: {sheet_name}")
        df = file.parse(sheet_name=sheet_name, dtype='str')
        
        # df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="Situação", list_remove_values=[
        #     "------", ""
        # ])

        df = df.dropna(subset=["CPF/CNPJ"])
        df =  df[ df["Situação"].str.contains("Pago") ]


        df = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df, dict_replace_names={
            "CPF/CNPJ": "CNPJ_ORIGIN",
            "Nome": "nome_pagador",
            "Pago": "VALOR_PAGAMENTO",
            "Recebido": "VALOR_RECEBIDO",
            "Liquidação": "DATA_PAGAMENTO",
            # "Data de vencimento original": "DATA_VENCIMENTO",
            "Juro": "juros",
            "Desconto": "desconto",
            # "Acréscimo": "multa",
        })
        print("\n\n -------------------- DF -------------------- ")
        print(df)


        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_16", cod_empresa=company_session)
        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "DATA_PAGAMENTO",
            "CNPJ": "CNPJ_ORIGIN",
            "NOME": "nome_pagador",
            "VALOR": "VALOR_PAGAMENTO",
        })
        # df = df.dropna(subset=['CNPJ_ORIGIN'])
        print("\n\n ------- DF IMPORTAÇÃO JB ------- ")
        print(df)
        df["DATA_PAGAMENTO"] = list(map(lambda x: datetime.datetime.strptime(x, "%d/%m/%Y"), df["DATA_PAGAMENTO"].values))

        # desconto
        # juros
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "D", "TYPE_PROCESS": "desconto"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
            # {"TP": "D", "TYPE_PROCESS": "multa"},
        ])
        
        df.sort_values(by=["nome_pagador", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))

        count_aux = 0
        for i in df.index:

            # if df["VALOR"][i].count(",") == 1:
            #     df["VALOR"][i] = df["VALOR"][i].replace(",", ".", 1)


            if df["VALOR"][i].count(".") == 2:
                df["VALOR"][i] = df["VALOR"][i].replace(".", "", 1).replace(",", ".")
                print(f' -----> VALOR AJUSTADO: {df["VALOR"][i]} | {type(df["VALOR"][i])}')

            if df["VALOR_PAGAMENTO"][i].count(".") == 2:
                df["VALOR_PAGAMENTO"][i] = df["VALOR_PAGAMENTO"][i].replace(".", "", 1).replace(",", ".")
                print(f' -----> VALOR_PAGAMENTO AJUSTADO: {df["VALOR_PAGAMENTO"][i]}')
            
            print(f"""
                --------------------------------
                -->>>> VALOR: {df["VALOR"][i]}
                -->>>> VALOR_PAGAMENTO: {df["VALOR_PAGAMENTO"][i]}
            """)

            
            if count_aux == 0:
                df["TP"][i] = "D"
                df["CONTA"][i] = ""
                
                try:
                    
                    v_pag = float(df["VALOR"][i].replace(",", "."))
                    v_desc = float(df["desconto"][i].replace(",", "."))
                    v_juros = float(df["juros"][i].replace(",", "."))
                    valor = None
                    
                    # ------------

                    if v_juros > 0:
                        valor = str(round((v_pag + v_desc) - v_juros, 2))
                        df["VALOR"][i] = valor
                    
                    elif v_desc > 0:
                        valor = str(round((v_pag - v_juros) + v_desc, 2))
                        df["VALOR"][i] = valor
                    
                    if valor is not None:
                        print(f"\n ID {i} --------------------------------------------------------")
                        print(f' >>> {df["COMPL_HISTORICO"][i]}')
                        print(f'>>>>>>>>>>> v_pag: {v_pag}')
                        print(f'>>>>>>>>>>> v_desc: {v_desc}')
                        print(f'>>>>>>>>>>> v_juros: {v_juros}')
                        print(f'>>>>>>>>>>> valor: {valor}')
                
                except Exception as e:
                    print(f">>>>>>> ERROR CALCULATE/CONVERT | ERROR: {e}")
                count_aux += 1

            elif count_aux == 1:
                
                df["TP"][i] = "C"
                df["CONTA"][i] = "1664"
                df["VALOR"][i] = df["desconto"][i]
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("Pagamento Dupl", "Desconto Obtido Dupl ")
                count_aux += 1

            elif count_aux == 2:

                df["TP"][i] = "D"
                df["CONTA"][i] = "1688"
                df["VALOR"][i] = df["juros"][i]
                df["COMPL_HISTORICO"][i] = df["COMPL_HISTORICO"][i].replace("Pagamento Dupl", "Pagamento Juros Dupl ")
                count_aux += 1

            elif count_aux == 3:
                df["TP"][i] = "C"
                df["CONTA"][i] = "-"
                df["VALOR"][i] = df["VALOR_PAGAMENTO"][i]
                df["TYPE_PROCESS"][i] = "account_code_credit"
                
                count_aux = 0
        
        try:
            df = PrepareDataToImportPackage3703.adjust_value_to_decimal_string(dataframe=df, column_name="VALOR", replace_caract=True, replace_from_format_BRL=True)
            df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00"])
        except Exception as e:
            print(f" ### ERROR ADJUST TO DECIMAL STRING | ERROR: {e}")
            return {}
        df.index = list(range(0, len(df.index)))
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)


        print("\n\n ------- DataFrame contas a pagar TELL ------- ")
        print(df.info())
        print(df)


        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

        return {
            "data_table": data_json,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
        }

    # ----
    
    def read_pdf_contas_a_pagar_ABBRACCIO(file, company_session):

        list_df = list()
        list_page_erros = list()
        
        print(" ----------- FILES ----------- ")
        print(file)

        list_files = list()

        for file_temp in file.getlist("file_1"):
   
            pdf_bytes = io.BytesIO(file_temp.read())  # Leia diretamente o arquivo_temp
            pdf_reader = PdfReader(pdf_bytes)

            list_files.append(pdf_reader)

            print(" ----------- pdf_reader ----------- ")
            print(pdf_reader)
      
     
            print(f"\n\n ----- Arquivo PDF informado comprovante ABBRACCIO ----- ")

            data_to_table = {
                # # # # ---------- IDENTIFICADORES
                "nome_beneficiario": list(),
                "cnpj_beneficiario": list(),

                # # # # # ---------- DATAS
                "data_de_debito": list(),
                # "data_de_vencimento": list(),

                # # # ---------- VALORES
                "valor": list(),
                "desconto": list(),
                "juros": list(),
                "multa": list(),
                "abatimento": list(),
                "valor_total": list(),
            }

            list_data_pages = list()
            index_page = 0
            print(f" TT PAGES: {len(pdf_reader.pages)}")

            for index_page in range(len(pdf_reader.pages)):
                try:
                    print(f"\n\n\n ---- INDEX PAGE: {index_page}")
                    
                    page = pdf_reader.pages[index_page]
                    
                    data_page = page.extract_text()


                    if "CPF/CNPJ Beneficiário" in data_page:
                        print("\n\n ----------------------- DATA EXTRACT ----------------------- ")
                        print(data_page)

                        valor = "0.00"
                        valor_total = "0.00"
                        juros = "0.00"
                        multa = "0.00"
                        desconto = "0.00"
                        abatimento = "0.00"

                        nome_beneficiario = ""
                        cnpj_beneficiario = ""
                        
                        for i in range(len(data_page)):
                            
                            # # # --------------------------------------------------------------------------------- VALOR DOCUMENTO
                            if "Descrição do Pagamento:" == data_page[i:i+23]:
                                data_split = data_page[i+23:i+300].split("(R$):")
                                print("\n\n >> VALOR DOCUMENTO ")
                                print(data_split)

                                valor = data_split[5].split(" ")[0].replace(",", ".").strip()
                                desconto = data_split[1].split(" ")[0].replace(",", ".").strip()
                                juros = data_split[3].split(" ")[0].replace(",", ".").strip()
                                multa = data_split[2].split(" ")[0].replace(",", ".").strip()
                                abatimento = data_split[4].split(" ")[0].replace(",", ".").strip()
                                valor_total = data_split[0].split(" ")[0].replace(",", ".").strip()
                                data_de_debito = data_split[6].split(" ")[0].strip()
                            
                            if "Nome Pagador:" == data_page[i:i+13]:
                                data_split = data_page[i+13:i+200].split("CPF/CNPJ Beneficiário:")
                                print("\n\n >> DATA SPLIT PAGADOR ")
                                print(data_split)
                                nome_beneficiario = data_split[1].split("Nome Fantasia")[0].strip()
                                cnpj_beneficiario = data_split[0].strip()

                            

                                
                        data_to_table["nome_beneficiario"].append(nome_beneficiario)
                        data_to_table["cnpj_beneficiario"].append(cnpj_beneficiario)
                        data_to_table["valor"].append(valor)
                        data_to_table["desconto"].append(desconto)
                        data_to_table["juros"].append(juros)
                        data_to_table["multa"].append(multa)
                        data_to_table["abatimento"].append(abatimento)
                        data_to_table["valor_total"].append(valor_total)
                        data_to_table["data_de_debito"].append(data_de_debito)

                except Exception as e:
                    print(f" ### ERROR EXTRACT DATA PDF | ERROR: {e}")
                    list_page_erros.append({index_page: e})
        
            print("\n\n ---------------- DATAFRAME EXTRACT ---------------- ")
            df = pd.DataFrame.from_dict(data_to_table)
            print(df)
            list_df.append(df)

        print("\n\n ---------------- DATAFRAMES CONCAT EXTRACT ---------------- ")
        df = pd.concat(list_df)
        df.index = list(range(0, len(df.index)))
        print(df)

        print("\n\n ---------- list_page_erros ---------- ")
        print(list_page_erros)

        
        df = PrepareDataToImportPackage3703.create_layout_JB(dataframe=df, model="model_18", cod_empresa=company_session)

        df = PrepareDataToImportPackage3703.transpose_values(dataframe=df, dict_cols_transpose={
            "DATA": "data_de_debito",
            "CNPJ": "cnpj_beneficiario",
            "NOME": "nome_beneficiario",
            "VALOR": "valor",
        })
        print("\n ----------------- LAYOUT JB ----------------- ")
        print(df)

        # # # # desconto
        # # # # abatimento
        # # # # bonificacao | neste caso não possui
        # # # # multa
        # # # # juros
        
        df = PrepareDataToImportPackage3703.duplicate_dataframe_rows_lote(dataframe=df, list_update_cols=[
            {"TP": "C", "TYPE_PROCESS": "comum"},
            {"TP": "D", "TYPE_PROCESS": "juros"},
            {"TP": "D", "TYPE_PROCESS": "multa"},
            {"TP": "C", "TYPE_PROCESS": "desconto"},
            {"TP": "C", "TYPE_PROCESS": "abatimento"},
        ])

        df.sort_values(by=["nome_beneficiario", "GRUPO_LCTO", "TP"], inplace=True)
        df.index = list(range(0, len(df.index)))

        count_aux = 0
        for i in df.index:

            print(f" ----> INDEX: {i} | count_aux: {count_aux}")

            if count_aux == 0:
                df["TP"][i] = "C"
                df["VALOR"][i] = df["valor_total"][i]
                df["TYPE_PROCESS"][i] = "account_code_credit"
                count_aux += 1

            elif count_aux == 1:
                df["TP"][i] = "D"
                df["VALOR"][i] = df["juros"][i]
                df["CONTA"][i] = "947"
                count_aux += 1

            elif count_aux == 2:
                df["TP"][i] = "D"
                df["VALOR"][i] = df["multa"][i]
                df["CONTA"][i] = "972"
                count_aux += 1

            elif count_aux == 3:
                df["TP"][i] = "C"
                df["VALOR"][i] = df["abatimento"][i]
                df["CONTA"][i] = "936"
                count_aux += 1
    
            elif count_aux == 4:
                df["TP"][i] = "C"
                df["VALOR"][i] = df["desconto"][i]
                df["CONTA"][i] = "936"
                count_aux += 1

            elif count_aux == 5:
                df["TP"][i] = "D"
                df["VALOR"][i] = df["valor"][i]
                df["CONTA"][i] = ""
                count_aux = 0
        
        df = PrepareDataToImportPackage3703.filter_data_dataframe(daraframe=df, name_column="VALOR", list_remove_values=["0.00", "0,00"])

        df.index = list(range(0, len(df.index)))
        df = PrepareDataToImportPackage3703.create_cod_erp_to_dataframe(dataframe=df)

        print("\n\n ---------------------------- DF LAYOUT JB ---------------------------- ")
        print(df.info())
        print(df)

        tt_rows = len(df)
        tt_debit    = len(df[df["TP"] == "D"])
        tt_credit   = len(df[df["TP"] == "C"])

        data_json = json.loads(df.to_json(orient="table"))
        # print(data_json)

        print(f"""
            --------- CONFIG CONTAS
            --> tt_rows: {tt_rows}
            --> tt_debit: {tt_debit}
            --> tt_credit: {tt_credit}
        """)

  
        return {
            "data_table": data_json ,
            "tt_rows": tt_rows,
            "tt_debit": tt_debit,
            "tt_credit": tt_credit,
            "list_page_erros": [],
        }

    # ----

    def read_file_plano_de_contas(file, data_query):
        try:
            print(f"\n\n ----- Arquivo informado PLANO DE CONTAS: {file}")

            contents = file.read()
            xlsx_bytes = io.BytesIO(contents)
            file = pd.ExcelFile(xlsx_bytes)
            sheet_name = file.sheet_names[0]

            df = file.parse(sheet_name=sheet_name, dtype='str')
            df = df[df["Saldo atual"] != "0,00"]

            df = df[ df["Cta. título"].isin(["2-Não"]) ][ ["Classificação", "Conta", "Nome da conta contábil/C. Custo", "Tipo conta"] ]
            df["NEW_CODE"] = ""
            df = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df, dict_replace_names={
                "Classificação": "CLASSIFICACAO",
                "Conta": "CONTA",
                "Nome da conta contábil/C. Custo": "NOME_CONTA_CENTRO_CUSTO",
                "Tipo conta": "TTIPO_CONTA",
            })
            

            # list_remove = ["        Socio - A", "        Socio - B", "        Socio - C"]
            # df = df[ ~ df["NOME_CONTA_CENTRO_CUSTO"].isin(list_remove) ]
            list_remove = ["Socio - A", "Socio - B", "Socio - C"]
            df = df[~df['NOME_CONTA_CENTRO_CUSTO'].str.contains('|'.join(list_remove))]

            # list_remove = ["3-DRE"]
            # df = df[~df['TTIPO_CONTA'].str.contains('|'.join(list_remove))]
            
            df.index = list(range(0, len(df.index)))

            for i in df.index:
                code_old = data_query.get(df["CONTA"][i])
                if code_old:
                    df["NEW_CODE"][i] = code_old

            df["CLASSE"] = True
            df.loc[df['NEW_CODE'] == '', 'CLASSE'] = False

            tt_rows = len(df)
            df_json = json.loads(df.to_json(orient="table"))["data"]
            
            print(df)
            return {
                "df_json": df_json,
                "tt_rows": tt_rows,
            }
        except Exception as e:
            return {
                    "code": 400,
                    "msg": "erro ao ler arquivo plano de contas",
                }

    # ----

    def read_file_plano_de_contas_v2(file, data_query):

        print(f"\n\n ----- Arquivo informado PLANO DE CONTAS: {file}")

        contents = file.read()
        xlsx_bytes = io.BytesIO(contents)
        file = pd.ExcelFile(xlsx_bytes)
        sheet_name = file.sheet_names[0]

        df = file.parse(sheet_name=sheet_name, dtype='str')
        # df = df[df["Saldo atual"] != "0,00"]

        print("\n\n ------------------ DF PARSE ------------------ ")
        print(df)

        df = df[~ df["TITULO"].isin(["1-Sintética "]) ][ ["CODIGO", "DESCRICAO", "CLASSIFICACAO", "TITULO", "TIPO", "NATUREZA"] ]
        df["NEW_CODE"] = ""

        df = PrepareDataToImportPackage3703.rename_columns_dataframe(dataframe=df, dict_replace_names={
            "CLASSIFICACAO": "CLASSIFICACAO",
            "CODIGO": "CONTA",
            "DESCRICAO": "NOME_CONTA_CENTRO_CUSTO",
            "TIPO": "TTIPO_CONTA",
        })
        
        print(" ---------------- DF RENOMEADO ---------------- ")
        print(df)

        # list_remove = ["Socio - A", "Socio - B", "Socio - C"]
        # df = df[~df['NOME_CONTA_CENTRO_CUSTO'].str.contains('|'.join(list_remove))]

        df.index = list(range(0, len(df.index)))

        for i in df.index:
            code_old = data_query.get(df["CONTA"][i])
            if code_old:
                df["NEW_CODE"][i] = code_old

        df["CLASSE"] = True
        df.loc[df['NEW_CODE'] == '', 'CLASSE'] = False

        

        tt_rows = len(df)
        df_json = json.loads(df.to_json(orient="table"))["data"]
        
        print("\n\n ----------------- PLANO DE CONTAS V2 ----------------- ")
        print(df)
        return {
            "df_json": df_json,
            "tt_rows": tt_rows,
        }
    
    def check_text_to_tag(data, dict_tags_to_text):
        
        data_split = data.split()
        count_aux = len(data_split)
        # dict_tags_to_text = dict()
        for x in data_split:
            # print(f" x ---------> {x}")
            try:
                data_temp = x.split(":")

                print("\n ----------------------------- DATA TO TEXT ----------------------------- ")
                print(x)

                for j in data_temp:
                    print(f" ---------> J: {j}")
                    print(x)

                    if dict_tags_to_text.get(j):
                        dict_tags_to_text[j]  = dict_tags_to_text.get(j) + 1
                    else:
                        dict_tags_to_text.update({j: 1})

                
                print("\n ----------------------------- ")

            except Exception as e:
                print(f" ### ERROR CHECK TEXT TO TAG | ERROR: {e}")
        
        return dict_tags_to_text


    def calculate_file_stock_H020(file_dir, percentage):
        
        # file_dir = io.BytesIO(file_dir)
        file = file_dir.readlines()
        print(">>>>>>>>>> ", file, type(file))

        
        data_new_file = list()
        for row in file:
            try:
                row = row.decode("utf-8")
            except:
                row = row.decode("latin-1")

            print(">>>> ", row)
            data_new_file.append(row)
            if "|H010|" == row[0:6]:
                values_temp = row.split("|")
                value_origin = values_temp[6]

                value_calc = float(value_origin.replace(",", ".").strip())
                value_calc = round( (value_calc * float(percentage)) / 100, 3)
                value_calc = round( value_calc, 2)
                value_calc = str(value_calc).replace(".", ",")
                


                if value_calc[len(value_calc)-2] == ",":
                    value_calc = value_calc + "0"

                value_H020 = f"|H020|000|{value_origin}|{value_calc}|"
                data_new_file.append(value_H020)

                print(f"""
                    ---------------------
                    row: {row}
                    values_temp: {values_temp}
                    value_origin: {value_origin}
                    value_calc: {value_calc}
                    value_H020: {value_H020}
                """)
        
        print(data_new_file)
        return {
            "data_new_file": data_new_file,
            "file_name": file_dir,
        }


