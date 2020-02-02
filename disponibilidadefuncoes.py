from datetime import datetime, date

str_data_forma = '%d/%m/%Y'


def diminir_um_dia(data):
    data = data.toordinal()
    data = data - 1
    return date.fromordinal(data)


def valida_data(data):
    # print(f'valida data: {data}')
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
    # Caso caso arquivo tipo txt(cc_txt) do banco igual True, obtem dados atraves das posiçoes da linha
    # caso contrario separa campos pelo ; e obtem dados atraves do indice
    # depois remove espaços da direira e esquerda
    if dados_banco.get('cc_txt'):
        data = dados_linha[dados_banco.get('pst_data')[0] - 1: dados_banco.get('pst_data')[1] - 1].strip()
    """
    else:
        dados = dados_linha.split(';')
        data = dados[dados_banco.get('pst_data') - 1].strip()"""
    return data


def converte_dados_lista(dados_linha):
    dados_linha = dados_linha.strip()
    dados_linha = dados_linha.replace(' ', ';')
    dados_linha = dados_linha.split(';')
    return dados_linha


def obter_saldo_cc(dados_linha, dados_banco):
    # Caso caso arquivo tipo txt(cc_txt) do banco igual True, converte os dados atraves da função seprando
    # os campos por ; e obtem dados atraves do indice configurado no banco sendo do final para o inicio,
    # depois remove caracteres indesejados e espaços da direira e esquerda
    if dados_banco.get('cc_txt'):
        dados = converte_dados_lista(dados_linha)
        print(f'Linha Saldo Conta Corrente obtida após conversão: {dados}')
        saldo_cc = dados[len(dados) - dados_banco.get('pst_saldo_cc')]
        print(f'Saldo Conta Corrente: {saldo_cc}')
    saldo_cc = saldo_cc.replace('C', '')
    saldo_cc = saldo_cc.replace('D', '')
    saldo_cc = saldo_cc.replace('.', '')
    saldo_cc = saldo_cc.replace('-', '')
    saldo_cc = saldo_cc.strip()
    return saldo_cc


def obter_saldo_apl(dados_arquivo, dados_banco):
    # Buscar linha de saldo apl pelos parametros configurados no banco
    if dados_banco.get('apl_busca'):
        texto_busca = dados_banco.get('texto_pst_vr_apl1')
        saldo_apl = apl_busca_linha_saldo(dados_arquivo, dados_banco, texto_busca)
        if dados_banco.get('qt_apl') == 2:
            texto_busca = dados_banco.get('texto_pst_vr_apl2')
            saldo_apl2 = apl_busca_linha_saldo(dados_arquivo, dados_banco, texto_busca)
            saldo_apl = soma_saldos_apl([saldo_apl, saldo_apl2])
        # Caso Não obtenha saldo da apl pelo texto 'texto_pst_vr_apl1' e não tenha 2 aplicações
        if saldo_apl == 0:
            texto_busca = dados_banco.get('texto_pst_vr_apl2')
            saldo_apl = apl_busca_linha_saldo(dados_arquivo, dados_banco, texto_busca)

    # Remove Caracteres indesejados e espaços da direira e esquerda
    if saldo_apl != '0':
        saldo_apl = saldo_apl.replace('C', '')
        saldo_apl = saldo_apl.replace('D', '')
        saldo_apl = saldo_apl.replace('.', '')
        saldo_apl = saldo_apl.replace('-', '')
        saldo_apl = saldo_apl.strip()
    return saldo_apl


def apl_busca_linha_saldo(dados_arquivo, dados_banco, texto_busca):
    qt_linhas = len(dados_arquivo)
    palavra = texto_busca
    linha = dados_banco.get('pst_linha_saldo_apl')
    qt_maxima = dados_banco.get('qt_linhas_busca_saldo_apl')
    dados = dados_arquivo[qt_linhas - linha]
    # Caso a palavra configurada no indice(texto_pst_vr_apl) do banco não exista nos dados da linha,
    # Sistema entra no laço while e percorre "qt_linhas_busca_saldo_apl" linhas configuradas no banco
    # para tentar encontrar a palavra nas linhas acima ao ponto inicial, "pst_linha_saldo_apl", configurado no banco.
    i = 0
    while palavra not in dados and i in range(qt_maxima) and (qt_linhas - linha - i) >= 0:
        dados = dados_arquivo[qt_linhas - linha - i]
        i += 1

    # Confirma se a palavra configurada no indice(texto_pst_vr_apl) do banco existe nos dados da linha
    if palavra in dados:
        dados = converte_dados_lista(dados)
        print(f'Linha aplicação obtida após conversão: {dados}')
        saldo_apl = dados[len(dados) - dados_banco.get('pst_saldo_apl')]
        print(f'Saldo aplicação: {saldo_apl}')
        return saldo_apl
    # Caso não obtenha o saldo_apl retorna o valor '0'
    else:
        saldo_apl = '0'
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
            # print(f'dados while{i}: {dados}')
            i += 1

        if palavra in dados:
            conta = texto_busca
            print(f'Conta obtida: {conta}')
            return conta
        # Caso não obtenha a conta retorna o valor Nao Identificada
        else:
            return 'Nao Identificada'
    return 'Nao Identificada'


def verifica_conta_cc(bancos, cabecalho, tipo):
    for chave, dados_banco in bancos.items():
        for conta_teste in dados_banco.get('contas'):
            texto_busca = conta_teste
            # print(f'Conta Teste: {conta_teste}')
            # print(f'Chave banco: {chave}')
            conta = busca_linha_conta(cabecalho, dados_banco, texto_busca, tipo)

            # Como não está padronizado a exibição das contas nos extratos de conta corrente e aplicação
            # do banco Santander sistema substitui o ponto por traço e fará um novo teste atendendo as
            # condicões do proximo if e depois retornará ao valor original da conta cadastrada
            if conta == 'Nao Identificada' and chave == '033':
                texto_busca = conta_teste.replace('.', '-')
                conta = busca_linha_conta(cabecalho, dados_banco, texto_busca, tipo)
                if conta != 'Nao Identificada':
                    conta = conta.replace('-', '.')

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


def saldos_conta(data_hoje, dados_arquivo, dados_banco):
    idx = len(dados_arquivo) - 1
    # Caso seja banco Banrisul, busca mes e ano a partir da função
    if dados_banco.get('contas')[0] == '06.851005.0-6':
        complemento_data = mes_ano_banrisul(dados_arquivo)
    while idx >= 0:
        # Obtendo dados da linha
        dados_linha = dados_arquivo[idx]
        # Obtendo data apartir da função
        data_linha = obter_data(dados_linha, dados_banco)
        # Caso seja banco Banrisul, complementa dia recebido com complemento de mes e ano
        if dados_banco.get('contas')[0] == '06.851005.0-6':
            try:
                # Tentando converter em inteiro para testar dia no formato valido
                data_linha = int(data_linha)
                # Convertendo novamente em string e adicionando 0 a esquerda para completar 2 digitos
                data_linha = (str(data_linha)).zfill(2)
            except ValueError:
                data_linha = '0'
            data_linha = data_linha + complemento_data
            # print(f'data completa banrisul: {data_linha}')

        # Caso seja banco banrisul procura data inferior a data do sistema para pegar o saldo CC
        # Se linha de busca ultrapassar dados MOVIMENTOS DA CONTA CORRENTE buscará saldo pelo caso abaixo
        if dados_banco.get('contas')[0] == '06.851005.0-6' and ('MOVIMENTOS DA CONTA CORRENTE' in dados_arquivo[idx]):
            i = 0
            while 'SALDO ANT EM' not in dados_arquivo[idx + i] and idx + i < len(dados_arquivo):
                i += 1
            dados = converte_dados_lista(dados_arquivo[idx + i])
            # Obtendo data de forma personalizada para condição e banco em especifico
            data_linha = dados[3]
            # Validando se string recebida é uma data, caso seja data será convertida em tipo date
            if valida_data(data_linha):
                data_linha = datetime.strptime(data_linha, str_data_forma).date()
                if data_linha.toordinal() < data_hoje.toordinal():
                    # obtendo saldos cc
                    saldo_cc = dados[len(dados) - 1]
                    # print(f'Saldo Conta Corrente: {saldo_cc}')
                    # interrompendo busca while
                    break
        # Validando se string recebida é uma data, caso seja data será convertida em tipo date
        elif valida_data(data_linha):
            data_linha = datetime.strptime(data_linha, str_data_forma).date()
            if data_linha.toordinal() < data_hoje.toordinal():
                # Caso seja banco banrisul procura data inferior a data do sistema para pegar o saldo CC
                # A linha do saldo conta corrente obedece a personalização abaixo
                if dados_banco.get('contas')[0] == '06.851005.0-6':
                    i = 0
                    while 'SALDO NA DATA' not in dados_arquivo[idx + i] and idx + i < len(dados_arquivo):
                        i += 1
                    dados = dados_arquivo[idx + i]
                    # obtendo saldos cc
                    saldo_cc = obter_saldo_cc(dados, dados_banco)
                    break
                # Caso qualquer outro banco obtem o Saldo CC de maneira padrão
                else:
                    # obtendo saldos cc
                    saldo_cc = obter_saldo_cc(dados_arquivo[idx], dados_banco)
                    break
        idx -= 1
    # Testa se dados do banco informa que arquivo tambem tem dados de aplicação
    # Caso positivo obtem saldos de aplicação
    if dados_banco.get('apl_incluso'):
        saldo_apl = obter_saldo_apl(dados_arquivo, dados_banco)
    else:
        saldo_apl = '0'

    try:
        # Convertendo data p/ str
        data_linha = data_linha.strftime(str_data_forma)
    except AttributeError:
        data_hoje = data_hoje.strftime(str_data_forma)
        data_linha = f'Não Localizado data valida anterior a hoje({data_hoje})'
        saldo_cc = f'Verificar arquivo atualizado dessa conta'

    # Guardando as informações no biblioteca de saldos
    saldos = {'data': data_linha, 'saldo_cc': saldo_cc, 'saldo_apl': saldo_apl}

    return saldos


def soma_saldos_apl(saldos):
    valores = []
    for saldo_apl in saldos:
        saldo_apl = saldo_apl.replace('.', '')
        saldo_apl = float(saldo_apl.replace(',', '.'))
        valores.append(saldo_apl)
    saldo_apl = sum(valores)
    saldo_apl = str(saldo_apl).replace('.', ',')
    return saldo_apl
