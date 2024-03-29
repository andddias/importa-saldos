from datetime import datetime, date, timedelta
from decimal import Decimal

str_data_forma = '%d/%m/%Y'


def diminir_um_dia(data):
    data = data.toordinal()
    data = data - 1
    return date.fromordinal(data)


def valida_data(data):
    if len(data) != 10:
        return False
    if len(data) == 10:
        if data[2] == '/' and data[5] == '/':
            dia = int(data[0:2])
            mes = int(data[3:5])
            ano = int(data[6:10])

            valida = False

            # Meses com 31 dias
            if mes == 1 or mes == 3 or mes == 5 or mes == 7 or mes == 8 or mes == 10 or mes == 12:
                if dia <= 31:
                    valida = True
            # Meses com 30 dias
            elif mes == 4 or mes == 6 or mes == 9 or mes == 11:
                if dia <= 30:
                    valida = True
            # Mes Fevereiro
            elif mes == 2:
                # Testa se é bissexto
                if ((ano % 4) == 0 and (ano % 100) != 0) or (ano % 400) == 0:
                    if dia <= 29:
                        valida = True
                elif dia <= 28:
                    valida = True
            return valida
    return False


def obter_data(dados_linha, dados_banco):
    # Caso cadastro do banco esteja configurado no campo 'cc_txt' igual True, converte os dados atraves da função
    # separando os campos por ; e obtem dados atraves do indice configurado no banco,
    # depois remove caracteres indesejados e espaços da direira e esquerda
    if dados_banco.get('cc_txt'):
        dados_linha = converte_dados_lista(dados_linha)
        try:
            data = dados_linha[dados_banco.get('pst_data') - 1]
        except IndexError:
            # preenchido com data invalida p/ falhar na validação da data
            data = '-----------'
    return data


def converte_dados_lista(dados_linha):
    dados_linha = dados_linha.strip()
    dados_linha = dados_linha.split(' ')
    if '' in dados_linha:
        dados_linha = exclui_itens_vazio_lista(dados_linha)
    return dados_linha


def exclui_itens_vazio_lista(dados_linha):
    while '' in dados_linha:
        dados_linha.remove('')
    return dados_linha


def obter_saldo_cc(dados_linha, dados_banco):
    # Caso cadastro do banco esteja configurado no campo 'cc_txt' igual True, converte os dados atraves da função
    # separando os campos por ; e obtem dados atraves do indice configurado no banco,
    # depois remove caracteres indesejados e espaços da direira e esquerda
    if dados_banco.get('cc_txt'):
        dados = converte_dados_lista(dados_linha)
        saldo_cc = dados[dados_banco.get('pst_saldo_cc')]
    saldo_cc = tratar_valor(saldo_cc)
    return saldo_cc


def montar_nome_arquivo(apl_list):
    saldo_apl_rename = ''
    i = len(apl_list)
    for saldo_apl in apl_list.values():
        if saldo_apl is not None:
            saldo_apl_rename += saldo_apl
            if i > 1:
                saldo_apl_rename += '-'
        i -= 1
    return saldo_apl_rename.replace(',', '_')


def obter_saldo_lista_apl(dados_arquivo, dados_banco, apl_list):
    if apl_list is not None:
        for nome_apl, saldo_apl in apl_list.items():
            if saldo_apl is None:
                apl_list[nome_apl] = obter_saldo_apl(dados_arquivo, dados_banco, nome_apl)
    return apl_list


def obter_saldo_apl(dados_arquivo, dados_banco, texto_apl):
    saldo_apl = apl_busca_linha_saldo(dados_arquivo, dados_banco, texto_apl)
    if saldo_apl is not None:
        saldo_apl = tratar_valor(saldo_apl)

    return saldo_apl


def tratar_valor(valor):
    valor = valor.replace('C', '')
    valor = valor.replace('D', '')
    valor = valor.replace('.', '')
    valor = valor.replace('-', '')
    valor = valor.strip()
    if valor == '':
        valor = None
    return valor


def apl_busca_linha_saldo(dados_arquivo, dados_banco, texto_busca):
    qt_linhas = len(dados_arquivo)
    palavra = texto_busca
    linha = dados_banco.get('pst_linha_saldo_apl')
    dados = dados_arquivo[qt_linhas - linha]
    # Caso a palavra configurada no indice(texto_pst_vr_apl) do banco não exista nos dados da linha,
    # Sistema entra no laço while e percorre linhas até o limite de linhas do arquivo ou até encontrar
    # a palavra nas linhas acima ao ponto inicial, "pst_linha_saldo_apl", configurado no banco.
    i = 0
    while palavra not in dados and (qt_linhas - linha - i) >= 0:
        dados = dados_arquivo[qt_linhas - linha - i]
        i += 1

    # Confirma se a palavra configurada no indice(texto_pst_vr_apl) do banco existe nos dados da linha
    if palavra in dados:
        dados = converte_dados_lista(dados)
        saldo_apl = dados[len(dados) - dados_banco.get('pst_saldo_apl')]
        return saldo_apl
    # Caso não obtenha o saldo_apl retorna o valor None
    else:
        saldo_apl = None
        return saldo_apl


def busca_linha_conta(cabecalho, dados_banco, texto_busca, tipo):
    qt_linhas = len(cabecalho)
    palavra = texto_busca
    # Caso a busca seja com os parametros Saldos da conta corrente
    if tipo == 'SALDO_CC':
        linha = dados_banco.get('pst_linha_cc')
        qt_maxima = dados_banco.get('qt_linhas_busca_conta')
        dados = cabecalho[linha - 1]
    # Caso a busca seja com os parametros Saldos de Aplicação da conta corrente
    # e dados_banco.get('pst_linha_cc_apl') não seja None
    elif tipo == 'SALDO_APL' and dados_banco.get('pst_linha_cc_apl') is not None:
        linha = dados_banco.get('pst_linha_cc_apl')
        qt_maxima = dados_banco.get('qt_linhas_busca_conta')
        dados = cabecalho[linha - 1]
    else:
        dados = None

    # Verifica se a variavel dados foi inicializada
    if dados is not None:
        # Caso a palavra configurada no indice(contas) do banco não exista nos dados da linha,
        # Sistema entra no laço while e percorre x(qt_linhas_busca_conta) configurada no banco
        # para tentar encontrar a palavra nas linhas abaixo ao ponto inicial configurado no banco.
        i = 0
        while palavra not in dados and i in range(qt_maxima) and (linha - 1 + i) < qt_linhas:
            dados = cabecalho[linha - 1 + i]
            i += 1

        if palavra in dados:
            conta = texto_busca
            return conta
        # Caso não obtenha a conta retorna o valor Nao Identificada
        else:
            return 'Nao Identificada'
    return 'Nao Identificada'


def verifica_conta_cc(bancos, cabecalho, tipo):
    for chave, dados_banco in bancos.items():
        for conta_teste in dados_banco.get('contas'):
            texto_busca = conta_teste
            conta = busca_linha_conta(cabecalho, dados_banco, texto_busca, tipo)

            # Como não está padronizado a exibição das contas nos extratos de conta corrente e aplicação
            # do banco Santander sistema substitui o ponto por traço e fará um novo teste atendendo as
            # condicões do proximo if e depois retornará ao valor original da conta cadastrada
            if conta == 'Nao Identificada' and chave == '033':
                texto_busca = conta_teste.replace('.', '-')
                conta = busca_linha_conta(cabecalho, dados_banco, texto_busca, tipo)
                if conta != 'Nao Identificada':
                    conta = conta_teste
            # segundo opção de teste caso seja banco santander
            if conta == 'Nao Identificada' and chave == '033':
                texto_busca = conta_teste.replace('.', '')
                conta = busca_linha_conta(cabecalho, dados_banco, texto_busca, tipo)
                if conta != 'Nao Identificada':
                    conta = conta_teste

            # Como não está padronizado a exibição das contas nos extratos de conta corrente e aplicação
            # do banco SICREDI sistema substitui o TRAÇO por NADA e fará um novo teste atendendo as
            # condicões do proximo if e depois retornará ao valor original da conta cadastrada
            if conta == 'Nao Identificada' and chave == '748':
                texto_busca = conta_teste.replace('-', '')
                conta = busca_linha_conta(cabecalho, dados_banco, texto_busca, tipo)
                if conta != 'Nao Identificada':
                    conta = conta_teste

            # segundo opção de teste caso seja banco Sicredi
            if conta == 'Nao Identificada' and chave == '748':
                texto_busca = 'procura'
                conta = busca_linha_conta(cabecalho, dados_banco, texto_busca, tipo)
                if conta != 'Nao Identificada':
                    conta = conta_teste

            # Busca APL CEF quando não existe informações da conta no arquivo buscará pelo nome da APL
            if conta == 'Nao Identificada' and chave == '104':
                texto_busca = dados_banco.get('contas')[conta_teste]['apl']['apl1']
                conta = busca_linha_conta(cabecalho, dados_banco, texto_busca, tipo)
                if conta != 'Nao Identificada':
                    conta = conta_teste

            if conta != 'Nao Identificada':
                return True, dados_banco, conta,
    return False,


def mes_ano_banrisul(dados_arquivo):
    idx = len(dados_arquivo) - 5
    while idx >= 0:
        dados_linha = dados_arquivo[idx]
        # O texto 'EXTRATO EMITIDO' é o localizador da linha onde é possivel identificar a data completa
        if 'EXTRATO EMITIDO' in dados_linha:
            complemento_data = dados_linha[51:59]
            return complemento_data
        idx -= 1
    # Caso não encontre retorna um valor invalido para falhar na validação da data
    return '/00/0000'


def ano_safra(dados_arquivo):
    idx = len(dados_arquivo) - 55
    while idx >= 0:
        dados_linha = dados_arquivo[idx]
        # O texto 'odo de' é o localizador da linha onde é possivel identificar a data completa
        if 'odo de' in dados_linha:
            complemento_data = dados_linha[29:34]
            return complemento_data
        idx -= 1
    # Caso não encontre retorna um valor invalido para falhar na validação da data
    return '/0000'


def saldos_conta(data_hoje, dados_arquivo, dados_banco, conta, apl_list):
    # Variavel para guardar dia anterior p/ comparação dia extrato banco Banrisul
    dia_anterior = None

    idx = len(dados_arquivo) - 1
    # Caso seja banco Banrisul, busca mes e ano a partir da função
    if conta == '06.851005.0-6':
        complemento_data = mes_ano_banrisul(dados_arquivo)

    # Caso seja banco Safra, busca ano a partir da função
    if conta == '23066-3':
        complemento_data = ano_safra(dados_arquivo)

    if dados_banco.get('extrato_invertido'):
        inversor = -1
    else:
        inversor = 1

    while idx >= 0:
        # Obtendo dados da linha
        dados_linha = dados_arquivo[inversor * idx]
        # Obtendo data apartir da função
        data_linha = obter_data(dados_linha, dados_banco)
        # Caso seja banco Banrisul, complementa dia recebido com complemento de mes e ano
        if conta == '06.851005.0-6':
            try:
                # Tentando converter em inteiro para testar dia no formato valido
                data_linha = int(data_linha)
                if dia_anterior is None:
                    dia_anterior = data_linha
                elif dia_anterior > data_linha:
                    dia_anterior = data_linha
                # Virada de mês Banrisul, ajustando complemento data
                else:
                    # Acrescentando primeiro dia ao complemento da data
                    data_str = '01' + complemento_data
                    # Convertendo data srt para tipo Date
                    data = datetime.strptime(data_str, str_data_forma).date()
                    # Diminuindo um dia para alterar o mes e ano(quando for o caso)
                    data = diminir_um_dia(data)
                    # Convertendo data tipo Date para str
                    data_str = data.strftime(str_data_forma)
                    # Ajustando complemento da data
                    complemento_data = data_str[2:10]
                # Convertendo novamente em string e adicionando 0 a esquerda para completar 2 digitos
                data_linha = (str(data_linha)).zfill(2)
            except ValueError:
                data_linha = '0'
            data_linha = data_linha + complemento_data

        if conta == '23066-3':
            try:
                # Tentando converter em inteiro para testar dia no formato valido
                int(data_linha[0:2])
                int(data_linha[3:5])
            except ValueError:
                data_linha = '0/00'
            data_linha = data_linha + complemento_data

        # Caso seja banco banrisul procura data inferior a data do sistema para pegar o saldo CC
        # Se linha de busca ultrapassar dados MOVIMENTOS DA CONTA CORRENTE buscará saldo pelo caso abaixo
        if conta == '06.851005.0-6' and (
                'MOVIMENTOS DA CONTA CORRENTE' in dados_arquivo[inversor * idx]):
            i = 0
            while 'SALDO ANT EM' not in dados_arquivo[inversor * idx + i] and inversor * idx + i < len(dados_arquivo):
                i += 1
            dados = converte_dados_lista(dados_arquivo[inversor * idx + i])
            # Obtendo data de forma personalizada para condição e banco em especifico
            data_linha = dados[3]
            # Validando se string recebida é uma data, caso seja data será convertida em tipo date
            if valida_data(data_linha):
                data_linha = datetime.strptime(data_linha, str_data_forma).date()
                if data_linha.toordinal() < data_hoje.toordinal():
                    # obtendo saldos cc
                    saldo_cc = tratar_valor(dados[dados_banco.get('pst_saldo_cc')])
                    # interrompendo busca while
                    break

        # Caso seja banco Santander procura Saldo Disponível em Conta Corrente para pegar o saldo CC
        # Se linha de busca ultrapassar dados Não há lançamentos desta conta corrente para o período solicitado.
        # buscará saldo pelo caso abaixo
        if conta == '13.002957.5' and (
                'amentos desta conta corrente para o per' in dados_arquivo[inversor * idx]):
            i = 0
            while 'vel em Conta Corrente' not in dados_arquivo[inversor * idx + i] \
                    and inversor * idx + i < len(dados_arquivo):
                i += 1
            dados = converte_dados_lista(dados_arquivo[inversor * idx + i])

            # Obtendo data de forma personalizada para condição e banco em especifico utilizando
            # a data de hoje -1 dia, pois nesse caso quando não há movimentacao não existe um data a buscar
            data_linha = data_hoje - timedelta(days=1)
            if data_linha.toordinal() < data_hoje.toordinal():
                # obtendo saldos cc
                saldo_cc = tratar_valor(dados[dados_banco.get('pst_saldo_cc')])
                # interrompendo busca while
                break

        # Validando se string recebida é uma data, caso seja data será convertida em tipo date
        elif valida_data(data_linha):
            data_linha = datetime.strptime(data_linha, str_data_forma).date()
            if data_linha.toordinal() < data_hoje.toordinal():
                # Caso seja banco banrisul procura data inferior a data do sistema para pegar o saldo CC
                # A linha do saldo conta corrente obedece a personalização abaixo
                if conta == '06.851005.0-6':
                    i = 0
                    while 'SALDO NA DATA' not in dados_arquivo[inversor * idx + i] \
                            and inversor * idx + i < len(dados_arquivo):
                        i += 1
                    dados = dados_arquivo[inversor * idx + i]
                    # obtendo saldos cc
                    saldo_cc = obter_saldo_cc(dados, dados_banco)
                    # interrompendo busca while
                    break
                # Caso qualquer outro banco obtem o Saldo CC de maneira padrão
                else:
                    # obtendo saldos cc
                    saldo_cc = obter_saldo_cc(dados_arquivo[inversor * idx], dados_banco)
                    # interrompendo busca while
                    break
        idx -= 1
    # Testa se dados do banco informa que arquivo tambem tem dados de aplicação
    # Caso positivo obtem saldos de aplicação
    if dados_banco.get('apl_incluso'):
        if apl_list is not None:
            apl_list = obter_saldo_lista_apl(dados_arquivo, dados_banco, apl_list)

    try:
        # Convertendo data p/ str
        data_linha = data_linha.strftime(str_data_forma)
    except AttributeError:
        data_hoje = data_hoje.strftime(str_data_forma)
        # retorna a data de realização do processo de obtenção de saldo
        data_linha = data_hoje
        # retorna None no saldo para indicar a pencia de importação
        saldo_cc = None

    # Guardando as informações no biblioteca de saldos
    saldos = {'data': data_linha, 'saldo_cc': saldo_cc, 'apl': apl_list}

    return saldos


def convert_ansi(file):
    try:
        s = open(file).read()
    except UnicodeDecodeError:
        s = open(file, mode='r', encoding='utf-8-sig').read()
        open(file, mode='w', encoding='ansi', errors="ignore").write(s)
