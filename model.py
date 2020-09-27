### Codebench Dataset Extractor by Marcos Lima (marcos.lima@icomp.ufam.edu.br)
### Universidade Federal do Amazonas - UFAM
### Instituto de Computação - IComp

from typing import List


class CSVEntity:
    """Interface que especifica os métodos de uma Entidade que possa ser salva num arquivo '.csv' (dataset)."""

    def as_row(self) -> List:
        """Retorna valores dos atributos da Entidade numa lista (row), para então serem salvos no dataset."""
        pass

    @staticmethod
    def get_csv_header() -> List[str]:
        """Retorna uma lista com o nome de todos os atributos da Entidade, que devam ser salvas no dataset (csv file header)."""
        pass


class Periodo(CSVEntity):
    """Entidade que representa um Período letivo."""

    def __init__(self, descricao: str, path: str):
        """
        Método Construtor.

        :param descricao: Descrição do Período, composta pelo ano e número do semestre.
        :param path: Caminho absoluto para o diretório do Período, dentro do dataset Codebench.
        """
        self.descricao = descricao
        self.path = path
        self.turmas = []

    def as_row(self) -> List:
        return [self.descricao]

    @staticmethod
    def get_csv_header():
        return list(Periodo(None, None).__dict__)[:-2]


class Turma(CSVEntity):
    """Entidade que representa uma Turma de Estudantes num :class:`Periodo` letivo."""

    def __init__(self, periodo: Periodo, codigo: int, path: str):
        """
        Método Construtor.

        :param periodo: O Periodo letivo em que a Turma ocorrreu.
        :param codigo: O código númerico único da Turma.
        :param path: Caminho absoluto para o diretório da Turma dentro do dataset do Codebench
        """
        self.periodo = periodo
        self.codigo = codigo
        self.descricao = None
        self.path = path
        self.atividades = []
        self.estudantes = []

    def as_row(self) -> List:
        return [
            self.periodo.descricao,
            self.codigo,
            self.descricao
        ]

    @staticmethod
    def get_csv_header():
        return list(Turma(Periodo(None, None), 0, None).__dict__)[:-3]


class Atividade(CSVEntity):
    """Entidade que representa uma Atividade realizada numa :class:`Turma`."""

    def __init__(self, turma: Turma, codigo: int, path: str):
        """
        Método Construtor.

        :param turma: A Turma em que a Atividade foi realizada.
        :param codigo: Código numérico único da Atividade.
        :param path: Caminho absoluto para o arquivo com as informações da Atividade (.data).
        """
        self.periodo = turma.periodo
        self.turma = turma
        self.codigo = codigo
        self.titulo = None
        self.data_inicio = None
        self.data_termino = None
        self.linguagem = None
        self.tipo = None
        self.peso = None
        self.n_blocos = None
        self.blocos = []
        self.path = path

    def as_row(self) -> List:
        return [
            self.periodo.descricao,
            self.turma.codigo,
            self.codigo,
            self.titulo,
            self.data_inicio,
            self.data_termino,
            self.linguagem,
            self.tipo,
            self.peso,
            self.n_blocos,
            self.blocos
        ]

    @staticmethod
    def get_csv_header():
        return list(Atividade(Turma(Periodo('', ''), 0, ''), 0, '').__dict__)[:-1]


class Estudante(CSVEntity):
    """Entidade que representa um Estudante matriculado numa :class:`Turma`."""

    def __init__(self, periodo: Periodo, turma: Turma, codigo: int, path: str):
        """
        Método Construtor

        :param periodo: O Período letivo em que a turma ocorreu.
        :param turma: A Turma na qual o Estudante está matriculado.
        :param codigo: Código numérico único do Estudante.
        :param path: Caminho absoluto para o diretório com as informações do Estudante no dataset Codebench.
        """
        self.periodo = periodo
        self.turma = turma
        self.codigo = codigo
        self.curso_id = None
        self.curso_nome = None
        self.instituicao_id = None
        self.instituicao_nome = None
        self.escola_nome = None
        self.escola_tipo = None
        self.escola_turno = None
        self.escola_ano_grad = None
        self.sexo = None
        self.ano_nascimento = None
        self.estado_civil = None
        self.tem_filhos = None
        self.execucoes = []
        self.path = path

    def as_row(self) -> List:
        return [
            self.periodo.descricao,
            self.turma.codigo,
            self.codigo,
            self.curso_id,
            self.curso_nome,
            self.instituicao_id,
            self.instituicao_nome,
            self.escola_nome,
            self.escola_tipo,
            self.escola_turno,
            self.escola_ano_grad,
            self.sexo,
            self.ano_nascimento,
            self.estado_civil,
            self.tem_filhos
        ]

    @staticmethod
    def get_csv_header() -> List[str]:
        return list(Estudante(None, None, 0, '').__dict__)[:-2]


class Execucao(CSVEntity):
    """
    Entidade que representa as Execuções do Código de um :class:`Estudante` na tentativa de resolver um Exercício proposto numa :class:`Atividade`.

    Contém informações sobre:
        - Quantidade de Submissões feitas pelo Estudante, :property:`Estudante.n_submissoes.
        - Quantidade de Testes feitos pelo Estudante.
        - Quantidade de Erros acusados pelo Interpretador Python durante as Submissões/Testes.
        - Tempo de Implementação descontado intervalos de 5 min (inatividade).
        - Tempo de Implementação Total.
        - Métricas de Complexidade de Código (McCabe).
        - Métricas de Software (Halstead).
        - Métricas Brutas de Código.
    """

    def __init__(self, periodo: Periodo, turma: Turma, estudante: Estudante, atividade: Atividade, exercicio_codigo: int):
        """
        Método Construtor.

        :param periodo: O Periodo letivo em que a Atividade ocorreu.
        :param turma: A Turma em que o Estudante estava matriculado.
        :param estudante: O Estudante que fez as Execuções.
        :param atividade: Código numérico único da Atividade do Exercício.
        :param exercicio_codigo: Código numérico único do Exercício que o Estudante tentava resolver.
        """
        self.periodo = periodo
        self.turma = turma
        self.estudante = estudante
        self.atividade = atividade
        self.exercicio = exercicio_codigo
        self.tempo_total = None
        self.tempo_foco = None
        self.n_submissoes = None
        self.n_testes = None
        self.n_erros = None
        self.t_execucao = None
        self.nota_final = None
        self.acertou = None
        self.metricas = Metricas(None)
        self.tokens = CodeTokens(None)

    def as_row(self) -> List:
        if not self.metricas:
            self.metricas = Metricas(None)
        if not self.tokens:
            self.tokens = CodeTokens(None)
        return [
            self.periodo.descricao,
            self.turma.codigo,
            self.estudante.codigo,
            self.atividade.codigo,
            self.exercicio,
            self.tempo_total,
            self.tempo_foco,
            self.n_submissoes,
            self.n_testes,
            self.n_erros,
            self.t_execucao,
            self.nota_final,
            self.acertou,
            self.metricas.complexity,
            self.metricas.n_classes,
            self.metricas.n_functions,
            self.metricas.loc,
            self.metricas.lloc,
            self.metricas.sloc,
            self.metricas.single_comments,
            self.metricas.comments,
            self.metricas.multilines,
            self.metricas.blank_lines,
            self.metricas.h1,
            self.metricas.h2,
            self.metricas.N1,
            self.metricas.N2,
            self.metricas.h,
            self.metricas.N,
            self.metricas.calculated_N,
            self.metricas.volume,
            self.metricas.difficulty,
            self.metricas.effort,
            self.metricas.bugs,
            self.metricas.time,
            self.tokens.imports,
            self.tokens.assignments,
            self.tokens.assignments_unique,
            self.tokens.kwds,
            self.tokens.kwds_unique,
            self.tokens.lt_numbers,
            self.tokens.lt_strings,
            self.tokens.lt_booleans,
            self.tokens.lgc_op,
            self.tokens.lgc_op_unique,
            self.tokens.and_op,
            self.tokens.or_op,
            self.tokens.not_op,
            self.tokens.arithmetic_op,
            self.tokens.arithmetic_op_unique,
            self.tokens.add_op,
            self.tokens.minus_op,
            self.tokens.mult_op,
            self.tokens.div_op,
            self.tokens.mod_op,
            self.tokens.power_op,
            self.tokens.div_floor_op,
            self.tokens.cmp_op,
            self.tokens.cmp_op_unique,
            self.tokens.equal_op,
            self.tokens.not_eq_op,
            self.tokens.lt_op,
            self.tokens.gt_op,
            self.tokens.less_op,
            self.tokens.greater_op,
            self.tokens.bitwise_op,
            self.tokens.bitwise_op_unique,
            self.tokens.bitwise_and,
            self.tokens.bitwise_or,
            self.tokens.bitwise_xor,
            self.tokens.bitwise_not,
            self.tokens.lshift_op,
            self.tokens.rshift_op,
            self.tokens.identity_op,
            self.tokens.membership_op,
            self.tokens.conditionals,
            self.tokens.ifs,
            self.tokens.elifs,
            self.tokens.elses,
            self.tokens.loops,
            self.tokens.whiles,
            self.tokens.fors,
            self.tokens.breaks,
            self.tokens.continues,
            self.tokens.builtin_f,
            self.tokens.builtin_f_unique,
            self.tokens.type_f,
            self.tokens.type_f_unique,
            self.tokens.lambdas,
            self.tokens.lpar,
            self.tokens.rpar,
            self.tokens.lsqb,
            self.tokens.rsqb,
            self.tokens.lbrace,
            self.tokens.rbrace,
            self.tokens.commas,
            self.tokens.colons,
            self.tokens.dots,
            self.tokens.prints,
            self.tokens.inputs,
            self.tokens.len,
            self.tokens.uident,
            self.tokens.uident_unique,
            self.tokens.uident_mean,
            self.tokens.uident_per_line,
            self.tokens.uident_chars
        ]

    @staticmethod
    def get_csv_header() -> List[str]:
        return list(Execucao(None, None, None, None, 0).__dict__)[:-2]+list(Metricas(None).__dict__)+list(CodeTokens(None).__dict__)


class Solucao(CSVEntity):
    """
    Entidade que representa métricas de uma :class:`Solucao` proposta por um Professor para um Exercício

    Contém informações sobre:
        - Métricas de Complexidade de Código (McCabe).
        - Métricas de Software (Halstead).
        - Métricas Brutas de Código.
    """

    def __init__(self, codigo: int):
        """
        Método Construtor

        :param codigo: Código numérico único do Exercicio da Solução.
        """
        self.codigo = codigo
        self.metricas = Metricas(None)
        self.tokens = CodeTokens(None)

    @staticmethod
    def get_csv_header() -> List[str]:
        return list(Solucao(0).__dict__)[:-2]+list(Metricas(None).__dict__)+list(CodeTokens(None).__dict__)

    def as_row(self) -> List:
        return [
            self.codigo,
            self.metricas.complexity,
            self.metricas.n_classes,
            self.metricas.n_functions,
            self.metricas.loc,
            self.metricas.lloc,
            self.metricas.sloc,
            self.metricas.single_comments,
            self.metricas.comments,
            self.metricas.multilines,
            self.metricas.blank_lines,
            self.metricas.h1,
            self.metricas.h2,
            self.metricas.N1,
            self.metricas.N2,
            self.metricas.h,
            self.metricas.N,
            self.metricas.calculated_N,
            self.metricas.volume,
            self.metricas.difficulty,
            self.metricas.effort,
            self.metricas.bugs,
            self.metricas.time,
            self.tokens.imports,
            self.tokens.assignments,
            self.tokens.assignments_unique,
            self.tokens.kwds,
            self.tokens.kwds_unique,
            self.tokens.lt_numbers,
            self.tokens.lt_strings,
            self.tokens.lt_booleans,
            self.tokens.lgc_op,
            self.tokens.lgc_op_unique,
            self.tokens.and_op,
            self.tokens.or_op,
            self.tokens.not_op,
            self.tokens.arithmetic_op,
            self.tokens.arithmetic_op_unique,
            self.tokens.add_op,
            self.tokens.minus_op,
            self.tokens.mult_op,
            self.tokens.div_op,
            self.tokens.mod_op,
            self.tokens.power_op,
            self.tokens.div_floor_op,
            self.tokens.cmp_op,
            self.tokens.cmp_op_unique,
            self.tokens.equal_op,
            self.tokens.not_eq_op,
            self.tokens.lt_op,
            self.tokens.gt_op,
            self.tokens.less_op,
            self.tokens.greater_op,
            self.tokens.bitwise_op,
            self.tokens.bitwise_op_unique,
            self.tokens.bitwise_and,
            self.tokens.bitwise_or,
            self.tokens.bitwise_xor,
            self.tokens.bitwise_not,
            self.tokens.lshift_op,
            self.tokens.rshift_op,
            self.tokens.identity_op,
            self.tokens.membership_op,
            self.tokens.conditionals,
            self.tokens.ifs,
            self.tokens.elifs,
            self.tokens.elses,
            self.tokens.loops,
            self.tokens.whiles,
            self.tokens.fors,
            self.tokens.breaks,
            self.tokens.continues,
            self.tokens.builtin_f,
            self.tokens.builtin_f_unique,
            self.tokens.type_f,
            self.tokens.type_f_unique,
            self.tokens.lambdas,
            self.tokens.lpar,
            self.tokens.rpar,
            self.tokens.lsqb,
            self.tokens.rsqb,
            self.tokens.lbrace,
            self.tokens.rbrace,
            self.tokens.commas,
            self.tokens.colons,
            self.tokens.dots,
            self.tokens.prints,
            self.tokens.inputs,
            self.tokens.len,
            self.tokens.uident,
            self.tokens.uident_unique,
            self.tokens.uident_mean,
            self.tokens.uident_per_line,
            self.tokens.uident_chars
        ]


class Erro(CSVEntity):
    """Entidade que representa a contagem de Erros de um mesmo Tipo, acusados pelo Interpretador Python, enquanto um :class:`Estudante` tentava resolver um Exercício."""

    def __init__(self, tipo: str, count: int):
        """
        Método Construtor

        :param tipo: Tipo (descrição do erro) segundo a nomenclatura do Interpretador Python.
        :param count: Quantidade de ocorrências do Erro enquanto o Estudante tentava resolver o Exercício.
        """
        self.periodo = None
        self.turma = None
        self.atividade = None
        self.estudante = None
        self.exercicio = None
        self.tipo = tipo
        self.ocorrencias = count

    def as_row(self) -> List:
        return [
            self.periodo.descricao,
            self.turma.codigo,
            self.atividade.codigo,
            self.estudante.codigo,
            self.exercicio,
            self.tipo,
            self.ocorrencias
        ]

    @staticmethod
    def get_csv_header() -> List[str]:
        return list(Erro('', 0).__dict__)


class Metricas:
    """Classe que representa as métricas de código extraídas usando o módulo 'radon'"""

    def __init__(self, default_value):
        self.complexity = default_value
        self.n_classes = default_value
        self.n_functions = default_value
        self.loc = default_value
        self.lloc = default_value
        self.sloc = default_value
        self.single_comments = default_value
        self.comments = default_value
        self.multilines = default_value
        self.blank_lines = default_value
        self.h1 = default_value
        self.h2 = default_value
        self.N1 = default_value
        self.N2 = default_value
        self.h = default_value
        self.N = default_value
        self.calculated_N = default_value
        self.volume = default_value
        self.difficulty = default_value
        self.effort = default_value
        self.bugs = default_value
        self.time = default_value


class CodeTokens:
    """Classe que representa os Tokens obtidos de um código Python"""

    def __init__(self, default_value):
        self.imports = default_value
        self.assignments = default_value
        self.assignments_unique = default_value
        self.kwds = default_value
        self.kwds_unique = default_value
        self.lt_numbers = default_value
        self.lt_strings = default_value
        self.lt_booleans = default_value
        self.lgc_op = default_value
        self.lgc_op_unique = default_value
        self.and_op = default_value
        self.or_op = default_value
        self.not_op = default_value
        self.arithmetic_op = default_value
        self.arithmetic_op_unique = default_value
        self.add_op = default_value
        self.minus_op = default_value
        self.mult_op = default_value
        self.div_op = default_value
        self.mod_op = default_value
        self.power_op = default_value
        self.div_floor_op = default_value
        self.cmp_op = default_value
        self.cmp_op_unique = default_value
        self.equal_op = default_value
        self.not_eq_op = default_value
        self.lt_op = default_value
        self.gt_op = default_value
        self.less_op = default_value
        self.greater_op = default_value
        self.bitwise_op = default_value
        self.bitwise_op_unique = default_value
        self.bitwise_and = default_value
        self.bitwise_or = default_value
        self.bitwise_xor = default_value
        self.bitwise_not = default_value
        self.lshift_op = default_value
        self.rshift_op = default_value
        self.identity_op = default_value
        self.membership_op = default_value
        self.conditionals = default_value
        self.ifs = default_value
        self.elifs = default_value
        self.elses = default_value
        self.loops = default_value
        self.whiles = default_value
        self.fors = default_value
        self.breaks = default_value
        self.continues = default_value
        self.builtin_f = default_value
        self.builtin_f_unique = default_value
        self.type_f = default_value
        self.type_f_unique = default_value
        self.lambdas = default_value
        self.lpar = default_value
        self.rpar = default_value
        self.lsqb = default_value
        self.rsqb = default_value
        self.lbrace = default_value
        self.rbrace = default_value
        self.commas = default_value
        self.colons = default_value
        self.dots = default_value
        self.prints = default_value
        self.inputs = default_value
        self.len = default_value
        self.uident = default_value
        self.uident_unique = default_value
        self.uident_mean = default_value
        self.uident_per_line = default_value
        self.uident_chars = default_value
