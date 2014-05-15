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

class Primitive(Class):
  def __init__(self):
    pass

  def __contains__(self, field):
    return False

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

  def __str__(self):
    return 'List(' + ','.join(map(str,self.template_array)) + ')'

class TemplateDiv(Template):
  def __init__(self, template_list):
    self.template_list = template_list

  def __str__(self):
    return 'Div(' + str(self.template_list) + ')'

class TemplateIf(Template):
  def __init__(self, template_list_true, template_list_false):
    self.template_list_true = template_list_true
    self.template_list_false = template_list_false

  def __str__(self):
    return 'If(' + str(self.template_list_true) + ',' + str(self.template_list_false) + ')'

class TemplateVal(Template):
  def __init__(self, expr):
    self.expr = expr

  def __str__(self):
    return 'Val(' + str(self.expr) + ')'

class TemplateText(Template):
  def __init__(self, text):
    self.text = text

  def __str__(self):
    return 'Text(' + self.text + ')'

def fieldNameToJS(field_name):
  return ''.join(map(lambda word: word[0] + word[1:], field_name.split('_')))

class CommonFieldRef(object):
  def __init__(self, base_class, field_chain):
    self.base_class = base_class
    self.field_chain = field_chain
    self.type = base_class
    for field in field_chain:
      self.type = self.type[field]
    self.type = type(self.type)

  def emitJS(self):
    js = 'this'
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
    return expr

  def visit_expr(self, node, (expr)):
    print expr
    return expr

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

  def visit_if_element(self, node, (_1, true_element_list, false_element_list, _2)):
    if type(false_element_list) is list:
      false_element_list = false_element_list[0][1]
    else:
      false_element_list = TemplateList([])
    return TemplateIf(true_element_list, false_element_list)

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
