from datetime import datetime
import disponibilidadefuncoes
from decimal import Decimal
import shutil
import csv
import os

str_data_forma = '%d/%m/%Y'

# Data comparação
# data_hoje = datetime.strptime('19/02/2020', str_data_forma).date()
data_hoje = datetime.today()
print(f'Serão obtidos saldos com data menor que a data atual: {data_hoje.strftime(str_data_forma)}')

# Quantidade maxima de linhas a ler para o cabecalho, maior atual APL Bradesco
cabecalho_linhas = 19
# Bancos posições e contas
bancos = {'001': {'pst_linha_cc': 8, 'pst_data': 1, 'pst_saldo_cc': -2,
                  'cc_txt': True, 'apl_incluso': True, 'qt_linhas_busca_conta': 2,
                  'pst_linha_saldo_apl': 8, 'pst_saldo_apl': 1,
                  'contas': {'21397-7': {'apl': None},
                             '52500-6': {'apl': {'apl1': 'DIFERENCIA', 'apl2': 'Prefixado'}},
                             '52600-2': {'apl': {'apl1': 'DIFERENCIA'}},
                             '52901-X': {'apl': None},
                             '52903-6': {'apl': {'apl1': 'DIFERENCIA'}},
                             '52904-4': {'apl': {'apl1': 'DIFERENCIA', 'apl2': 'Prefixado'}},
                             '152600-6': {'apl': None},
                             '152700-2': {'apl': None},
                             '152800-9': {'apl': None},
                             '152900-5': {'apl': {'apl1': 'DIFERENCIA', 'apl2': 'Prefixado'}}
                             }
                  },
          '104': {'pst_linha_cc': 15, 'pst_data': 1, 'pst_saldo_cc': -2,
                  'cc_txt': True, 'apl_incluso': False, 'qt_linhas_busca_conta': 5,
                  'pst_linha_cc_apl': 7,
                  'pst_linha_saldo_apl': 100, 'pst_saldo_apl': 2,
                  'contas': {'1416-0': {'apl': {'apl1': 'MEGA'}},
                             '1417-9': {'apl': {'apl1': 'PREMIUM'}}
                             }
                  },
          '237': {'pst_linha_cc': 2, 'pst_data': 1, 'pst_saldo_cc': -1,
                  'cc_txt': True, 'apl_incluso': False, 'qt_linhas_busca_conta': 2,
                  'pst_linha_cc_apl': 19,
                  'pst_linha_saldo_apl': 10,  'pst_saldo_apl': 1,
                  'contas': {'29383-0': {'apl': {'apl1': 'Total'}},
                             '29384-9': {'apl': {'apl1': 'Total'}}
                             }
                  },
          '033': {'pst_linha_cc': 3, 'pst_data': 1, 'pst_saldo_cc': -1,
                  'cc_txt': True, 'apl_incluso': True, 'qt_linhas_busca_conta': 2,
                  'pst_linha_cc_apl': 11,
                  'pst_linha_saldo_apl': 24, 'pst_saldo_apl': 1,
                  'contas': {'13.002957.5': {'apl': {'apl1': 'tico', 'apl2': 'Fundo'}},
                             '13.002958.2': {'apl': {'apl1': 'tico', 'apl2': 'Fundo'}}
                             }
                  },
          '041': {'pst_linha_cc': 3, 'pst_data': 1, 'pst_saldo_cc': -1,
                  'cc_txt': True, 'apl_incluso': True, 'qt_linhas_busca_conta': 2,
                  'pst_linha_saldo_apl': 23, 'pst_saldo_apl': 1,
                  'contas': {'06.851005.0-6': {'apl': {'apl1': 'ATUAL......'}}
                             }
                  },
          '748': {'pst_linha_cc': 5, 'pst_data': 1, 'pst_saldo_cc': -1,
                  'cc_txt': True, 'apl_incluso': True, 'qt_linhas_busca_conta': 2,
                  'pst_linha_saldo_apl': 30, 'pst_saldo_apl': 1,
                  'contas': {'586188': {'apl': {'apl1': 'tico:'}}
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
for dados_banco in bancos.values():
    for conta in dados_banco['contas']:
        saldos = {'data': None, 'saldo_cc': None, 'apl1': None, 'apl2': None}
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

    if os.path.isfile(src + arquivo_txt) and arquivo_txt.split('.')[1].lower() in ['txt', 'csv']:
        with open(src + arquivo_txt) as arquivo:
            cabecalho = []
            for contador in range(0, cabecalho_linhas):
                ln_arquivo = arquivo.readline()
                cabecalho.append(ln_arquivo)

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

                # Recebendo os dados apartir da função
                saldos = disponibilidadefuncoes.saldos_conta(data_hoje, dados_arquivo, dados_banco, conta)

                # Guardando as informações no biblioteca de saldos
                biblioteca_saldos[conta] = saldos

                # Guardando nome do arquivo para depois move-lo para pasta de item processados
                arquivo_processado = arquivo_txt

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
            if saldos.get('apl1') is not None:
                saldo_apl_rename = saldos.get('apl1')
                saldo_apl_rename = saldo_apl_rename.replace(',', '_')

                rename_arquivo = f'{data_rename}_{conta}_CC({saldo_cc_rename})_APL({saldo_apl_rename}).txt'
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

                    # Recebendo os dados apartir da função
                    texto_apl = dados_banco.get('contas')[conta]['apl']
                    saldo_apl = disponibilidadefuncoes.obter_saldo_apl(dados_arquivo, dados_banco, texto_apl)

                    # Verificando saldos apls já guardados
                    if saldo_apl[0] is None and saldo_apl[1] is not None:
                        biblioteca_saldos[conta]['apl2'] = saldo_apl[1]
                        # Guardando Saldo APL na variavel que irá renomear arquivo
                        saldo_apl_rename = saldo_apl[1]

                    if saldo_apl[0] is not None:
                        biblioteca_saldos[conta]['apl1'] = saldo_apl[0]
                        # Guardando Saldo APL na variavel que irá renomear arquivo
                        saldo_apl_rename = saldo_apl[0]

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
