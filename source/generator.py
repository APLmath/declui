from parsimonious.nodes import NodeVisitor

import grammar

class Class(object):
  def __init__(self, class_decl_tree):
    self.__class_decl_tree = class_decl_tree
    self.name = class_decl_tree.children[1].text
    self.fields = {}
    self.templates = {}

  def __getitem__(self, field):
    return self.fields[field]

  def __contains__(self, field):
    return field in self.fields

  def finishSetup(self, classes):
    field_decl_list = self.__class_decl_tree.children[3]
    if len(field_decl_list.children) == 0:
      return
    for field_decl in map(lambda node: node.children[0], field_decl_list.children[0].children[1]):
      field_type = classes[field_decl.children[0].text]
      field_name = field_decl.children[2].text
      self.fields[field_name] = field_type

  def addTemplate(self, template_name, template):
    self.templates[template_name] = template

  def getTemplate(self, template_name):
    return self.templates[template_name]

  def emitJS(self):
    args = ', '.join(map(fieldNameToJS, self.fields.keys()))
    field_decls = '\n'.join(map(lambda field: '  this.' + field + ' = ' + field + ';', map(fieldNameToJS, self.fields.keys())))
    js = """
declui.%s = function(%s) {
%s
};
""" % (self.name, args, field_decls)
    for field in self.fields.keys():
      field = fieldNameToJS(field)
      js += """
declui.%s.prototype.get%s = function() {
  return this.%s;
};

declui.%s.prototype.set%s = function(%s) {
  this.%s = %s;
  declui.global.update();
};
""" % (self.name, field, field, self.name, field, field, field, field)
    for template in self.templates.keys():
      js += """
declui.%s.%s = %s;
""" % (self.name, template, self.templates[template].emitJS())
    return js

class Primitive(Class):
  def __init__(self):
    pass

  def __contains__(self, field):
    return False

  def emitJS(self):
    return ''

  def finishSetup(self, classes):
    pass

class Bool(Primitive):
  pass

class Int(Primitive):
  pass

class String(Primitive):
  pass

class Template(object):
  def emitJS(self):
    pass

class TemplateList(Template):
  def __init__(self, template_array):
    self.template_array = template_array

  def emitJS(self):
    return 'new declui.template.List([' + ','.join(map(lambda template: template.emitJS(), self.template_array)) + '])'

  def __str__(self):
    return 'List(' + ','.join(map(str,self.template_array)) + ')'

class TemplateDiv(Template):
  def __init__(self, template_list):
    self.template_list = template_list

  def emitJS(self):
    return 'new declui.template.Div(' + self.template_list.emitJS() + ')'

  def __str__(self):
    return 'Div(' + str(self.template_list) + ')'

class TemplateIf(Template):
  def __init__(self, bool_expr, template_list_true, template_list_false):
    self.bool_expr = bool_expr
    self.template_list_true = template_list_true
    self.template_list_false = template_list_false

  def emitJS(self):
    return 'new declui.template.If(function(state){ return ' + self.bool_expr.emitJS() + '; },' + self.template_list_true.emitJS() + ',' + self.template_list_false.emitJS() + ')'

  def __str__(self):
    return 'If(' + str(self.template_list_true) + ',' + str(self.template_list_false) + ')'

class TemplateVal(Template):
  def __init__(self, expr):
    self.expr = expr

  def emitJS(self):
    return 'new declui.template.Val(function(state){ return ' + self.expr.emitJS() + '; })'

  def __str__(self):
    return 'Val(' + str(self.expr) + ')'

class TemplateText(Template):
  def __init__(self, text):
    self.text = text

  def emitJS(self):
    return 'new declui.template.Text(' + repr(self.text) + ')'

  def __str__(self):
    return 'Text(' + self.text + ')'

def fieldNameToJS(field_name):
  return ''.join(map(lambda word: word[0].upper() + word[1:], field_name.split('_')))

class CommonFieldRef(object):
  def __init__(self, base_class, field_chain):
    self.base_class = base_class
    self.field_chain = field_chain
    self.type = base_class
    for field in field_chain:
      self.type = self.type[field]
    self.type = type(self.type)

  def emitJS(self):
    js = 'state'
    for field_name in self.field_chain:
      js += '.get' + fieldNameToJS(field_name) + '()'
    return js

  def getType(self):
    return self.type

class CommonIntLiteral(object):
  def __init__(self, value):
    self.value = value

  def emitJS(self):
    return self.value

  def getType(self):
    return Int

class CommonParenExpr(object):
  def __init__(self, expr):
    self.expr = expr

  def emitJS(self):
    return '(' + self.expr.emitJS() + ')'

  def getType(self):
    return self.expr.getType()

class CommonOrTest(object):
  def __init__(self, and_test1, and_test2):
    self.and_test1 = and_test1
    self.and_test2 = and_test2

  def emitJS(self):
    return self.and_test1.emitJS() + '||' + self.and_test2.emitJS()

  def getType(self):
    return Bool

class CommonAndTest(object):
  def __init__(self, not_test1, not_test2):
    self.not_test1 = not_test1
    self.not_test2 = not_test2

  def emitJS(self):
    return self.not_test1.emitJS() + '&&' + self.not_test2.emitJS()

  def getType(self):
    return Bool

class CommonNotTest(object):
  def __init__(self, comparison):
    self.comparison = comparison

  def emitJS(self):
    return '!(' + self.comparison.emitJS() + ')'

  def getType(self):
    return Bool

class CommonComparison(object):
  def __init__(self, a_expr1, op, a_expr2):
    self.a_expr1 = a_expr1
    self.op = op
    self.a_expr2 = a_expr2

  def emitJS(self):
    return self.a_expr1.emitJS() + self.op + self.a_expr2.emitJS()

  def getType(self):
    return Bool

class CommonAExpr(object):
  def __init__(self, m_expr1, op, m_expr2):
    print op
    self.m_expr1 = m_expr1
    self.op = op
    self.m_expr2 = m_expr2

  def emitJS(self):
    return self.m_expr1.emitJS() + self.op + self.m_expr2.emitJS()

  def getType(self):
    return Int

class CommonMExpr(object):
  def __init__(self, atom1, op, atom2):
    print op
    self.atom1 = atom1
    self.op = op
    self.atom2 = atom2

  def emitJS(self):
    return self.atom1.emitJS() + self.op + self.atom2.emitJS()

  def getType(self):
    return Int

class CommonVisitor(NodeVisitor):
  def __init__(self, base_class):
    self.base_class = base_class

  def visit_int_literal(self, node, (text)):
    return CommonIntLiteral(node.text)

  def visit_field_name(self, node, (text)):
    return node.text

  def visit_field_ref(self, node, (_, field_names)):
    return CommonFieldRef(self.base_class, map(lambda n: n[1], field_names))

  def visit_atom(self, node, (atom)):
    return atom[0]

  def visit_paren_expr(self, node, (_1, expr, _2)):
    return CommonParenExpr(expr)

  def visit_expr(self, node, (and_test, other_and_tests)):
    currentExpr = and_test
    for other_and_test in other_and_tests:
      currentExpr = CommonOrTest(currentExpr, other_and_test[1])
    return currentExpr

  def visit_and_test(self, node, (not_test, other_not_tests)):
    currentExpr = not_test
    for other_not_test in other_not_tests:
      currentExpr = CommonAndTest(currentExpr, other_not_test[1])
    return currentExpr

  def visit_not_test(self, node, (comparison)):
    comparison = comparison[0]
    if type(comparison) is list:
      return CommonNotTest(comparison[1])
    else:
      return comparison

  def visit_comparison(self, node, (a_expr, other_a_exprs)):
    currentExpr = a_expr
    for other_a_expr in other_a_exprs:
      currentExpr = CommonComparison(currentExpr, other_a_expr[0][0].text, other_a_expr[1])
    return currentExpr

  def visit_a_expr(self, node, (m_expr, other_m_exprs)):
    currentExpr = m_expr
    for other_m_expr in other_m_exprs:
      currentExpr = CommonAExpr(currentExpr, other_m_expr[0][0].text, other_m_expr[1])
    return currentExpr

  def visit_m_expr(self, node, (atom, other_atoms)):
    currentExpr = atom
    for other_atom in other_atoms:
      currentExpr = CommonMExpr(currentExpr, other_atom[0][0].text, other_atom[1])
    return currentExpr

  def visit_WS(self, node, _):
    return None

class TemplateVisitor(CommonVisitor):
  def visit_template_decl(self, node, (_1, class_name, _2, template_name, _3, element_list, _4)):
    return (class_name.text, template_name.text, str(element_list))

  def visit_template_decl_list(self, node, (_1, template_decls)):
    return map(lambda n: n[0], template_decls)

  def visit_element_list(self, node, (element_list)):
    return TemplateList([element[0] for element in element_list if element[0]])

  def visit_div_element(self, node, (_1, element_list, _2)):
    return TemplateDiv(element_list)

  def visit_if_element(self, node, (_1, expr, _2, true_element_list, false_element_list, _3)):
    if type(false_element_list) is list:
      false_element_list = false_element_list[0][1]
    else:
      false_element_list = TemplateList([])
    return TemplateIf(expr, true_element_list, false_element_list)

  def visit_val_element(self, node, (_1, expr, _2)):
    return TemplateVal(expr)

  def visit_text_element(self, node, (text)):
    return TemplateText(node.text)

  def generic_visit(self, node, visited_children):
    return visited_children or node

class TemplateVisitorFirstPass(NodeVisitor):
  def visit_template_decl_list(self, node, (_1, template_decls)):
    return map(lambda n: n[0], template_decls)

  def visit_template_decl(self, node, (_1, class_name, _2, template_name, _3, element_list, _4)):
    return (class_name.text, template_name.text, element_list)

  def visit_element_list(self, node, (element_list)):
    return node

  def generic_visit(self, node, visited_children):
    return visited_children or node

class Generator(object):
  def __init__(self, data_text, template_text):
    self.classes = {
      'bool': Bool(),
      'int': Int(),
      'string': String()
    }

    # Parse the data model.
    tree = grammar.DATA_GRAMMAR.parse(data_text)

    for class_decl_tree in map(lambda node: node.children[0], tree.children[1]):
      class_decl = Class(class_decl_tree)
      self.classes[class_decl.name] = class_decl
    for class_name in self.classes:
      self.classes[class_name].finishSetup(self.classes)

    # Parse the templates.
    tree = grammar.TEMPLATE_GRAMMAR.parse(template_text)

    templateNodes = {}

    for (class_name, template_name, templateNode) in TemplateVisitorFirstPass().visit(tree):
      templateNodes[class_name, template_name] = templateNode

    for class_name, template_name in templateNodes:
      self.classes[class_name].addTemplate(template_name,
          TemplateVisitor(self.classes[class_name]).visit(templateNode))

    self.boilerplateJS = ''
    for c in self.classes:
      self.boilerplateJS += self.classes[c].emitJS()

  def initializeWith(self, template_name, initialText):
    tree = grammar.INITIAL_GRAMMAR.parse(initialText)
    return self.boilerplateJS + ("""
declui.global.initialize(declui.%s, %s);
""" % (template_name, InitialVisitor(self.classes).visit(tree)))

class InitialVisitor(NodeVisitor):
  def __init__(self, classes):
    self.classes = classes

  def visit_class_instance(self, node, (_1, class_name, _2, _3, field_instances, _4, _5, _6)):
    value_dict = {name: value for name, value in field_instances}
    return "new declui.%s(%s)" % (class_name, ', '.join(map(lambda field_name: value_dict[field_name], self.classes[class_name].fields.keys())))

  def visit_field_instance(self, node, (_1, field_name, _2, _3, _4, field_value)):
    return (field_name, field_value)

  def visit_field_value(self, node, (value)):
    return value[0]

  def pass_the_literal(self, node, (literal)):
    return node.text

  def generic_visit(self, node, visited_children):
    return visited_children

  visit_int_literal = visit_bool_literal = visit_string_literal = visit_class_name = visit_field_name = pass_the_literal