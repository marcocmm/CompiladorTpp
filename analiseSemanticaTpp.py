import pprint
from analiseSintaticaTpp import Parser


class Semantica:	

	def __init__(self, code):
		self.simbolos = {}
		self.escopo = "global"
		self.parser = Parser(code)
		self.top(self.parser.ast)

	def top(self, node):
		if node.type == "top":
			if len(node.child) == 1:
				self.codigo(node.child[0])
			else:
				self.top(node.child[0])
				self.codigo(node.child[1])

	def codigo(self, node):
		if node.child[0].type == "declaracao":
			self.declaracao(node.child[0])
		else:
			self.funcao(node.child[0])

	def declaracao(self, node):
		if self.escopo+"."+node.value in self.simbolos.keys():
			print(
				"Erro Semantico. Variavel "+self.escopo+"."+node.value + " já está declarada")
			exit(1)

		else:
			tipo_var = self.tipo(node.child[0])
			self.simbolos[self.escopo+"."+node.value] = ['declaracao', tipo_var, 'nao_atribuido']
			return tipo_var

	def declaracao_args(self, node):
		if self.escopo+"."+node.value in self.simbolos.keys():
			print(
				"Erro Semantico. Variavel "+self.escopo+"."+node.value + " já está declarada")
			exit(1)

		else:
			tipo_var = self.tipo(node.child[0])
			self.simbolos[self.escopo+"."+node.value] = ['declaracao', tipo_var, 'atribuido']
			return tipo_var

	def funcao(self, node):
		if self.escopo+"."+node.value in self.simbolos.keys():
			print(
				"Erro Semantico. Função "+self.escopo+"."+node.value + " já está declarada")
			exit(1)
		elif node.value in ["leia", "escreva"]:
			print(
				"Erro Semantico. Função "+node.value + " é reservada")
			exit(1)

		else:
			self.escopo = node.value
			tipo_func = self.tipo(node.child[0])
			lista_tipos = self.argumentos(node.child[1], [])
			self.corpo(node.child[2], tipo_func)      
			self.escopo = "global"
			self.simbolos[self.escopo+"."+node.value] = ['funcao', tipo_func, lista_tipos, "nao_atribuido"]
			if node.value == "principal":
				self.simbolos[self.escopo+"."+node.value] = ['funcao', tipo_func, lista_tipos, "atribuido"]


	def tipo(self, node):
		if  node.type == "tipo_flutuante":
			return "tipo_flutuante"
		else:
			return "tipo_inteiro"


	def argumentos(self, node, lista_tipos):
		if node == None:
			return []
		novo_tipo = self.declaracao_args(node.child[0])
		lista_tipos.append(novo_tipo)
		if len(node.child) != 1:
			self.argumentos(node.child[1], lista_tipos)

		return lista_tipos

	def corpo(self, node, tipo_func):
		if node == None:
			return
		self.corpo(node.child[0], tipo_func)
		self.detalhamento(node.child[1], tipo_func)


	def detalhamento(self, node, tipo_func):
		if node.child[0].type == "atribuicao":
			self.atribuicao(node.child[0])
		elif node.child[0].type == "leia":
			self.leia(node.child[0])
		elif node.child[0].type == "escreva":
			self.escreva(node.child[0])
		elif node.child[0].type == "declaracao":
			self.declaracao(node.child[0])
		elif node.child[0].type == "chamada":
			self.chamada(node.child[0])
		elif node.child[0].type == "repita":
			self.repita(node.child[0])
		elif node.child[0].type == "condicao":
			self.condicao(node.child[0])
		elif node.child[0].type == "retorna":
			self.retorna(node.child[0], tipo_func)

	def atribuicao(self,node):
		if (self.escopo+"."+node.value in self.simbolos.keys()):
			tipo = self.expressao(node.child[0],"")
			if tipo == "warning":
				print(
				"Warning Semantico. Variavel "+self.escopo+"."+node.value + " recebe uma expressao que contém tipo_flutuante e tipo_inteiro")
				if self.simbolos[self.escopo+"."+node.value][1] == "tipo_inteiro":
					print(
					"Warning Semantico. Variavel "+self.escopo+"."+node.value + " é do tipo_inteiro e recebe um valor do tipo_flutuante")
			elif (self.simbolos[self.escopo+"."+node.value][1] != tipo):
					print(
					"Warning Semantico. Variavel "+self.escopo+"."+node.value + " recebe um valor do tipo "+ tipo +"diferente do esperado")

			self.simbolos[self.escopo+"."+node.value] = [self.simbolos[self.escopo+"."+node.value][0], self.simbolos[self.escopo+"."+node.value][1],'atribuido']

		elif ("global."+node.value in self.simbolos.keys()):
			tipo = self.expressao(node.child[0],"")
			if tipo == "warning":
				print(
				"Warning Semantico. Variavel "+"global."+node.value + " recebe uma expressao que contém tipo_flutuante e tipo_inteiro")
				if self.simbolos["global."+node.value][1] == "tipo_inteiro":
					print(
					"Warning Semantico. Variavel "+"global."+node.value + " é do tipo_inteiro e recebe um valor do tipo_flutuante")
			elif (self.simbolos["global."+node.value][1] != tipo):
					print(
					"Warning Semantico. Variavel "+"global."+node.value + " rrecebe um valor do tipo "+ tipo +"diferente do esperado")
			self.simbolos["global."+node.value] = [self.simbolos["global."+node.value][0], self.simbolos["global."+node.value][1],'atribuido']

		else:
			print(
				"Erro Semantico. Variavel "+node.value + " não foi declarada")
			exit(1)


	def leia(self, node):
		self.argumentos_chamada(node.child[0], [])

	def escreva(self, node):
		self.argumentos_chamada(node.child[0], [])

	def chamada(self, node):

		if "global."+node.value not in self.simbolos.keys():
			print(
				"Erro Semantico. Função "+node.value + " não foi declarada aqui")
			exit(1)

		real_args = self.simbolos["global."+node.value][2]

		lista_args = self.argumentos_chamada(node.child[0], [])
		self.simbolos["global."+node.value][3] = "atribuido"
		
		if len(real_args) != len(lista_args):
			print(
				"Erro Semantico. Função global."+node.value + " recebeu uma quantia diferente de argumentos")
			exit(1)
		else:
			for i in range(0,len(real_args)):
				if real_args[i] != lista_args[i]:
					print(
					"Warning Semantico. Função global."+node.value + " recebeu um paremetro de tipo diferente")


	def repita(self, node):
		self.corpo(node.child[0], None)
		self.expressao_condicao(node.child[1],"")
	

	def condicao(self, node):
		self.expressao_condicao(node.child[0],"")
		self.corpo(node.child[1],None)
		if len(node.child) == 3:
			self.corpo(node.child[2], None)

	def retorna(self, node, tipo_func):
		tipo = self.expressao(node.child[0],"")
		if tipo == "warning":
			print(
			"Warning Semantico. Retorno da funcao  recebe uma expressao que contém tipo_flutuante e tipo_inteiro")
		elif tipo_func != tipo:
			print(
			"Warning Semantico. Retorno da funcao  recebe um valor do tipo "+ tipo +"diferente do esperado")



	'''
	tipo_int
	tipo_flu

	warning
	'''

	def expressao(self, node, tipo_exp):
		if node.type == "expressao":
			tipo = self.expressao(node.child[0], tipo_exp)
			tipo_exp = self.valida_tipo(tipo, tipo_exp)
		elif node.type == "expressao_meio":
			if node.child[0].type == "chamada":
				self.chamada(node.child[0])
				tipo = self.simbolos["global."+node.child[0].value][1]
				tipo_exp = self.valida_tipo(tipo, tipo_exp)
			elif node.child[0].type == "expressao_normal":
				tipo = self.expressao_normal(node.child[0], tipo_exp)
				tipo_exp = self.valida_tipo(tipo, tipo_exp)
			elif node.child[0].type == "expressao_unaria":
				tipo = self.expressao_unaria(node.child[0], tipo_exp)
				tipo_exp = self.valida_tipo(tipo, tipo_exp)

		else:
			if node.child[0].type == "id":
				node = node.child[0]
				if self.escopo+"."+node.value in self.simbolos.keys():
					if self.simbolos[self.escopo+"."+node.value][2] == 'nao_atribuido':
						print(
							"Erro Semantico. Variavel "+self.escopo+"."+node.value + " não foi atribuido")
						exit(1)
					tipo = self.simbolos[self.escopo+"."+node.value][1]
					tipo_exp = self.valida_tipo(tipo, tipo_exp)						

				elif "global."+node.value in self.simbolos.keys():
					if (self.simbolos["global."+node.value][2] == 'nao_atribuido'):
						print(
							"Erro Semantico. Variavel "+"global."+node.value + " não foi atribuido")
						exit(1)

					tipo = self.simbolos["global."+node.value][1]
					tipo_exp = self.valida_tipo(tipo, tipo_exp)

				else:
					print(
							"Erro Semantico. Variavel "+self.escopo+"."+node.value + " não foi declarada")
					exit(1)

			elif node.child[0].type == "num_inteiro":
				tipo_exp = self.valida_tipo("tipo_inteiro",tipo_exp)
			else:
				tipo_exp = self.valida_tipo("tipo_flutuante",tipo_exp)

		return tipo_exp


	def argumentos_chamada(self, node, lista_args):
		if node == None:
			return lista_args
		lista_args.append(self.expressao(node.child[0],""))
		if len(node.child) == 2:
			lista_args = self.argumentos_chamada(node.child[1], lista_args)
		return lista_args

	def expressao_condicao(self, node, tipo_exp):
		tipo = self.expressao_logica(node.child[0], tipo_exp)
		tipo_exp = self.valida_tipo(tipo, tipo_exp)
		return tipo_exp

	def expressao_logica(self, node, tipo_exp):
		tipo = self.expressao(node.child[0], tipo_exp)
		tipo_exp = self.valida_tipo(tipo, tipo_exp)
		tipo = self.expressao(node.child[1], tipo_exp)
		tipo_exp = self.valida_tipo(tipo, tipo_exp)
		return tipo_exp

	def expressao_normal(self, node, tipo_exp):
		tipo = self.expressao(node.child[0], tipo_exp)
		tipo_exp = self.valida_tipo(tipo, tipo_exp)
		tipo = self.expressao(node.child[1], tipo_exp)
		tipo_exp = self.valida_tipo(tipo, tipo_exp)
		return tipo_exp

	def expressao_unaria(self, node, tipo_exp):
		tipo = self.expressao(node.child[0], tipo_exp)
		tipo_exp = self.valida_tipo(tipo, tipo_exp)
		return tipo_exp		


	def valida_tipo(self, tipo_var,tipo_atual):
		if tipo_atual == "warning":
			return tipo_atual
		if tipo_var == "warning":
			return tipo_var
		elif tipo_atual == "":
			tipo_atual = tipo_var
		elif tipo_atual == "tipo_flutuante":
			if tipo_var == "tipo_inteiro":
				tipo_atual = "warning"
		elif tipo_atual == "tipo_inteiro":
			if tipo_var == "tipo_flutuante":
				tipo_atual = "warning"
		return tipo_atual

	def lastWarnings(self, simbolos):
		for s in simbolos.keys():
			valor = simbolos[s]
			if valor[0] == "funcao":
				if valor[3] == "nao_atribuido":
					print(
					"Warning Semantico. Funcao "+s+ " não foi usada")
			elif valor[0] == "declaracao":
				if valor[2] == "nao_atribuido":
					print(
					"Warning Semantico. Variavel "+s+ " não foi usada")

if __name__ == '__main__':
	import sys
	code = open(sys.argv[1])
	s = Semantica(code.read())
	s.lastWarnings(s.simbolos)
	pprint.pprint(s.simbolos, depth=3, width="200")
	#print("Tabela de Simbolos:", s.simbolos)


'''
informações sobre tipos nas variaveis

'''