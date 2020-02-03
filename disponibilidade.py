from datetime import datetime, date
import disponibilidadefuncoes
import shutil
import csv
import os

str_data_forma = '%d/%m/%Y'

# Data comparação
# data_hoje = datetime.strptime('29/01/2020', str_data_forma).date()
data_hoje = datetime.today()
print(f'Serão obtidos saldos com data menor que a data atual: {data_hoje.strftime(str_data_forma)}')

# Quantidade maxima de linhas a ler para o cabecalho, maior atual APL Bradesco
cabecalho_linhas = 19
# Bancos posições e contas
bancos = {'001': {'pst_linha_cc': 8, 'pst_cc': [31, 39], 'pst_data': [4, 14], 'pst_saldo_cc': 2,
                  'cc_txt': True, 'apl_txt': True, 'apl_incluso': True, 'qt_linhas_busca_conta': 2,
                  'qt_apl': 2, 'apl_busca': True, 'texto_pst_vr_apl1': 'DIFERENCIA', 'texto_pst_vr_apl2': 'Prefixado',
                  'pst_linha_saldo_apl': 8, 'pst_saldo_apl': 1, 'qt_linhas_busca_saldo_apl': 8,
                  'contas': ['21397-7', '52500-6', '52600-2', '52901-X', '52903-6', '52904-4',
                             '152600-6', '152700-2', '152800-9', '152900-5']},
          '104': {'pst_linha_cc': 15, 'pst_cc': [30, 36], 'pst_data': [5, 15], 'pst_saldo_cc': 2,
                  'cc_txt': True, 'apl_txt': False, 'apl_incluso': False, 'qt_linhas_busca_conta': 5,
                  'qt_apl': 2, 'apl_busca': True, 'texto_pst_vr_apl1': 'PREMIUM', 'texto_pst_vr_apl2': 'REFDI',
                  'pst_linha_cc_apl': 7, 'pst_cc_apl': [69, 75],
                  'pst_linha_saldo_apl': 119, 'pst_saldo_apl': 2, 'qt_linhas_busca_saldo_apl': 20,
                  'contas': ['1416-0', '1417-9']},
          '237': {'pst_linha_cc': 2, 'pst_cc': [73, 80], 'pst_data': [1, 11], 'pst_saldo_cc': 1,
                  'cc_txt': True, 'apl_txt': True, 'apl_incluso': False, 'qt_linhas_busca_conta': 2,
                  'qt_apl': 1, 'apl_busca': True, 'texto_pst_vr_apl1': 'Total',
                  'pst_linha_cc_apl': 19, 'pst_cc_apl': [27, 34],
                  'pst_linha_saldo_apl': 10,  'pst_saldo_apl': 1, 'qt_linhas_busca_saldo_apl': 5,
                  'contas': ['29383-0', '29384-9']},
          '033': {'pst_linha_cc': 3, 'pst_cc': [125, 137], 'pst_data': [4, 14], 'pst_saldo_cc': 1,
                  'cc_txt': True, 'apl_txt': True, 'apl_incluso': True, 'qt_linhas_busca_conta': 2,
                  'qt_apl': 2, 'apl_busca': True, 'texto_pst_vr_apl1': 'tico', 'texto_pst_vr_apl2': 'Fundo',
                  'pst_linha_cc_apl': 11, 'pst_cc_apl': [123, 135],
                  'pst_linha_saldo_apl': 24, 'pst_saldo_apl': 1, 'qt_linhas_busca_saldo_apl': 9,
                  'contas': ['13.002957.5', '13.002958.2']},
          '041': {'pst_linha_cc': 3, 'pst_cc': [10, 23], 'pst_data': [1, 3], 'pst_saldo_cc': 1,
                  'cc_txt': True, 'apl_txt': True, 'apl_incluso': True, 'qt_linhas_busca_conta': 2,
                  'qt_apl': 1, 'apl_busca': True, 'texto_pst_vr_apl1': 'ATUAL......',
                  'pst_linha_saldo_apl': 23, 'pst_saldo_apl': 1, 'qt_linhas_busca_saldo_apl': 50,
                  'contas': ['06.851005.0-6']}
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
# print(lista_de_arquivos)

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

            """
            for idx, item in enumerate(cabecalho):
                print(f'{idx} - {item}')  """

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
                saldos = disponibilidadefuncoes.saldos_conta(data_hoje, dados_arquivo, dados_banco)

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
            saldo_cc_rename = saldos.get('saldo_cc')
            saldo_cc_rename = saldo_cc_rename.replace(',', '_')
            saldo_apl_rename = saldos.get('saldo_apl')
            saldo_apl_rename = saldo_apl_rename.replace(',', '_')
            rename_arquivo = f'{data_rename}_{conta}_CC({saldo_cc_rename})_APL({saldo_apl_rename}).txt'

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

                # lista temporaria p/ receber linhas do arquivo lido
                dados_arquivo = []

                # colocando cursor no inicio do arquivo
                arquivo.seek(0)
                dados_arquivo = arquivo.readlines()

                """ # impressao de teste
                for idx, item in enumerate(dados_arquivo):
                    print(f'{idx}{item}') """

                # Recebendo os dados apartir da função
                saldo_apl_atualizado = disponibilidadefuncoes.obter_saldo_apl(dados_arquivo, dados_banco)

                # Guardando Saldo APL na variavel que irá renomear arquivo
                saldo_apl_rename = saldo_apl_atualizado

                # Obtendo saldo apl já guardado e somando saldo_apl recebido da função
                if conta in biblioteca_saldos:
                    saldo_apl_atualizado = float(saldo_apl_atualizado.replace(',', '.'))
                    if biblioteca_saldos[conta].get('saldo_apl') is not None:
                        saldo_apl_anterior = float(biblioteca_saldos[conta].get('saldo_apl').replace(',', '.'))
                    else:
                        saldo_apl_anterior = 0
                    saldo_apl_atualizado += saldo_apl_anterior
                    saldo_apl_atualizado = str(saldo_apl_atualizado).replace('.', ',')
                    # Guardando as informações no biblioteca de saldos
                    biblioteca_saldos[conta]['saldo_apl'] = saldo_apl_atualizado
                else:
                    # Guardando as informações no biblioteca de saldos
                    biblioteca_saldos[conta] = {'saldo_apl': saldo_apl_atualizado}

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

# print(biblioteca_saldos)

arquivo = 'receita/disponibilidade.csv'
with open(arquivo, 'w', newline='') as arquivo_csv:
    escritor = csv.writer(arquivo_csv, delimiter=';')
    escritor.writerow(('CONTA', 'DATA', 'SALDO CC', 'SALDO APL'))
    for chave in biblioteca_saldos:
        conta = chave
        data = biblioteca_saldos[chave].get('data')
        saldo_cc = biblioteca_saldos[chave].get('saldo_cc')
        saldo_apl = biblioteca_saldos[chave].get('saldo_apl')
        item = (conta, data, saldo_cc, saldo_apl)
        escritor.writerow(item)
