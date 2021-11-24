from datetime import datetime
import disponibilidadefuncoes
from decimal import Decimal
import shutil
import csv
import os

str_data_forma = '%d/%m/%Y'

# Data comparação
# data_hoje = datetime.strptime('20/09/2021', str_data_forma).date()
data_hoje = datetime.today()
print(f'Serão obtidos saldos com data menor que a data atual: {data_hoje.strftime(str_data_forma)}')

# Quantidade maxima de linhas a ler para o cabecalho, maior atual APL Bradesco
cabecalho_linhas = 55

nome_bancos = {'001': 'B. Brasil', '104': 'B. CEF', '237': 'B. Bradesco', '033': 'B. Santander',
               '041': 'B. Banrisul', '748': 'B. Sicredi', '422': 'B. Safra', }

tipos_apls = {'Diferenciad': 'RENDA FIXA', 'Prefixado': 'RENDA FIXA', 'MEGA': 'RENDA FIXA',
              'RUBI': 'RENDA FIXA', 'CDB-FACIL': 'CDB', 'Resgate Autom': 'CDB',
              'q.dispon': 'RENDA FIXA', '(100,00%)': 'RENDA FIXA', 'MODER': 'MULTIMERCADO',
              'SPECI': 'RENDA FIXA', 'EXECUTIVE': 'RENDA FIXA'}

# Bancos posições e contas
bancos = {'001': {'pst_linha_cc': 8, 'pst_data': 1, 'pst_saldo_cc': -2,
                  'cc_txt': True, 'apl_incluso': True, 'qt_linhas_busca_conta': 2,
                  'pst_linha_saldo_apl': 8, 'pst_saldo_apl': 1,
                  'contas': {'21397-7': {'apl': None, 'prefixo': 'OAB'},
                             '52500-6': {'apl': {'apl1': 'Diferenciad'}, 'prefixo': 'OAB'},
                             '52600-2': {'apl': {'apl1': 'Diferenciad'}, 'prefixo': 'OAB'},
                             '52901-X': {'apl': None, 'prefixo': 'OAB'},
                             '52903-6': {'apl': {'apl1': 'Diferenciad'}, 'prefixo': 'OAB'},
                             '52904-4': {'apl': {'apl1': 'Diferenciad', 'apl2': 'Prefixado'}, 'prefixo': 'FIDA'},
                             '152600-6': {'apl': {'apl1': 'Diferenciad'}, 'prefixo': 'OAB'},
                             '152700-2': {'apl': None, 'prefixo': 'OAB'},
                             '152800-9': {'apl': None, 'prefixo': 'OAB'},
                             '152900-5': {'apl': {'apl1': 'Diferenciad', 'apl2': 'Prefixado'},
                                          'prefixo': 'EXAME DE ORDEM'}
                             }
                  },
          '104': {'pst_linha_cc': 11, 'pst_data': 1, 'pst_saldo_cc': -2,
                  'cc_txt': True, 'apl_incluso': False, 'qt_linhas_busca_conta': 5,
                  'pst_linha_cc_apl': 47,
                  'pst_linha_saldo_apl': 47, 'pst_saldo_apl': 2,
                  'contas': {'1416-0': {'apl': {'apl1': 'MEGA'}, 'prefixo': 'OAB'},
                             '1417-9': {'apl': {'apl1': 'RUBI'}, 'prefixo': 'FIDA'}
                             }
                  },
          '237': {'pst_linha_cc': 2, 'pst_data': 1, 'pst_saldo_cc': -1,
                  'cc_txt': True, 'apl_incluso': False, 'qt_linhas_busca_conta': 2,
                  'pst_linha_cc_apl': 9,
                  'pst_linha_saldo_apl': 25,  'pst_saldo_apl': 1,
                  'contas': {'29383-0': {'apl': {'apl1': 'CDB-FACIL'}, 'prefixo': 'OAB'},
                             '29384-9': {'apl': {'apl1': 'CDB-FACIL'}, 'prefixo': 'FIDA'}
                             }
                  },
          '033': {'pst_linha_cc': 7, 'pst_data': 1, 'pst_saldo_cc': -1,
                  'cc_txt': True, 'apl_incluso': True, 'qt_linhas_busca_conta': 2,
                  'pst_linha_cc_apl': 11,
                  'pst_linha_saldo_apl': 24, 'pst_saldo_apl': 1,
                  'contas': {'13.002957.5': {'apl': {'apl1': 'Resgate Autom', 'apl2': 'q.dispon'}, 'prefixo': 'OAB'},
                             '13.002958.2': {'apl': {'apl1': 'Resgate Autom', 'apl2': 'q.dispon'}, 'prefixo': 'FIDA'}
                             }
                  },
          '041': {'pst_linha_cc': 3, 'pst_data': 1, 'pst_saldo_cc': -1,
                  'cc_txt': True, 'apl_incluso': True, 'qt_linhas_busca_conta': 2,
                  'pst_linha_saldo_apl': 23, 'pst_saldo_apl': 1,
                  'contas': {'06.851005.0-6': {'apl': None, 'prefixo': 'OAB'}
                             }
                  },
          '422': {'pst_linha_cc': 11, 'pst_data': 1, 'pst_saldo_cc': -1,
                  'cc_txt': True, 'apl_incluso': False, 'qt_linhas_busca_conta': 2,
                  'pst_linha_cc_apl': 5,
                  'pst_linha_saldo_apl': 45, 'pst_saldo_apl': 2,
                  'contas': {'23066-3': {'apl': {'apl1': 'MODER', 'apl2': 'SPECI',
                                                 'apl3': 'EXECUTIVE'}, 'prefixo': 'FIDA'}
                             }
                  },
          '748': {'pst_linha_cc': 7, 'pst_data': 1, 'pst_saldo_cc': -1,
                  'cc_txt': True, 'apl_incluso': False, 'qt_linhas_busca_conta': 5,
                  'pst_linha_cc_apl': 3,
                  'pst_linha_saldo_apl': 20, 'pst_saldo_apl': 2,
                  'contas': {'58618-8': {'apl': {'apl1': '(100,00%)'}, 'prefixo': 'OAB'}
                             }
                  },
          }

# Dicionario que receberá todos os dados de contas saldos e data
biblioteca_saldos = {}

# Guardando maior data obtida para renomear arquivos APL
maior_data = None

# Retorna um diretorio referente ao caminho completo até a pasta do projeto
os.chdir('..')
# Obtendo caminho completo até o diretorio anterior ao diretorio do projeto
cwd = os.getcwd()

src = cwd + '\\import\\'
dst = cwd + '\\import\\processado\\'

lista_de_arquivos = os.listdir(src)

# Prenchendo os dados de todas as contas com None
for chave, dados_banco in bancos.items():
    for conta in dados_banco['contas']:
        prefixo = dados_banco.get('contas').get(conta).get('prefixo')
        apls = dados_banco.get('contas').get(conta).get('apl')
        apl_list = {}

        if apls is not None:
            for nome_apl in apls.values():
                apl_list[nome_apl] = None
        else:
            apl_list = None

        saldos = {'cod_banco': chave, 'prefixo': prefixo, 'data': None, 'saldo_cc': None, 'apls': apl_list}
        biblioteca_saldos[conta] = saldos

# Removendo arquivo anterior de disponibilidade_dia_anterior.csv
try:
    os.remove(os.path.join(cwd, 'disponibilidade_dia_anterior.csv'))
except FileNotFoundError:
    print('Arquivo disponibilidade_dia_anterior.csv não encontrado para deletar')

# Renomeando arquivo de diponibilidade do dia anterior
try:
    os.rename(os.path.join(cwd, 'disponibilidade.csv'),
              os.path.join(cwd, 'disponibilidade_dia_anterior.csv'))
except FileNotFoundError:
    print('Arquivo disponibilidade.csv não encontrado para renomear')

# Percorrendo lista de arquivos para guardar primeiramente arquivos com saldos cc
# ou que tenham saldos cc e de aplicações no mesmo arquivo
for arquivo_txt in lista_de_arquivos:

    arquivo_processado = None
    arquivo_erro = None

    if os.path.isfile(src + arquivo_txt) and arquivo_txt.split('.')[1].lower() in ['txt', 'csv']:

        # Verifica se é ANSI e não faz nada, se for do tipo UTF-8-BOM converte para ANSI
        disponibilidadefuncoes.convert_ansi(src + arquivo_txt)

        with open(src + arquivo_txt) as arquivo:
            cabecalho = []
            for contador in range(0, cabecalho_linhas):
                try:
                    ln_arquivo = arquivo.readline()
                    cabecalho.append(ln_arquivo)
                except UnicodeDecodeError:
                    cabecalho = None
                    arquivo_erro = arquivo_txt
                    break

            if cabecalho is not None:
                # Caso boolena verdadeiro recebe os parametros para iniciar função de obtenção saldos,
                # caso falso na variavel dados_banco recebe lista de valores testados para impressão no
                # caso de também falhar na pesquisa por contas de aplicação
                tupla_dados = disponibilidadefuncoes.verifica_conta_cc(bancos, cabecalho, tipo='SALDO_CC')
                if tupla_dados[0]:
                    dados_banco = tupla_dados[1]
                    conta = tupla_dados[2]

                    # lista temporaria p/ receber linhas do arquivo lido
                    dados_arquivo = []

                    # colocando cursor no inicio do arquivo
                    arquivo.seek(0)
                    dados_arquivo = arquivo.readlines()

                    # lista de Apls
                    apl_list = biblioteca_saldos.get(conta).get('apls')

                    # Recebendo os dados apartir da função
                    saldos = disponibilidadefuncoes.saldos_conta(data_hoje, dados_arquivo, dados_banco, conta, apl_list)

                    # Guardando as informações no biblioteca de saldos
                    biblioteca_saldos[conta]['data'] = saldos.get('data')
                    biblioteca_saldos[conta]['saldo_cc'] = saldos.get('saldo_cc')
                    biblioteca_saldos[conta]['apls'] = saldos.get('apl')

                    # Guardando nome do arquivo para depois move-lo para pasta de item processados
                    arquivo_processado = arquivo_txt

        if arquivo_erro is not None:
            # Renomeando arquivo com erro
            try:
                rename_arquivo = f'{arquivo_erro.split(".")[0]}.txt_erro'
                os.rename(os.path.join(src, arquivo_erro), os.path.join(src, rename_arquivo))
            except FileExistsError:
                pass

        if arquivo_processado is not None:
            # Preparando dados para renomear arquivos processados
            conta = conta.replace('.', '')
            data_rename = saldos.get('data')

            # Guardando maior data para renomear arquivos APL
            dt = datetime.strptime(data_rename, str_data_forma).date()
            if maior_data is None:
                maior_data = dt
            elif dt > maior_data:
                maior_data = dt

            data_rename = data_rename[6:10] + data_rename[2:6] + data_rename[0:2]
            data_rename = data_rename.replace('/', '-')
            if saldos.get('saldo_cc') is not None:
                saldo_cc_rename = saldos.get('saldo_cc')
            else:
                saldo_cc_rename = '0'
            saldo_cc_rename = saldo_cc_rename.replace(',', '_')

            if saldos.get('apl') is not None:
                apl_list = {}
                for idx, saldo_apl in saldos.get('apl').items():
                    if saldo_apl is not None:
                        apl_list[idx] = saldo_apl
                if len(apl_list) > 0:
                    saldo_apl_rename = disponibilidadefuncoes.montar_nome_arquivo(apl_list)
                    rename_arquivo = f'{data_rename}_{conta}_CC({saldo_cc_rename})_APL({saldo_apl_rename}).txt'
                else:
                    rename_arquivo = f'{data_rename}_{conta}_CC({saldo_cc_rename}).txt'
            else:
                rename_arquivo = f'{data_rename}_{conta}_CC({saldo_cc_rename}).txt'

            # Renomeando arquivo processado
            try:
                os.rename(os.path.join(src, arquivo_processado), os.path.join(src, rename_arquivo))
            except FileExistsError:
                pass

            # Guardando novo nome em arquivo_processado
            arquivo_processado = rename_arquivo

            # Verificando e Movendo arquivo para pasta de item processado
            shutil.move(os.path.join(src, arquivo_processado), os.path.join(dst, arquivo_processado))

# obtendo lista de arquivos restantes
lista_de_arquivos = os.listdir(src)

# Percorrendo resto da lista de arquivos que contenham somente informações de aplicações
# ou que não estejam registradas nos bancos cadastrados
for arquivo_txt in lista_de_arquivos:

    arquivo_processado = None
    saldo_apl_rename = None

    if os.path.isfile(src + arquivo_txt) and arquivo_txt.split('.')[1].lower() in ['txt', 'csv']:
        with open(src + arquivo_txt) as arquivo:
            cabecalho = []
            for contador in range(0, cabecalho_linhas):
                ln_arquivo = arquivo.readline()
                cabecalho.append(ln_arquivo)

            # Caso boolena verdadeiro recebe os parametros para iniciar função de obtenção saldos aplicações,
            # caso falso na variavel dados_banco recebe lista de valores testados para impressão no
            # caso de também falhar na pesquisa por contas de aplicação
            tupla_dados = disponibilidadefuncoes.verifica_conta_cc(bancos, cabecalho, tipo='SALDO_APL')
            if tupla_dados[0]:
                dados_banco = tupla_dados[1]
                conta = tupla_dados[2]

                if dados_banco.get('contas').get(conta).get('apl') is not None:
                    # lista temporaria p/ receber linhas do arquivo lido
                    dados_arquivo = []

                    # colocando cursor no inicio do arquivo
                    arquivo.seek(0)
                    dados_arquivo = arquivo.readlines()

                    # lista de Apls
                    apl_list = biblioteca_saldos.get(conta).get('apls')

                    # Recebendo os dados apartir da função
                    saldo_apl = disponibilidadefuncoes.obter_saldo_lista_apl(dados_arquivo, dados_banco, apl_list)

                    # Verificando saldos apls já guardados
                    biblioteca_saldos[conta]['apls'] = saldo_apl

                    if saldo_apl is not None:
                        saldo_apl_rename = disponibilidadefuncoes.montar_nome_arquivo(saldo_apl)

                    # Guardando nome do arquivo para depois move-lo para pasta de item processados
                    arquivo_processado = arquivo_txt

        if arquivo_processado is not None:
            # Preparando dados para renomear arquivos processados
            conta = conta.replace('.', '')
            if maior_data is None:
                data_rename = data_hoje.strftime(str_data_forma)
            else:
                data_rename = maior_data.strftime(str_data_forma)
            data_rename = data_rename[6:10] + data_rename[2:6] + data_rename[0:2]
            data_rename = data_rename.replace('/', '-')
            saldo_apl_rename = saldo_apl_rename.replace(',', '_')
            rename_arquivo = f'{data_rename}_{conta}_APL({saldo_apl_rename}).txt'

            # Renomeando arquivo processado
            try:
                os.rename(os.path.join(src, arquivo_processado), os.path.join(src, rename_arquivo))
            except FileExistsError:
                pass

            # Guardando novo nome em arquivo_processado
            arquivo_processado = rename_arquivo

            # Verificando e Movendo arquivo para pasta de item processado
            shutil.move(os.path.join(src, arquivo_processado), os.path.join(dst, arquivo_processado))

"""
arquivo = 'disponibilidade.csv'
with open(arquivo, 'w', newline='') as arquivo_csv:
    escritor = csv.writer(arquivo_csv, delimiter=';')
    escritor.writerow(('CONTA', 'DATA', 'SALDO CC', 'SALDO APL1', 'SALDO APL2', 'TOTAL'))
    total_cc = []
    total_apl1 = []
    total_apl2 = []
    for chave in biblioteca_saldos:
        conta = chave
        data = biblioteca_saldos[chave].get('data')

        saldo_cc = biblioteca_saldos[chave].get('saldo_cc')
        # verifica se há valor para validar se foi importado ou não
        if saldo_cc is not None:
            # Convertendo valores para calcular o total
            cc = Decimal(saldo_cc.replace(',', '.'))
            total_cc.append(cc)
        else:
            saldo_cc = 'NÃO IMPORTADO'
            cc = 0
            total_cc.append(cc)

        saldo_apl1 = biblioteca_saldos[chave].get('apl1')
        # verifica se há valor para validar se foi importado ou não
        if saldo_apl1 is not None:
            apl1 = Decimal(saldo_apl1.replace(',', '.'))
            total_apl1.append(apl1)
        else:
            saldo_apl1 = 'NÃO IMPORTADO'
            apl1 = 0
            total_apl1.append(apl1)

        saldo_apl2 = biblioteca_saldos[chave].get('apl2')
        # verifica se há valor para validar se foi importado ou não
        if saldo_apl2 is not None:
            apl2 = Decimal(saldo_apl2.replace(',', '.'))
            total_apl2.append(apl2)
        else:
            saldo_apl2 = 'NÃO IMPORTADO'
            apl2 = 0
            total_apl2.append(apl2)

        total = str(cc + apl1 + apl2).replace('.', ',')
        item = (conta, data, saldo_cc, saldo_apl1, saldo_apl2, total)
        escritor.writerow(item)
    total_geral_cc = str(sum(total_cc)).replace('.', ',')
    total_geral_apl1 = str(sum(total_apl1)).replace('.', ',')
    total_geral_apl2 = str(sum(total_apl2)).replace('.', ',')
    total_geral = str(sum(total_cc) + sum(total_apl1) + sum(total_apl2)).replace('.', ',')
    escritor.writerow(('TOTAL GERAL', None, total_geral_cc, total_geral_apl1, total_geral_apl2, total_geral))
"""

arquivoBi = 'disponibilidade-bi.csv'
with open(arquivoBi, 'w', newline='') as arquivo_csv:
    escritor = csv.writer(arquivo_csv, delimiter=';')
    escritor.writerow(('DATA', 'PREFIXO', 'BANCO', 'CONTA', 'TIPO', 'SALDO'))
    #total = []

    for chave in biblioteca_saldos:
        conta = chave
        data = biblioteca_saldos[chave].get('data')
        prefixo = biblioteca_saldos[chave].get('prefixo')
        nome_banco = nome_bancos.get(biblioteca_saldos[chave].get('cod_banco'))

        saldo_cc = biblioteca_saldos[chave].get('saldo_cc')
        # verifica se há valor para validar se foi importado ou não
        if saldo_cc is not None:
            # Convertendo valores para calcular o total
            cc = Decimal(saldo_cc.replace(',', '.'))
            #total.append(cc)
        else:
            saldo_cc = 'NÃO IMPORTADO'
            #cc = 0
            #total.append(cc)
        escritor.writerow((data, prefixo, nome_banco, conta, 'C/C', saldo_cc))

        apl_list = biblioteca_saldos[chave].get('apls')
        # verifica se há valor para validar se foi importado ou não
        if apl_list is not None:
            for idx, saldo_apl in apl_list.items():
                tipo_apl = tipos_apls.get(idx)
                if saldo_apl is not None:
                    apl = Decimal(saldo_apl.replace(',', '.'))
                    #total.append(apl)
                else:
                    saldo_apl = 'NÃO IMPORTADO'
                    #apl = 0
                    #total.append(apl)
                escritor.writerow((data, prefixo, nome_banco, conta, tipo_apl, saldo_apl))

    #total_geral = str(sum(total)).replace('.', ',')
    #escritor.writerow(('TOTAL GERAL', None, None, None, None, total_geral))
