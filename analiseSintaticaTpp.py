# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# lexer.py
# Analisador sintático e geração de uma árvore sintática abstrata para a
#   linguagem Caleidoscópio
# Autores: Rodrigo Hübner e Jorge Luiz Franzon Rossi
#-------------------------------------------------------------------------
# Analisador sintatico para a linguagem T++
# Autor: Marco Cezar Moreira de Mattos

from ply import yacc
from analiselexicaTpp import Lexer

class Tree:

	def __init__(self, type_node, child=[], value=''):
		self.type = type_node
		self.child = child
		self.value = value

	def __str__(self):
		return self.type

class Parser:

	def __init__(self, code):
		lex = Lexer()
		self.tokens = lex.tokens
		self.precedence = (
			('left', 'EQ', 'MAIOR', 'MENOR', 'MAIOREQ', 'MENOREQ'),
			('left', 'SOMA', 'SUB'),
			('left', 'MUL', 'DIV'),
		)
		parser = yacc.yacc(debug=True, module=self, optimize=False)
		self.ast = parser.parse(code)


	def p_top_1(self, p):
		'top : codigo'
		
		p[0] = Tree('top', [p[1]])
	
	def p_top_2(self, p):
		'top : top codigo'
		
		p[0] = Tree('top', [p[1], p[2]])

	def p_codigo(self, p):
		'''
		codigo : declaracao
			   | funcao
		'''
		p[0] = Tree('codigo', [p[1]])

	def p_declaracao(self, p):
		'declaracao : tipo DPON ID'
		p[0] = Tree('declaracao', [p[1]], p[3])

	def p_funcao(self, p):
		'funcao : tipo ID APAR argumentos FPAR corpo FIM'
		p[0] = Tree('funcao', [p[1], p[4], p[6]], p[2])

	def p_argumentos_1(self, p):
		'argumentos : '

	def p_argumentos_2(self, p):
		'argumentos : declaracao VIRG argumentos'
		p[0] = Tree('argumentos', [p[1], p[3]])

	def p_argumentos_3(self, p):
		'argumentos : declaracao'
		p[0] = Tree('argumentos', [p[1]])

	def p_corpo_1(self, p):
		'corpo : '

	def p_corpo_2(self, p):
		'corpo : corpo detalhamento'
		p[0] = Tree('corpo', [p[1], p[2]])

	def p_detalhamento(self, p):
		'''
		detalhamento : atribuicao
			  | leia
			  | escreva
			  | declaracao
			  | chamada
			  | repita
			  | condicao
			  | retorna
		'''
		p[0] = Tree('detalhamento', [p[1]])

	def p_chamada(self, p):
		'chamada : ID APAR argumentos_chamada FPAR'

		p[0] = Tree('chamada', [p[3]], p[1])

	def p_leia(self, p):
		'leia : LEIA APAR FPAR'

		p[0] = Tree('leia', [], p[1])

	def p_escreva(self, p):
		'escreva : ESCREVA APAR expressao FPAR'
		
		p[0] = Tree('escreva', [p[3]], p[1])

	def p_retorna(self, p):
		'retorna : RETORNA expressao'

		p[0] = Tree('retorna', [p[2]], p[1])

	def p_argumentos_chamada_1(self, p):
		'argumentos_chamada : '

	def p_argumentos_chamada_2(self, p):
		'argumentos_chamada : expressao'
		p[0] = Tree('argumentos_chamada', [p[1]])

	def p_argumentos_chamada_3(self, p):
		'argumentos_chamada : expressao VIRG argumentos_chamada'
		p[0] = Tree('argumentos_chamada', [p[1], p[3]])

	def p_atribuicao(self, p):
		'atribuicao : ID ATRIB expressao'
		p[0] = Tree('atribuicao', [p[3]], p[1])

	def p_condicao_1(self, p):
		'condicao : SE expressao_condicao ENTAO corpo FIM'
		p[0] = Tree('condicao', [p[2], p[4]])

	def p_condicao_2(self, p):
		'condicao : SE expressao_condicao ENTAO corpo SENAO corpo FIM'
		p[0] = Tree('condicao', [p[2], p[4], p[6]])

	def p_num_int(self, p):
		'num_int : NUM_INT'
		p[0] = Tree('num_inteiro', [], p[1])


	def p_num_flu(self, p):
		'num_flu : NUM_FLU'
		p[0] = Tree('num_flutuante', [], p[1])

	def p_id(self, p):
		'id : ID'
		p[0] = Tree('id', [], p[1])

	def p_expressao_condicao_1(self, p):
		'''
		expressao_condicao : APAR expressao_logica FPAR
		'''
		p[0] = Tree('expressao_condicao', [p[2]])

	def p_expressao_condicao_2(self, p):
		'''
		expressao_condicao : expressao_logica
		'''
		p[0] = Tree('expressao_condicao', [p[1]])

	def p_expressao_logica(self, p):
		'''
		expressao_logica : expressao EQ expressao
						 | expressao MAIOR expressao
						 | expressao MENOR expressao
						 | expressao MAIOREQ expressao
						 | expressao MENOREQ expressao
		'''
		p[0] = Tree('expressao_logica', [p[1], p[3]], p[2])

	def p_expressao_1(self, p):
		'''
		expressao : num_int
				  | num_flu
				  | id
		'''
		p[0] = Tree('expressao_fim', [p[1]])

	def p_expressao_2(self, p):
		'''
		expressao : chamada
				  | expressao_normal
				  | expressao_unaria
		'''
		p[0] = Tree('expressao_meio', [p[1]])


	def p_expressao_3(self, p):
		'''
		expressao : APAR expressao FPAR
		'''
		p[0] = Tree('expressao', [p[2]])


	def p_expressao_normal(self, p):
		'''
		expressao_normal : expressao SOMA expressao
						 | expressao SUB expressao
						 | expressao DIV expressao
						 | expressao MUL expressao
		'''
		p[0] = Tree('expressao_normal', [p[1], p[3]], p[2])

	def p_expressao_unaria(self, p):
		'''
		expressao_unaria : SUB expressao
						 | SOMA expressao
 		'''
		p[0] = Tree('expressao_unaria', [p[2]], p[1])


	def p_tipo_1(self, p):
		'tipo : FLUTUANTE'
		p[0] = Tree('tipo_flutuante', [])


	def p_tipo_2(self, p):
		'tipo : INTEIRO'
		p[0] = Tree('tipo_inteiro', [])


	def p_repita(self, p):
		'repita : REPITA corpo ATE expressao_condicao'
		p[0] = Tree('repita', [p[2], p[4]])


	def p_error(self, p):
		if p:
			print("Erro sintático: '%s', linha %d" % (p.value, p.lineno))
			exit(1)
		else:
			yacc.restart()
			print('Erro sintático: definições incompletas!')
			exit(1)


def imprime_arvore(raiz, level="-"):
	if raiz != None:
		print(level + "Tipo: " + raiz.type + " Valor: "+ raiz.value)
		for son in raiz.child:
			imprime_arvore(son, level+"-")

if __name__ == '__main__':
	from sys import argv, exit
	f = open(argv[1])
	a = Parser(f.read())
	imprime_arvore(a.ast)