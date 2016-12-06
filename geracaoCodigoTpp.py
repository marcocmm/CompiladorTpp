from llvmlite import ir, binding
from ctypes import CFUNCTYPE, c_int32
import os
from analiseSemanticaTpp import *
from sys import exit

#from llvm.ee import ExecutionEngine
#from llvm.passes import (FunctionPassManager, PASS_INSTCOMBINE, PASS_GVN, PASS_REASSOCIATE, PASS_SIMPLIFYCFG, PASS_MEM2REG)

class Gen:
	#otimizar
	def __init__(self, code, optz=False, debug=True):

		binding.initialize()
		binding.initialize_native_target()
		binding.initialize_native_asmprinter()
		binding.load_library_permanently(os.getcwd() + '//funcoesC.so')
		self.ee = self.create_execution_engine()

		s = Semantica(code.read())
		self.tree = s.parser.ast
		self.module = ir.Module('program')
		self.simbolos = s.simbolos
		self.escopo = "global"
		self.builder = None
		self.func = None
		self.debug = debug
		self.leia = None
		self.imprime = None

		
		print("1")
	
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
			self.func = ir.Function(self.module,tipo_func,node.value)
			self.simbolos["global."+node.value].append(self.func)
			bb = self.func.append_basic_block('entry')
			self.builder = ir.IRBuilder(bb)
			self.gen_corpo(node.child[2])
			self.escopo = "global"


	def gen_corpo(self,node):
		if node == None:
			return
		self.gen_corpo(node.child[0])
		self.gen_detalhamento_funcao(node.child[1])

	def gen_detalhamento_funcao(self, node):
		if node.child[0].type == "atribuicao":
			self.gen_atribuicao(node.child[0])
		elif node.child[0].type == "leia":
			self.gen_leia(node.child[0])
		elif node.child[0].type == "escreva":
			self.gen_escreva(node.child[0])
		elif node.child[0].type == "declaracao":
			self.gen_declaracao_variavel(node.child[0])
		elif node.child[0].type == "chamada":
			self.gen_chamada_funcao(node.child[0])
		elif node.child[0].type == "repita":
			self.gen_repita(node.child[0])
		elif node.child[0].type == "condicao":
			self.gen_condicao(node.child[0])
		elif node.child[0].type == "retorna": 
			self.gen_retorna(node.child[0])

	def gen_atribuicao(self, node):
		var = None
		try:
			var = self.simbolos[self.escopo+"."+node.value][3]
			tipo = self.get_tipo(self.simbolos[self.escopo+"."+node.value][1])
		except:
			pass
		if var == None:
			try:
				pass
			except :
				pass
			if var == None:
				try:
					var = self.simbolos["global."+node.value][3]
					tipo = self.get_tipo(self.simbolos["global."+node.value][1])
				except:
					pass	
		res = self.gen_expressao(node.child[0], tipo)
		print(res)
		if res != None:
			self.builder.store(res, var)
		#tipo = self.expressao(node.child[0],"")
		#self.simbolos[self.escopo+"."+node.value] = [self.simbolos[self.escopo+"."+node.value][0], self.simbolos[self.escopo+"."+node.value][1],'atribuido']

	def gen_expressao(self, node, tipo):
		res = None
		if node.type == "expressao":
			res = self.gen_expressao(node.child[0], tipo)
		elif node.type == "expressao_meio":
			if node.child[0].type == "chamada":
				res = self.gen_chamada_funcao(node.child[0])
			elif node.child[0].type == "expressao_normal":
				res = self.gen_expressao_normal(node.child[0], tipo)
			elif node.child[0].type == "expressao_unaria":
				res = self.gen_expressao_unaria(node.child[0], tipo)
		else:
			if node.child[0].type == "id":
				print(node.value)
				return self.builder.load(self.simbolos[self.escopo+"."+node.child[0].value][3])
			else:
				return ir.Constant(tipo, node.child[0].value)
		return res

		

	def gen_expressao_normal(self, node, tipo):
		exp1 = self.gen_expressao(node.child[0], tipo)

		exp2 = self.gen_expressao(node.child[1], tipo)

		if node.value == "+":
			res = self.builder.fadd(exp1, exp2, name='add')
		elif node.value == "-":
			res = self.builder.fsub(exp1, exp2, name='sub')
		elif node.value == "*":
			res = self.builder.fmul(exp1, exp2, name='mult')
		elif node.value == "/":
			res = self.builder.fdiv(exp1, exp2, name='div')
		return res

	def gen_expressao_unaria(self, node, tipo):
		res = self.gen_expressao(node.child[0], tipo)
		if node.value == "+":
			return res
		else:
			return self.builder.fmul(res, ir.Constant(tipo, -1), name='mult')

	def gen_expressao_logica(self, node, tipo):
		tipo = self.get_tipo("tipo_flutuante")
		node = node.child[0]
		exp1 = self.gen_expressao(node.child[0], tipo)

		exp2 = self.gen_expressao(node.child[1], tipo)

		if node.value == "=":
			res = self.builder.icmp_signed("==", exp1, exp2, 'cmptmp')
		else:
			res = self.builder.icmp_signed(node.value, exp1, exp2, 'cmptmp')
		return res

	def gen_retorna(self, node):
		res = self.gen_expressao(node.child[0])
		self.builder.ret(res)


	def gen_chamada_funcao(self, node):
		nome_func = node.value
		func = self.builder.load(self.simbolos["global."+nome_func][4])
		lista_args = self.gen_argumentos_chamada_funcao(node.child[0], (), nome_func)
		return self.builder.call(func,lista_args,name="call")


	def gen_argumentos_chamada_funcao(self, node, lista_args, nome_func):
		real_arg = self.simbolos["global."+nome_func][2].pop(0)
		tipo = self.get_tipo(real_arg)
		valor = self.gen_expressao(node.child[0], tipo)
		lista_args = lista_args + (valor, )
		if len(node.child) == 2:
			lista_args = self.gen_argumentos_chamada_funcao(node.child[1], lista_args, nome_func)
		return lista_args

	def gen_condicao(self, node):
		cond = self.gen_expressao_logica(node.child[0])
		then_if = self.func.append_basic_block('then_if')
		if (len(node.child)== 3): 
			else_if = self.func.append_basic_block('else_if')
		end_if = self.func.append_basic_block('end_if')
		if (len(node.child)==3):
			self.builder.cbranch(cond, then_if, else_if)
		else:
			self.builder.cbranch(cond, then_if, end_if)
		self.builder.position_at_start(then_if)
		self.gen_corpo(node.child[1])
		self.builder.branch(end_if)
		if (len(node.child)==3):
			self.builder.position_at_start(else_if)
			self.gen_corpo(node.child[2])
			self.builder.branch(end_if)
		self.builder.position_at_start(end_if)

	def gen_repita(self, node):
		repeat = self.func.append_basic_block('repeat')
		end_repeat = self.func.append_basic_block('end_repeat')
		self.builder.branch(repeat)
		self.builder.position_at_start(repeat)
		self.gen_corpo(node.child[0])
		cond = self.gen_expressao_logica(node.child[1])
		self.builder.cbranch(cond, end_repeat, repeat)
		self.builder.position_at_start(end_repeat)

	def gen_leia(self, node):
		leia_t = ir.FunctionType(ir.IntType(32), [])
		self.leia = ir.Function(self.module, leia_t, 'leia')
		x = self.builder.call(self.leia, [])
		res = ir.Constant(ir.DoubleType(), x)
		self.builder.ret(res)
		self.mod = self.compile_ir()
		func_ptr = self.ee.get_function_address("leia")
		cfunc = CFUNCTYPE(c_int32)(func_ptr)
		retval = cfunc()

	def gen_escreva(self, node):
		imprime_t = ir.FunctionType(ir.VoidType(), [ir.IntType(32)])
		self.imprime = ir.Function(self.module, imprime_t, 'imprime')
		x = self.gen_expressao(node.child[0])
		self.builder.call(self.imprime, [x])
		self.mod = self.compile_ir()
		func_ptr = self.ee.get_function_address("imprime")
		cfunc = CFUNCTYPE(c_int32)(func_ptr)
		retval = cfunc()


	def get_tipo(self, tipo):
		if(tipo == "tipo_inteiro"):
			return ir.IntType(32)
		else:
			return ir.DoubleType()
	def create_execution_engine(self):
		target = binding.Target.from_default_triple()
		target_machine = target.create_target_machine()
		backing_mod = binding.parse_assembly("")
		engine = binding.create_mcjit_compiler(backing_mod, target_machine)
		return engine

		binding.load_library_permanently("//funcoesC.so")
	def compile_ir(self):
		self.mod = binding.parse_assembly(str(self.module))
		self.mod.verify()
		self.ee.add_module(self.mod)
		self.ee.finalize_object()
		return self.mod

if __name__ == '__main__':
	import sys
	code = open(sys.argv[1])
	driver = Gen(code)
	pprint.pprint(driver.simbolos, depth=3, width="300")
