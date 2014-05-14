import grammar

class ClassDecl(object):
  def __init__(self, class_decl_tree):
    self.__class_decl_tree = class_decl_tree
    self.name = class_decl_tree.children[1].text

  def finishSetup(self, classes):
    pass

class Generator(object):
  def __init__(self, data_text, template_text):
    self.classes = {}

    # Parse the data model.
    try:
      tree = grammar.DATA_GRAMMAR.parse(data_text)

      print "ASDF"
      for class_decl_tree in map(lambda node: node.children[0], tree.children[1]):
        class_decl = ClassDecl(class_decl_tree)
        self.classes[class_decl.name] = class_decl
    except Exception as e:
      raise e