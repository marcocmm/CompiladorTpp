from llvmlite import ir

from analiseSemanticaTpp import *
from analiseSintaticaTpp import *
from sys import exit
#from llvm.ee import ExecutionEngine
#from llvm.passes import (FunctionPassManager, PASS_INSTCOMBINE, PASS_GVN, PASS_REASSOCIATE, PASS_SIMPLIFYCFG, PASS_MEM2REG)

class Gen:
	#otimizar
	def __init__(self, code, optz=False, debug=True):
		s = Semantica(code.read())
		self.tree = s.parser.ast
		self.module = ir.Module('program')
		self.simbolos = s.simbolos
		self.escopo = "global"
		self.builder = None
		self.func = None
		self.debug = debug      
		#self.printf_f = Function.new(self.module, Type.function(Type.float(), [Type.float()]), "printf_f")
		#self.scanf_f = Function.new(self.module, Type.function(Type.float(), []), "scanf_f")
		
		self.gen_inicio(self.tree)
		#self.builder.ret(Constant.int(Type.int(), 0))

		print('\n\n;=== Código LLVM final ===')
		if(optz==True):
			print("----SEM OTIMIZAÇÃO----\n",self.module)
			self.passes.run(self.func)
			print("----COM OTIMIZAÇÃO----\n",self.module)
		else:
			print(self.module)


	def gen_inicio(self, node):
		if node.type == "top":
				
			if len(node.child) == 1:
				self.gen_codigo(node.child[0])
			else:
				self.gen_inicio(node.child[0])
				self.gen_codigo(node.child[1])

	def gen_codigo(self, node):
		if node.child[0].type == "declaracao":
			self.gen_declaracao_variavel(node.child[0])
		else:
			self.gen_declaracao_funcao(node.child[0])
			

	def gen_declaracao_variavel(self, node):
		tipo = self.get_tipo(node.child[0].type)
		if (self.escopo == "global"):
			a = ir.GlobalVariable(self.module,tipo, name = node.value)
			self.simbolos[self.escopo+"."+node.value].append(a)
			#possivelmente errado
		else:
			var = self.builder.alloca(tipo, name=node.value)
			self.simbolos[self.escopo+"."+node.value].append(var)

						

	def gen_declaracao_funcao(self, node):
			str_args = self.simbolos[self.escopo+"."+node.value][2]
			self.escopo = node.value
			return_type = self.get_tipo(node.child[0].type)

			args_type = ()
			for a in str_args:
				args_type = args_type + (self.get_tipo(a),)

			tipo_func = ir.FunctionType(return_type,args_type)
			func = ir.Function(self.module,tipo_func,node.value)
			self.simbolos["global."+node.value].append(func)
			bb = func.append_basic_block('entry')
			self.builder = ir.IRBuilder(bb)
			self.gen_corpo_funcao(node.child[2])

			self.escopo = "global"


	def gen_corpo_funcao(self,node):
		if node == None:
			return
		self.gen_corpo_funcao(node.child[0])
		self.gen_detalhamento_funcao(node.child[1])

	def gen_detalhamento_funcao(self, node):
		if node.child[0].type == "atribuicao":
			self.gen_atribuicao(node.child[0])
		#elif node.child[0].type == "leia":
			#self.gen_leia(node.child[0])
		#elif node.child[0].type == "escreva":
			#self.gen_escreva(node.child[0])
		elif node.child[0].type == "declaracao":
			self.gen_declaracao_variavel(node.child[0])
		elif node.child[0].type == "chamada":
			self.gen_chamada_funcao(node.child[0])
		#elif node.child[0].type == "repita":
			#self.gen_repita(node.child[0])
		#elif node.child[0].type == "condicao":
			#self.gen_condicao(node.child[0])
		#elif node.child[0].type == "retorna":expressao
			#self.gen_retorna(node.child[0])

	def gen_atribuicao(self, node):
		res = self.gen_expressao(node.child[0])
		if res != None:
			var = self.simbolos[self.escopo+"."+node.value][3]
			self.builder.store(res, var)
		#tipo = self.expressao(node.child[0],"")
		#self.simbolos[self.escopo+"."+node.value] = [self.simbolos[self.escopo+"."+node.value][0], self.simbolos[self.escopo+"."+node.value][1],'atribuido']

	def gen_expressao(self, node):
		res = None
		if node.type == "expressao":
			res = self.gen_expressao(node.child[0])
		elif node.type == "expressao_meio":
			if node.child[0].type == "chamada":
				res = self.gen_chamada_funcao(node.child[0])
			elif node.child[0].type == "expressao_normal":
				res = self.gen_expressao_normal(node.child[0])
			elif node.child[0].type == "expressao_unaria":
				res = self.gen_expressao_unaria(node.child[0])
		
		else:
			if node.child[0].type == "id":
				print(node.value)
				return self.builder.load(self.simbolos[self.escopo+"."+node.child[0].value][3])
			elif node.child[0].type == "num_inteiro":
				return ir.Constant(ir.IntType(32), node.child[0].value)
			else:
				return ir.Constant(ir.DoubleType(), node.child[0].value)
		return res

		

	def gen_expressao_normal(self, node):
		exp1 = self.gen_expressao(node.child[0])

		exp2 = self.gen_expressao(node.child[1])
		print(exp2)

		if node.value == "+":
			res = self.builder.fadd(exp1, exp2, name='add')
		elif node.value == "-":
			res = self.builder.fsub(exp1, exp2, name='sub')
		elif node.value == "*":
			res = self.builder.fmul(exp1, exp2, name='mult')
		elif node.value == "/":
			res = self.builder.fdiv(exp1, exp2, name='div')


		return res

	def gen_expressao_unaria(self, node):
		res = self.gen_expressao(node.child[0])
		if node.value == "+":
			return res
		else:
			return self.builder.fmul(res, ir.Constant(ir.IntType(32), -1), name='mult')

	def gen_chamda_funcao(self, node):


		real_args = self.simbolos["global."+node.value][2]

		lista_args = self.argumentos_chamada(node.child[0], [])
		self.simbolos["global."+node.value][3] = "atribuido"

	def gen_argumentos_chamda_funcao(self, node):
		pass
		lista_args.append(self.expressao(node.child[0],""))
		if len(node.child) == 2:
			lista_args = self.argumentos_chamada(node.child[1], lista_args)

	def gen_block(self):
		block = self.func.append_basic_block('entry')
		self.builder = ir.IRBuilder(block)

	def get_tipo(self, tipo):
		if(tipo == "tipo_inteiro"):
			return ir.IntType(32)
		else:
			return ir.DoubleType()

if __name__ == '__main__':
	import sys
	code = open(sys.argv[1])
	driver = Gen(code)
	pprint.pprint(driver.simbolos, depth=3, width="300")
