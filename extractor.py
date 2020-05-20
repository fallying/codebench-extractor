import keyword
import re
import tokenize
from datetime import datetime, timedelta

from radon.metrics import h_visit
from radon.raw import analyze
from radon.visitors import ComplexityVisitor

from parser import *
from util import Util


class CodebenchExtractor:
    """
    Classe Extratora das Entidades do dataset Codebench
    """

    # extensão dos arquivos de informações das 'Atividades' de uma 'Turma'
    __atividade_file_extension = '.data'
    # nome do arquivo de informações de 'Estudante'
    __estudante_file_name = 'user.data'
    # extensão do arquivo de log do CodeMirror
    __codemirror_file_extension = '.log'
    # extensão do arquivo de código-fonte das soluções dos 'Estudantes'
    __exercices_file_extension = '.py'
    # extensão do arquivo de código-fonte das soluções dos 'Professores
    __solution_extension = '.code'
    # limite do intervalo de tempo entre eventos de interação com o CodeMirror duranet a implementação de uma Solução
    # qualquer intervalo maior que o limite abaixo é considerado ociosidade
    __limite_ociosidade = timedelta(minutes=5)

    __module_token = {
        'import': True,
        'from': True
    }

    __type_token = {
        'bool': True,
        'bytes': True,
        'bytearray': True,
        'complex': True,
        'dict': True,
        'float': True,
        'set': True,
        'int': True,
        'list': True,
        'range': True,
        'object': True,
        'str': True,
        'memoryview': True,
        'None': True,
        'frozenset': True
    }

    __builtin_token = {
        'abs': True,
        'all': True,
        'any': True,
        'ascii': True,
        'bin': True,
        'bool': True,
        'breakpoint': True,
        'bytearray': True,
        'bytes': True,
        'callable': True,
        'chr': True,
        'classmethod': True,
        'compile': True,
        'complex': True,
        'delattr': True,
        'dict': True,
        'dir': True,
        'divmod': True,
        'enumerate': True,
        'eval': True,
        'exec': True,
        'filter': True,
        'float': True,
        'format': True,
        'frozenset': True,
        'getattr': True,
        'globals': True,
        'hasattr': True,
        'hash': True,
        'hex': True,
        'id': True,
        'input': True,
        'int': True,
        'isinstance': True,
        'issubclass': True,
        'iter': True,
        'len': True,
        'list': True,
        'locals': True,
        'map': True,
        'max': True,
        'min': True,
        'next': True,
        'object': True,
        'oct': True,
        'open': True,
        'ord': True,
        'pow': True,
        'print': True,
        'property': True,
        'range': True,
        'repr': True,
        'reversed': True,
        'round': True,
        'set': True,
        'setattr': True,
        'slice': True,
        'sorted': True,
        'staticmethod': True,
        'str': True,
        'sum': True,
        'super': True,
        'tuple': True,
        'type': True,
        'vars': True,
        'zip': True,
    }

    __loop_token = {
        'for': True,
        'while': True
    }

    __conditional_token = {
        'if': True,
        'elif': True,
        'else': True
    }

    __logical_op_token = {
        'and': True,
        'or': True,
        'not': True
    }

    @staticmethod
    def __is_import_token(t: tokenize.TokenInfo):
        if t.start[1] == 0:
            return CodebenchExtractor.__module_token.get(t.string, False)
        return False

    @staticmethod
    def extract_periodos(path: str) -> List[Periodo]:
        """
        Retorna uma lista de todos os :class:`Periodo` letivos encontrados no dataset Codebench.

        Cada Período corresponde a uma pasta dentro do diretório do dataset Codebench.

        Exemplo de uso:
            periodos = CodebenchExtractor.extract_periodos('cb_dataset_v1.11/')

            for periodo in periodos:
                print(periodo)
            ...

        :param path: Caminho absoluto para o diretório do dataset do Codebench.
        :type path: str
        """
        periodos = []
        # recupera todas as 'entradas' (arquivos ou pastas) no caminho informado (path).
        with os.scandir(path) as entries:
            for entry in entries:
                with os.scandir(entry.path) as folders:
                    for folder in folders:
                        Logger.info(f'Extraindo informações de Perído: {folder.name}')
                        p = Periodo(folder.name, folder.path)
                        periodos.append(p)
        return periodos

    @staticmethod
    def __extract_turma_descricao_from_file(path: str, turma: Turma):
        """
        Recupera a descrição da :class:`Turma`, a partir de um dos arquivo de :class:`Atividade` (assessments).
        A descrição da turma é então atribuída a propriedade 'descricao' da 'Turma'.

        ---- classe name: [descrição]

        :param path: Caminho absoluto para o diretório de atividades da Turma
        :type path: str
        :param turma: Objeto que irá armazenar a descrição da Turma.
        :type turma: Turma
        """
        # coleta todas os arquivos/pastas no diretório informado (diretório de atividades da turma)
        with os.scandir(path) as entries:
            for entry in entries:
                # se a 'entrada' for um arquivo de extensão '.data' então corresponde atividade
                if entry.is_file() and entry.path.endswith(CodebenchExtractor.__atividade_file_extension):
                    with open(entry.path, 'r') as f:
                        Logger.info(f'Extraindo descrição da Turma no arquivo: {entry.path}')
                        line = f.readline()
                        while line:
                            # ---- class name: Introdução à Programação de Computadores
                            if line.startswith('---- class name:'):
                                turma.descricao = line.strip()[17:]
                                break
                            line = f.readline()
                    break

    @staticmethod
    def extract_turmas(periodo: Periodo):
        """
        Retorna uma lista contendo todas as :class:`Turma` de um :class:`Período` letivo.

        Cada Turma corresponde a uma pasta dentro do diretório do Período:
            - '220': Turma 220
            - '221': Turma 221 ...

        As turmas encontradas são salvas no período (periodo.turma)

        Exemplo de uso:
            CodebenchExtractor.extract_turmas(periodo)

            for turma in periodo.turmas:
                print(turma)
            ...

        :param periodo: O Período letivo do qual devem ser recuperadas as Turmas.
        :type periodo: Periodo
        """
        # coleta todas os arquivos/pastas dentro do diretório do período.
        with os.scandir(periodo.path) as folders:
            for folder in folders:
                # se a 'entrada' for uma diretório (pasta) então corresponde a uma 'turma'
                if folder.is_dir():
                    Logger.info(f'Extraindo informações de Turma: {folder.name} {periodo.descricao}')
                    code = int(folder.name)
                    turma = Turma(periodo, code, folder.path)
                    CodebenchExtractor.__extract_turma_descricao_from_file(f'{folder.path}/assessments', turma)
                    periodo.turmas.append(turma)

    @staticmethod
    def __extract_atividade_info_from_file(path: str, atividade: Atividade):
        """
        Recupera as informações da :class:`Atividade` de um arquivo ('.data').

        As informações extraídas são salvas na 'atividade'.

        :param path: Caminho absoluto para o arquivo de dados da Atividade.
        :type path: str
        :param atividade: Objeto que irá armazenar as informações retiradas do arquivo.
        :type atividade: Atividade
        """
        with open(path, 'r') as f:
            Logger.info(f'Extraindo informações da Atividade no arquivo: {path}')
            for line in f.readlines():
                if line.startswith('---- as'):
                    atividade.titulo = line[23:].strip()
                elif line.startswith('---- st'):
                    atividade.data_inicio = line[12:].strip()
                elif line.startswith('---- en'):
                    atividade.data_termino = line[10:].strip()
                elif line.startswith('---- la'):
                    atividade.linguagem = line[15:].strip()
                elif line.startswith('---- ty'):
                    atividade.tipo = line[11:].strip()
                elif line.startswith('---- we'):
                    atividade.peso = float(line[13:].strip())
                elif line.startswith('---- to'):
                    atividade.n_blocos = int(line[22:].strip())
                elif line.startswith('---- ex'):
                    bloco = line[18:].strip()
                    if len(bloco) > 0:  # verifica se exite alguma questão, pois no dataset alguns dados estão faltando
                        # testa se realmente corresponde a um bloco de exercícios, blocos são separados por 'or'
                        if ' or ' in bloco:
                            # separa os códigos dos exercícios do bloco
                            bloco = bloco.split(' or ')
                            bloco = [int(x) for x in bloco]  # converte os códigos dos exercícios em inteiro
                            bloco.sort()
                        else:
                            bloco = int(bloco)
                        atividade.blocos.append(bloco)

    @staticmethod
    def extract_atividades(turma: Turma):
        """
        Recupera uma lista com todas as :class:`Atividade` realizadas numa dada :class:`Turma`.

        Cada turma possui informações sobre os estudantes e atividades.

        Cada atividade corresponde a um arquivo de extensão '.data'.

        Os arquivos das atividades estão localizadas dentro do diretório da turma, na pasta 'assessments'.

        As atividades encontradas são salvas na turma (turma.atividades)

        Exemplos de uso:
            CodebenchExtractor.extract_atividades(turma)

            for atividade in turma.atividades:
                print(atividade)
            ...

        :param turma: A Turma das Atividades.
        :type turma: Turma
        """
        # coleta todas os arquivos/pastas dentro do diretório de atividades da turma
        with os.scandir(f'{turma.path}/assessments') as arquivos:
            for arquivo in arquivos:
                # se a 'entrada' for um arquivo de extensão '.data', então corresponde a uma atividade.
                if arquivo.is_file() and arquivo.path.endswith(CodebenchExtractor.__atividade_file_extension):
                    Logger.info(f'Extraindo informações de Atividade: {arquivo.name}')
                    code = int(arquivo.path.split('/')[-1].replace(CodebenchExtractor.__atividade_file_extension, ''))
                    atividade = Atividade(turma, code, arquivo.path)
                    CodebenchExtractor.__extract_atividade_info_from_file(arquivo.path, atividade)
                    turma.atividades.append(atividade)

    @staticmethod
    def __extract_estudante_info_from_file(path: str, estudante: Estudante):
        """
        Extrai as informações referentes ao :class:`Estudante` do arquivo 'user.data'.

        As informações são salvas no objeto 'estudante' passado como parametro.

        :param path: Caminho absoluto do arquivo 'user.data' com as informações do Estudante.
        :type path: str
        :param estudante: Objeto que irá armazenar as informações retiradas do arquivo.
        :type estudante: Estudante
        """
        with open(path, 'r') as f:
            Logger.info(f'Extraindo informações do Estudante no arquivo: {path}')
            for index, line in enumerate(f.readlines(), start=0):
                line = line.strip()
                if line.startswith('---- cou') and index == 1:
                    estudante.curso_id = int(CodebenchExtractor.__get_property_value(line))
                elif line.startswith('---- cou') and index == 2:
                    estudante.curso_nome = CodebenchExtractor.__get_property_value(line)
                elif line.startswith('---- in') and index == 3:
                    estudante.instituicao_id = int(CodebenchExtractor.__get_property_value(line))
                elif line.startswith('---- in') and index == 4:
                    estudante.instituicao_nome = CodebenchExtractor.__get_property_value(line)
                elif line.startswith('---- hi'):
                    estudante.escola_nome = CodebenchExtractor.__get_property_value(line)
                elif line.startswith('---- sch'):
                    estudante.escola_tipo = CodebenchExtractor.__get_property_value(line)
                elif line.startswith('---- shi'):
                    estudante.escola_turno = CodebenchExtractor.__get_property_value(line)
                elif line.startswith('---- gr'):
                    estudante.escola_ano_grad = int(CodebenchExtractor.__get_property_value(line))
                elif line.startswith('---- sex'):
                    estudante.sexo = CodebenchExtractor.__get_property_value(line)
                elif line.startswith('---- year o'):
                    estudante.ano_nascimento = int(CodebenchExtractor.__get_property_value(line))
                elif line.startswith('---- civ'):
                    estudante.estado_civil = CodebenchExtractor.__get_property_value(line)
                elif line.startswith('---- hav'):
                    estudante.tem_filhos = True if CodebenchExtractor.__get_property_value(line) == 'yes' else False

    @staticmethod
    def __get_property_value(text: str):
        """
        Recebe uma linha de texto do arquivo de informações do estudante contendo uma chave e valor.

        Retorna somente o valor associado a aquela chave. Cada linha possui uma chave separada de seu valor por ':'.

        :param text: Linha de texto com a chave e valor.
        :type text: str
        :return: O valor encontrado na linha de texto ou 'None'.
        """
        idx = text.find(':')
        if idx >= 0:
            return text.strip()[idx + 2:]
        return None

    @staticmethod
    def extract_estudantes(turma: Turma):
        """
        Recupera uma lista com todos os :class:`Estudante` de uma :class:`Turma`.

        Cada turma possui informações sobre os estudantes e atividades.

        As informações dos estudantes estão localizadas dentros de pastas nomeadas com o código do estudante.

        Essas pastas estão localizadas dentro da pasta 'users' no diretório da turma.

        Os estudantes encontrados são salvos na turma (turma.estudantes)

        Exemplo de uso:
            CodebenchExtractor.extract_estudantes(turma)

            for estudante in turma.estudantes:
                print(estudante)
            ...

        :param turma: A Turma (disciplina) na qual os Estudantes estão matriculados.
        :type turma: Turma
        """
        # coleta todas os arquivos/pastas no diretório de 'estudantes' informado
        with os.scandir(f'{turma.path}/users') as folders:
            for folder in folders:
                # se a 'entrada' for um diretório, então corresponde a pasta de um 'estudante'.
                if folder.is_dir():
                    Logger.info(f'Extraindo informações do Estudante: {folder.name}')
                    estudante = Estudante(turma.periodo, turma, int(folder.name), folder.path)
                    CodebenchExtractor.__extract_estudante_info_from_file(
                        f'{folder.path}/{CodebenchExtractor.__estudante_file_name}', estudante)
                    turma.estudantes.append(estudante)

    @staticmethod
    def __extract_code_metrics(codigo: str):
        """
        Recupera as métricas de um código Python.

        McCabe's (Complexidade)
            - complexity: Complexidade Total
            - n_classes: Quantidade de Classes
            - n_functions: Quantidade de Funções
        Métricas Brutas (Código)
            - loc: Número Total de Linhas
            - lloc: Número de Linhas Lógicas de Código
            - sloc: Número de Linhas de Código
            - comments: Número de Comentários
            - single_comments: Número de Comentários Simples
            - multilines: Número de Multi-line Strings
            - blank_lines: Número de Linhas em Branco
        Halstead (Métricas de SW)
            - h1: Número de Operadores Distintos
            - h2: Número de Operandos Distintos
            - N1: Número Total de Operadores
            - N2: Número Total de Operandos
            - vocabulary: Vocabulário (h = h1 + h2)
            - length: Tamanho (N = N1 + N2)
            - calculated_length: Tamanho Calculado (h1 * log2(h1) + h2 * log2(h2))
            - volume: Volume (V = N * log2(h))
            - difficulty: Dificuldade (D = h1/2 * N2/h2)
            - effort: Esforço (E = D * V)
            - time: Tempo (T = E / 18 segundos)
            - bugs: Bugs (B = V / 3000), estivativa de erros na implementação

        :param codigo: String com o Código-Fonte.
        :type codigo: str
        :return: As métricas que puderam ser extraídas do código.
        """
        metricas = Metricas(None)
        v = ComplexityVisitor.from_code(codigo)
        metricas.complexity = v.complexity
        metricas.n_functions = len(v.functions)
        metricas.n_classes = len(v.functions)

        a = analyze(codigo)
        metricas.loc = a.loc
        metricas.lloc = a.lloc
        metricas.sloc = a.sloc
        metricas.blank_lines = a.blank
        metricas.multilines = a.multi
        metricas.comments = a.comments
        metricas.single_comments = a.single_comments

        h = h_visit(codigo)
        metricas.h1 = h.total.h1
        metricas.h2 = h.total.h2
        metricas.N1 = h.total.N1
        metricas.N2 = h.total.N2
        metricas.h = h.total.vocabulary
        metricas.N = h.total.length
        metricas.calculated_N = h.total.calculated_length
        metricas.volume = h.total.volume
        metricas.difficulty = h.total.difficulty
        metricas.effort = h.total.effort
        metricas.bugs = h.total.bugs
        metricas.time = h.total.time

        return metricas

    @staticmethod
    def __extract_solution_interval(path: str, execucao: Execucao):
        """
        Calcula os tempos de implementação e interação utilizando como limites os intervalos definidos na Atividade.

        O tempo de implementação é o tempo gasto pelo usuário enquanto o editor do CodeMirror estiver em foco, descontados os intervalos de inatividade.

        O tempo de interação é o tempo total gasto pelo usuário interagindo com o editor do CodeMirror.

        :param path: Caminho absoluto do arquivo de 'log' com as informações do CodeMirror.
        :type path: str
        :param execucao: Objeto que irá armazenar as informações obtidas do arquivo de 'log' do CodeMirror.
        :type execucao: Execucao
        """
        with open(path, 'r') as f:
            Logger.info(f'Calculando tempos des implementação e interação: {path}')
            # datas de inicio e termino da atividade, servem como limites para o calculo do tempo e solução
            atividade_data_inicio = datetime.strptime(execucao.atividade.data_inicio, '%Y-%m-%d %H:%M')
            atividade_data_fim = datetime.strptime(execucao.atividade.data_termino, '%Y-%m-%d %H:%M')

            # algumas turmas são dividas durante os exames, por isso aumento o intervalo de tempo
            if execucao.atividade.tipo == 'exam':
                atividade_data_inicio -= timedelta(hours=2)
                atividade_data_fim += timedelta(hours=2)

            execucao.tempo_total = timedelta(0)
            execucao.tempo_foco = timedelta(0)

            # percorremos o arquivo de log até os eventos terem um datetime maior que o do inicio da atividade
            line = f.readline()
            at_open = True
            while line and at_open:
                event_datetime, event_name, event_msg = CodebenchExtractor.__get_event_info(line)
                if event_name == 'focus' and event_datetime and (event_datetime >= atividade_data_inicio):
                    last_interaction = event_datetime
                    line = f.readline()
                    while line and event_name != 'blur':
                        next_interaction, event_name, event_msg = CodebenchExtractor.__get_event_info(line)
                        if next_interaction:
                            if next_interaction > atividade_data_fim:
                                at_open = False
                                break
                            intervalo = next_interaction - last_interaction
                            execucao.tempo_total += intervalo
                            if intervalo <= CodebenchExtractor.__limite_ociosidade:
                                execucao.tempo_foco += intervalo
                            last_interaction = next_interaction
                        line = f.readline()
                line = f.readline()

    @staticmethod
    def __get_event_info(log_line: str):
        """
        Recebe uma linha de entrada do arquivo de logs do CodeMirro e retorna uma Tupla com:

        - A Data e Hora do evento
        - Nome do evento (tipo)
        - Mensagem do evento (texto)

        :param log_line: 
        :return: Tupla com data, nome, mensagem.
        """
        date, name, msg = None, '', ''
        try:
            date, _, log_line = log_line.partition('#')
            name, _, msg = log_line.partition('#')
            # data e hora do evento desconsiderando os milisegundos
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        except Exception:
            date = None
            name = ''
            msg = ''

        return date, name, msg

    @staticmethod
    def __extract_executions_count(path: str, execucao: Execucao):
        """
        Recupera as informações de submissões, testes e erros do arquivo de 'log' das tentativas de solução de um exercício.

        As informações sobre submissões, testes e erros são salvos no objeto 'execucao'.

        :param path: Caminho absoluto do arquivo de 'log' com as informações das execuções feitas pelo estudante.
        :type path: str
        :param execucao: Objeto que irá armazenar as informações obtidas do arquivo de 'log' do Codebench.
        :type execucao: model.Execucao
        """
        error_names = []
        with open(path, 'r') as f:
            execucao.n_submissoes = 0
            execucao.n_testes = 0
            execucao.n_erros = 0
            execucao.nota_final = 0.0

            i = 0
            lines = f.readlines()
            size = len(lines)

            while i < size:
                if lines[i].startswith('== S'):
                    execucao.t_execucao = None
                    execucao.acertou = False
                    execucao.n_submissoes += 1
                    i += 1
                    while not lines[i].startswith('*-*'):
                        if lines[i].startswith('-- CODE'):
                            i += 1
                            code_start_line = i
                            while not lines[i].startswith('-- '):
                                i += 1
                            code_end_line = i
                        elif lines[i].startswith('-- EXEC'):
                            value = lines[i + 1].strip()
                            try:
                                execucao.t_execucao = float(value)
                            except Exception:
                                execucao.t_execucao = None
                            i += 2
                        elif lines[i].startswith('-- GRAD'):
                            value = lines[i + 1].strip()[:-1]
                            try:
                                execucao.nota_final = float(value)
                            except Exception:
                                execucao.nota_final = None
                            i += 2
                        elif lines[i].startswith('-- ERROR'):
                            execucao.n_erros += 1
                            i += 2
                            while not lines[i].startswith('*-*'):
                                m = re.match(r"^([\w_\.]+Error)", lines[i])
                                if m:
                                    error_names.append(m.group(0))
                                i += 1
                        else:
                            i += 1

                    if execucao.nota_final > 99.99:
                        try:
                            code = ''.join(lines[code_start_line:code_end_line])
                            execucao.metricas = CodebenchExtractor.__extract_code_metrics(code)
                            with open('temp.py', 'w') as temp:
                                temp.write(code)
                            execucao.tokens = CodebenchExtractor.__extract_code_tokens('temp.py')
                            execucao.acertou = True
                            i = size + 1
                        except Exception:
                            execucao.nota_final = 0.0
                            execucao.metricas = None
                            execucao.tokens = None
                            Logger.error(f'Erro ao extrair métricas e tokens do arquivo de log de execucoes: {path}')

                elif lines[i].startswith('== T'):
                    execucao.n_testes += 1
                    while not lines[i].startswith('*-*'):
                        if lines[i].startswith('-- ERROR'):
                            execucao.n_erros += 1
                            i += 2
                            while not lines[i].startswith('*-*'):
                                m = re.match(r"^([\w_\.]+Error)", lines[i])
                                if m:
                                    error_names.append(m.group(0))
                                i += 1
                        else:
                            i += 1
                i += 1

        erros_count = Util.count_errors(error_names, execucao)
        if len(erros_count):
            CSVParser.salvar_erros(erros_count)

    @staticmethod
    def extract_execucoes(estudante: Estudante):
        """
        Recupera todas as :class:`Execucoes` feitas por um :class:`Estudante` tentando solucionar um Exercício de uma :class:`Atividade`.

        As execuções estão localizadas dentro da pasta 'executions', dentro do diretório do estudante.

        Cada estudante possui um registro de execuções para cada exercício.

        As execuções de uma determinada questão corresponde a um arquivo de extensão '.log', e cujo nome é formado pela composição do código da atividade e do código da questão, separados por um 'underscore'.

        As execuções encontradas são salvas no objeto estudante (estudante.execucoes).

        Exemplo de uso:
            CodebenchExtractor.extract_execucoes(estudante)

            for execucao in estudante.execucoes:
                print(execucao)
            ...

        :param estudante: O estudante cujas execuções devem ser recuperadas.
        :type estudante: Estudante
        """
        # transforma a lista de atividades da turma num dicionário, utilizando o código da turma como 'chave' (key)
        # isto facilita a obtenção do intervalo da atividade no cálculo dos tempos de implementação e interação
        atividades = {a.codigo: a for a in estudante.turma.atividades}
        # coleta todas os arquivos/pastas dentro do diretório de execuções do aluno
        with os.scandir(f'{estudante.path}/executions') as arquivos:
            for arquivo in arquivos:
                # se a 'entrada' for um arquivo de extensão '.log', então corresponde as execuções de uma questão.
                if arquivo.is_file() and arquivo.path.endswith(CodebenchExtractor.__codemirror_file_extension):
                    Logger.info(f'Extraindo informações de Execução: {arquivo.name}')
                    # divide o nome do arquivo obtendo os códigos da atividade e exercício.
                    atividade_code, exercicio_code, *_ = arquivo.name.replace(
                        CodebenchExtractor.__codemirror_file_extension, '').split('_')
                    atividade = atividades.get(int(atividade_code), None)
                    execucao = Execucao(estudante.periodo, estudante.turma, estudante, atividade, int(exercicio_code))

                    CodebenchExtractor.__extract_executions_count(arquivo.path, execucao)

                    codemirror_file = f'{estudante.path}/codemirror/{arquivo.name}'
                    if os.path.exists(codemirror_file):
                        CodebenchExtractor.__extract_solution_interval(codemirror_file, execucao)
                    else:
                        Logger.warn(f'Arquivo de execução não encontrado: {codemirror_file}')

                    if not execucao.metricas:
                        code_file = arquivo.name.replace(CodebenchExtractor.__codemirror_file_extension,
                                                         CodebenchExtractor.__exercices_file_extension)
                        code_file = f'{estudante.path}/codes/{code_file}'
                        if os.path.exists(code_file):
                            with open(code_file) as f:
                                codigo = ''.join(f.readlines())
                            try:
                                execucao.metricas = CodebenchExtractor.__extract_code_metrics(codigo)
                                execucao.tokens = CodebenchExtractor.__extract_code_tokens(code_file)
                            except Exception as e:
                                execucao.metricas = None
                                execucao.tokens = None
                                Logger.error(f'Erro ao extrair métricas e tokens do arquivo, {str(e)}: {code_file}')
                        else:
                            Logger.warn(f'Arquivo de código fonte não encontrado: {code_file}')

                    estudante.execucoes.append(execucao)

    @staticmethod
    def extract_solucoes(path: str):
        """
        Extrai as métricas das soluções dos exercícios propostas pelos Professores.

        As soluções estão salvas com a extensão '.code'.

        Exemplo de uso:
            solucoes = CodebenchExtractor.extract_solucoes([solutions_path])

            for solucao in solucoes:
                print(solucao)
            ...

        :param path: Caminho absoluto para a pasta onde se encontram as soluções.
        :type path: str
        :return: Lista de Soluções e suas métricas
        """
        solucoes = []
        # coleta todas os arquivos/pastas dentro do diretório de execuções do aluno
        with os.scandir(path) as arquivos:
            for arquivo in arquivos:
                # se a 'entrada' for um arquivo de extensão '.code', então corresponde as execuções de uma questão.
                if arquivo.is_file() and arquivo.path.endswith(CodebenchExtractor.__solution_extension):
                    Logger.info(f'Extraindo métricas da Solução: {arquivo.path}')
                    solucao = Solucao(int(arquivo.name.replace(CodebenchExtractor.__solution_extension, '')))
                    with open(arquivo.path, 'r') as f:
                        codigo = ''.join(f.readlines())
                    try:
                        solucao.metricas = CodebenchExtractor.__extract_code_metrics(codigo)
                        solucao.tokens = CodebenchExtractor.__extract_code_tokens(arquivo.path)
                        solucoes.append(solucao)
                    except Exception as e:
                        Logger.error(
                            f'Não foi possível extrair métricas e tokens do códigodo instrutor: {arquivo.path}')

        return solucoes

    @staticmethod
    def __extract_code_tokens(path: str):
        """
        Extrai e contabiliza Tokens de um arquivo de Código-Fonte Python.

        :param path: Caminho absoluto para o arquivo de Código-Fonte Python.
        :return: Objeto CodeTokens com a contagem de tokens encontrados.
        """
        # TODO média de caracteres por linha, média de espaços por linha, executa (True or False)
        # TODO comprimento medio dos user-defined identifiers
        # TODO desagrupar sum/minus e mult/div
        ct = CodeTokens(0)
        kwd_unique = set()
        lgc_unique = set()
        btf_unique = set()
        tpf_unique = set()
        asg_unique = set()
        art_unique = set()
        cmp_unique = set()
        btw_unique = set()

        with tokenize.open(path) as f:
            tokens = tokenize.generate_tokens(f.readline)
            for token in tokens:
                exact_type = token.exact_type
                if keyword.iskeyword(token.string):
                    ct.keywords += 1
                    kwd_unique.add(token.string)
                    if CodebenchExtractor.__conditional_token.get(token.string, False):
                        ct.conditionals += 1
                    elif CodebenchExtractor.__is_import_token(token):
                        ct.imports += 1
                    elif CodebenchExtractor.__loop_token.get(token.string, False):
                        ct.loops += 1
                    elif CodebenchExtractor.__logical_op_token.get(token.string, False):
                        ct.logical_op += 1
                        lgc_unique.add(token.string)
                    elif token.string == 'True' or token.string == 'False':
                        ct.literal_booleans += 1
                    elif token.string == 'break' or token.string == 'continue':
                        ct.loop_control += 1
                    elif token.string == 'is':
                        ct.identity_op += 1
                    elif token.string == 'in':
                        ct.membership_op += 1
                    elif token.string == 'lambda':
                        ct.lambdas += 1
                elif CodebenchExtractor.__builtin_token.get(token.string, False):
                    ct.builtin_f += 1
                    btf_unique.add(token.string)
                    if CodebenchExtractor.__type_token.get(token.string, False):
                        ct.type_f += 1
                        tpf_unique.add(token.string)
                    elif token.string == 'print':
                        ct.prints += 1
                    elif token.string == 'input':
                        ct.inputs += 1
                elif token.type == tokenize.OP:
                    if exact_type == tokenize.EQUAL or exact_type == tokenize.DOUBLESLASHEQUAL or (tokenize.PLUSEQUAL <= exact_type <= tokenize.DOUBLESTAREQUAL):
                        ct.assignments += 1
                        asg_unique.add(token.string)
                    elif (tokenize.PLUS <= exact_type <= tokenize.SLASH) or exact_type == tokenize.PERCENT or exact_type == tokenize.DOUBLESTAR or exact_type == tokenize.DOUBLESLASH:
                        ct.arithmetic_op += 1
                        art_unique.add(token.string)
                    elif (tokenize.EQEQUAL <= exact_type <= tokenize.GREATEREQUAL) or exact_type == tokenize.LESS or exact_type == tokenize.GREATER:
                        ct.comparison_op += 1
                        cmp_unique.add(token.string)
                    elif exact_type == tokenize.VBAR or exact_type == tokenize.AMPER or (tokenize.TILDE <= exact_type <= tokenize.RIGHTSHIFT):
                        ct.bitwise_op += 1
                        btw_unique.add(token.string)
                    elif exact_type == tokenize.LPAR:
                        ct.lpar += 1
                    elif exact_type == tokenize.RPAR:
                        ct.rpar += 1
                elif token.type == tokenize.NUMBER:
                    ct.literal_numbers += 1
                elif token.type == tokenize.STRING:
                    ct.literal_strings += 1

        ct.keywords_unique = len(kwd_unique)
        ct.logical_op_unique = len(lgc_unique)
        ct.builtin_f_unique = len(btf_unique)
        ct.type_f_unique = len(tpf_unique)
        ct.assignments_unique = len(asg_unique)
        ct.arithmetic_op_unique = len(art_unique)
        ct.comparison_op_unique = len(cmp_unique)
        ct.bitwise_op_unique = len(btw_unique)

        return ct
