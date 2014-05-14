import grammar

def run(data_text, template_text):
  try:
    grammar.DATA_GRAMMAR.parse(data_text)
  except:
    pass