# -*- coding: utf-8 -*-
### Codebench Dataset Extractor by Marcos Lima (marcos.lima@icomp.ufam.edu.br)
### Universidade Federal do Amazonas - UFAM
### Instituto de Computação - IComp

import os
import time

from csv_parser import CSVParser
from extractor import CodebenchExtractor
from util import Util, Logger

__version__ = '2.3.0'

# cwd (current working dir): diretório de trabalho atual
__cwd__ = os.getcwd()


def main():
    # cria a pasta para os arquivos de saídade (CSV), caso já exista, recria os arquivos
    CSVParser.create_output_dir()
    # configura o módulo de log
    Logger.configure()

    Util.clear_console()
    print(f'-- CODEBENCH DATASET EXTRACTOR v{__version__} --')
    dataset_dir = input('Informe o caminho para o dataset: ')

    loop = True
    while loop:
        Util.clear_console()
        print(f'-- CODEBENCH DATASET EXTRACTOR v{__version__} --')
        print()
        print('Escolha uma opção:')
        print('1 - Extrair dados dos períodos letivos')
        print('2 - Extrair dados das turmas ministradas (disciplinas)')
        print('3 - Extrair dados das atividades realizadas (trabalhos e exames)')
        print('4 - Extrair dados dos estudantes cadastrados')
        print('5 - Extrair dados das tentativas de solução')
        print('6 - Extrair dados das soluções dos instrutores')
        print('0 - Sair')
        op = input('Digite a opção desejada: ')
        op = int(op.strip())
        if op == 0:
            loop = False
        elif op == 1:
            start_time = time.time()
            periodos = CodebenchExtractor.extract_periodos(dataset_dir)
            CSVParser.salvar_periodos(periodos)
            time_elapsed = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
            print(f'Tempo Total de Execução: {time_elapsed}. Tecla algo para continuar...')
            input()
        elif op == 2:
            start_time = time.time()
            turmas = []
            periodos = CodebenchExtractor.extract_periodos(dataset_dir)
            for periodo in periodos:
                CodebenchExtractor.extract_turmas(periodo)
                turmas.extend(periodo.turmas)
            CSVParser.salvar_turmas(turmas)
            time_elapsed = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
            print(f'Tempo Total de Execução: {time_elapsed}. Tecla algo para continuar...')
            input()
        elif op == 3:
            start_time = time.time()
            atividades = []
            periodos = CodebenchExtractor.extract_periodos(dataset_dir)
            for periodo in periodos:
                CodebenchExtractor.extract_turmas(periodo)
                for turma in periodo.turmas:
                    CodebenchExtractor.extract_atividades(turma)
                    atividades.extend(turma.atividades)
            CSVParser.salvar_atividades(atividades)
            time_elapsed = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
            print(f'Tempo Total de Execução: {time_elapsed}. Tecla algo para continuar...')
            input()
        elif op == 4:
            start_time = time.time()
            periodos = CodebenchExtractor.extract_periodos(dataset_dir)
            for periodo in periodos:
                CodebenchExtractor.extract_turmas(periodo)
                for turma in periodo.turmas:
                    CodebenchExtractor.extract_estudantes(turma)
                    CSVParser.salvar_estudantes(turma.estudantes)
            time_elapsed = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
            print(f'Tempo Total de Execução: {time_elapsed}. Tecla algo para continuar...')
            input()
        elif op == 5:
            start_time = time.time()
            periodos = CodebenchExtractor.extract_periodos(dataset_dir)
            for periodo in periodos:
                CodebenchExtractor.extract_turmas(periodo)
                for turma in periodo.turmas:
                    CodebenchExtractor.extract_estudantes(turma)
                    for estudante in turma.estudantes:
                        CodebenchExtractor.extract_execucoes(estudante)
                        CSVParser.salvar_execucoes(estudante.execucoes)
            time_elapsed = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
            print(f'Tempo Total de Execução: {time_elapsed}. Tecla algo para continuar...')
            input()
        elif op == 6:
            solutions_dir = input('Informe o caminho para as soluções dos instrutores: ')
            start_time = time.time()
            solucoes = CodebenchExtractor.extract_solucoes(solutions_dir)
            CSVParser.salvar_solucoes(solucoes)
            time_elapsed = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
            print(f'Tempo Total de Execução: {time_elapsed}. Tecla algo para continuar...')
            input()


if __name__ == '__main__':
    main()
