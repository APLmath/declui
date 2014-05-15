from parsimonious.nodes import NodeVisitor

import grammar

class Class(object):
  def __init__(self, class_decl_tree):
    self.__class_decl_tree = class_decl_tree
    self.name = class_decl_tree.children[1].text
    self.fields = {}

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
  pass

class Generator(object):
  def __init__(self, data_text, template_text):
    self.classes = {
      'bool': Bool(),
      'int': Int(),
      'string': String()
    }

    # Parse the data model.
    try:
      tree = grammar.DATA_GRAMMAR.parse(data_text)

      for class_decl_tree in map(lambda node: node.children[0], tree.children[1]):
        class_decl = Class(class_decl_tree)
        self.classes[class_decl.name] = class_decl
      for class_name in self.classes:
        self.classes[class_name].finishSetup(self.classes)
    except Exception as e:
      raise e