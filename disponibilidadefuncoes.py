from datetime import datetime, date

str_data_forma = '%d/%m/%Y'


def diminir_um_dia(data):
    data = data.toordinal()
    data = data - 1
    return date.fromordinal(data)


def valida_data(data):
    print(f'valida data: {data}')
    if len(data) != 10:
        return False
    if len(data) == 10:
        # if data[2] != '/' and data[5] != '/':
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
    else:
        dados = dados_linha.split(';')
        data = dados[dados_banco.get('pst_data') - 1].strip()
    return data


def converte_dados_lista(dados_linha):
    print(f'dados linha: {dados_linha}')
    dados_linha = dados_linha.strip()
    print(f'dados linha após strip(): {dados_linha}')
    dados_linha = dados_linha.replace(' ', ';')
    print(f'dados linha após replace: {dados_linha}')
    dados_linha = dados_linha.split(';')
    print(f'dados linha após split(;): {dados_linha}')
    return dados_linha


def obter_saldo_cc(dados_linha, dados_banco):
    # Caso caso arquivo tipo txt(cc_txt) do banco igual True, obtem dados atraves das posiçoes da linha
    # caso contrario separa campos pelo ; e obtem dados atraves do indice
    # depois remove espaços da direira e esquerda
    if dados_banco.get('cc_txt'):
        dados = converte_dados_lista(dados_linha)
        saldo_cc = dados[len(dados) - dados_banco.get('pst_saldo_cc')]
    else:
        dados = dados_linha.split(';')
        saldo_cc = dados[dados_banco.get('pst_saldo_cc') - 1]
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

    # Caso caso arquivo tipo txt(apl_txt) do banco igual True, obtem dados atraves das posiçoes da linha
    # caso contrario separa campos pelo ; e obtem dados atraves do indice
    # depois remove espaços da direira e esquerda

    else:
        dados = dados_arquivo[dados_banco.get('pst_linha_saldo_apl') - 1]
        dados = dados.split(';')
        saldo_apl = dados[dados_banco.get('pst_saldo_apl') - 1]
        # Caso saldo APL CEF esteja na linha abaixo da setada nos paramentros do banco
        if saldo_apl == 'SALDO':
            dados = dados_arquivo[dados_banco.get('pst_linha_saldo_apl')]
            dados = dados.split(';')
            saldo_apl = dados[dados_banco.get('pst_saldo_apl') - 1]
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
    # Sistema entra no laço while e percorre 10 linhas para tentar encontrar a palavra nas linhas acima.
    i = 0
    while palavra not in dados and i in range(qt_maxima) and (linha - 1 - i) > 0:
        dados = dados_arquivo[qt_linhas - linha - i]
        print(f'dados apl while {i}: {dados}')
        i += 1

    print(f'dados obtido pelo while: {dados}')
    dados = dados.strip()
    print(f'dados após strip(): {dados}')
    # Verifica se a palavra configurada no indice(texto_pst_vr_apl) do banco existe nos dados da linha
    if palavra in dados:
        dados = dados.replace(' ', ';')
        print(f'dados replace ; : {dados}')
        dados = dados.split(';')
        print(f'dados após split: {dados}')
        saldo_apl = dados[len(dados) - dados_banco.get('pst_saldo_apl')]
        print(saldo_apl)
        return saldo_apl
    # Caso não obtenha o saldo_apl retorna o valor 0
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
        # para tentar encontrar a palavra nas linhas abaixo.
        i = 0
        while palavra not in dados and i in range(qt_maxima) and (linha - 1 + i) < qt_linhas:
            dados = cabecalho[linha - 1 + i]
            print(f'dados while{i}: {dados}')
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
            print(f'Conta Teste: {conta_teste}')
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


"""
def verifica_conta_apl(bancos, cabecalho):
    tipo = 'SALDO_APL'
    return verifica_conta_cc(bancos, cabecalho, tipo)
    
    for chave in bancos.keys():
        if not bancos[chave].get('apl_incluso') or bancos[chave].get('qt_apl') == 2:
            # print(f'Chave: {chave}')
            # Caso campo pst 'pst_linha_cc_apl' = None, não executa as linhas abaixo
            if bancos[chave].get('pst_linha_cc_apl') is not None:
                dados = cabecalho[bancos[chave].get('pst_linha_cc_apl') - 1]
                conta = dados[bancos[chave].get('pst_cc_apl')[0] - 1: bancos[
                                                                          chave].get('pst_cc_apl')[1] - 1].strip()
                # print(f'Conta apl: {conta}')
                # Caso conta CEF esteja na linha abaixo da setada nos paramentros do banco
                if chave == '104' and conta not in bancos[chave].get('contas'):
                    dados = cabecalho[bancos[chave].get('pst_linha_cc_apl')]
                    conta = dados[bancos[chave].get('pst_cc_apl')[0] - 1: bancos[
                                                                              chave].get('pst_cc_apl')[1] - 1].strip()
                if conta in bancos[chave].get('contas'):
                    return True, bancos[chave], conta, chave
    return False,"""


def saldos_conta(data_hoje, dados_arquivo, dados_banco):
    saldos = {}
    idx = len(dados_arquivo) - 1
    while idx >= 0:
        # Obtendo dados da linha
        dados_linha = dados_arquivo[idx]
        # Obtendo data apartir da função
        data_linha = obter_data(dados_linha, dados_banco)
        # Validando se string recebida é uma data, caso seja data será convertida em tipo date
        if valida_data(data_linha):
            data_linha = datetime.strptime(data_linha, str_data_forma).date()
            if data_linha.toordinal() < data_hoje.toordinal():
                # convertendo str data para tipo date
                # dt = datetime.strptime(dt, str_data_forma).date() # desabilitado para manter em str
                # obtendo saldos cc
                saldo_cc = obter_saldo_cc(dados_arquivo[idx], dados_banco)

                # Testa se dados do banco informa que arquivo tambem tem dados de aplicação
                # Caso positivo obtem saldos de aplicação
                if dados_banco.get('apl_incluso'):
                    saldo_apl = obter_saldo_apl(dados_arquivo, dados_banco)
                else:
                    saldo_apl = '0'

                # Convertendo data p/ str
                data_linha = data_linha.strftime(str_data_forma)

                # Guardando as informações no biblioteca de saldos
                saldos = {'data': data_linha, 'saldo_cc': saldo_cc, 'saldo_apl': saldo_apl}
                break
        idx -= 1
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
