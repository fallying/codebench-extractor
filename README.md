# Extrator para o Dataset Codebench - Marcos Lima - 2020

> Extrator escrito em Python para o dataset do Juíz Online Codebench.

> Keywords: `extrator`, `codebench`, `python`, `data-mining`

<!-- TABLE OF CONTENTS -->
## Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Built with](#built-with)
    - [Python3](#python3)
        - [Pandas](#pandas)
        - [Numpy](#numpy)
        - [Matplotlib](#matplotlib)
        - [Seaborn](#seaborn)
- [Release History](#release-history)
- [Contact](#contact)
- [License](#license)

## Sobre o Projeto

### Codebench

O CodeBench (http://codebench.icomp.ufam.edu.br/) é um sistema juiz online, desenvolvido pelo Instituto de Computação da Universidade Federal do Amazonas, que tem por objetivos: 

- prover ao discente de disciplinas de programação um conjunto de ferramentas pedagógicas capazes de estimular e facilitar seu aprendizado;
- prover o docente com informações úteis sobre a caminhada do aluno nas disciplinas de programação;
- dispor um conjunto de ferramentas capazes de simplificar o trabalho docente; e
- fomentar e apoiar professores no desenvolvimento e/ou implementação de práticas de ensino mais modernas e criativas.

Através do Codebench, os professores podem disponibilizar exercícios de programação para seus alunos, que por sua vez devem desenvolver soluções para tais exercícios e submetê-las através da interface do sistema. O Ambiente de Desenvolvimento Integrado, ou Integrated Development Environment (IDE), utilizado pelos alunos para desenvolver as soluções dos exercícios propostos, atualmente suporta as principais funcionalidades de um IDE típico, tais como: 

- autocompletion;
- autosave;
- syntax highlighting;
- busca e substituição de strings; e
- etc.

Uma vez que um aluno submete uma solução para um dado exercício, o sistema informa instantaneamente ao aluno se sua solução está correta ou errada. As soluções são verificadas por meio de casos de teste. Ao cadastrar um dado exercício no sistema, o professor ou monitor deverá informar um ou mais casos de testes que serão usados para julgar a corretude dos códigos submetidos pelos alunos. Um caso de teste é formado por um par <E, S>, onde E é a entrada passada ao código do aluno, e S é a saída correta para a entrada fornecida. Por exemplo, considerando um exercício em que o aluno deverá imprimir o quadrado de um valor fornecido, os casos de teste deste exercícios poderiam ser: <1, 1>, <6, 36> e <12, 144>.

Atualmente, o CodeBench suporta as seguintes linguagens de programação: C, C++, Java, Python, Haskell e Lua. Além dessas linguagens, o ambiente também suporta a linguagem SQL, para exercícios envolvendo consultas a bancos de dados. Ao criar um dado trabalho, o professor ou monitor deverá informar qual linguagem será usada pelos alunos para desenvolver as soluções dos exercícios de programação desse trabalho. Além disso, o CodeBench permite a troca de mensagens entre alunos e professores de uma dada turma, bem como o compartilhamento de recursos didáticos por parte dos professores.


### O Conjunto de Dados

O CodeBench registra automaticamente todas as ações realizadas pelos alunos no IDE incorporado durante suas tentativas de resolver os exercícios propostos. Atualmente o conjunto de dados (http://codebench.icomp.ufam.edu.br/dataset/) contém todos os registros coletados de alunos CS1 durante os semestres letivos compreendidos entre 2016 e 2019. Os dados estão distribuídos em diversos arquivos, organizados numa estrutura hierárquica de diretórios.

Devido a organização semi-estruturada e distribuída dos dados, fez-se necessário organizá-los segundo algum critério. Para tanto, desenvolvemos em Python um extrator automatizado, capaz de percorrer todo o conjunto de dados, minerando e organizando as informações disponíveis.

### Nosso Extrator


```
project
│   README.md
│   file001.txt    
│
└───folder1
│   │   file011.txt
│   │   file012.txt
│   │
│   └───subfolder1
│       │   file111.txt
│       │   file112.txt
│       │   ...
│   
└───folder2
    │   file021.txt
    │   file022.txt
```

## Built with

### Python3

#### Pandas

#### Numpy

#### Matplotlib

#### Seaborn

## Release History

## License

- **[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)** [![GNU GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
- Copyright 2020 © [marcosmapl](https://github.com/marcosmapl).

<!-- Markdown link & img dfn's -->
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/marcosmapl

## Contato

Marcos A. P. de Lima  – marcos.lima@icomp.ufam.edu.br
[![LinkedIn][linkedin-shield]][linkedin-url]

Leandro Silva Galvao de Carvalho  – galvao@icomp.ufam.edu.br

<!-- ACKNOWLEDGEMENTS -->
## Agradecimentos

- [Elaine H. T. Oliveira](elaine@icomp.ufam.edu.br)
- [David B. F. Oliveira](david@icomp.ufam.edu.br)
- [Filipe Dwan Pereira](david@icomp.ufam.edu.br)
- ...
