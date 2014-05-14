import parsimonious

COMMON_GRAMMAR = """
class_name      = ~"[A-Z][a-z]*"
field_name      = ~"[a-z]+(_[a-z]+)*"

WS = ~"[ \\t\\r\\n]+"
"""

DATA_GRAMMAR = """
class_decl_list = WS? class_decl (WS class_decl)* WS?
class_decl      = "class" WS class_name WS "{" field_decl_list? "}"
field_decl_list = WS? field_decl (WS field_decl)* WS?
field_decl      = field_type WS field_name ";"
field_type      = "bool" / "int" / "string" / class_name
""" + COMMON_GRAMMAR

TEMPLATE_GRAMMAR = """
template_decl_list = WS? template_decl (WS template_decl) * WS?
template_decl      = "{template " class_name "." template_name "}" WS? "{/template}"
template_name      = ~"[a-z]+([A-Z][a-z]*)*" 
""" + COMMON_GRAMMAR

SAMPLE_DATA = """
class Address {
  int number;
  string street;
  string city;
}

class Employee {
  string name;
  int years_of_experience;
  bool is_intern;
  Address home_address;
}
"""

SAMPLE_TEMPLATE = """
{template Employee.businessCard}
{/template}
"""

DATA_GRAMMAR = parsimonious.grammar.Grammar(DATA_GRAMMAR)
TEMPLATE_GRAMMAR = parsimonious.grammar.Grammar(TEMPLATE_GRAMMAR)
