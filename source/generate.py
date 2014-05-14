import parsimonious

DATA_GRAMMAR = """
class_decl_list = WS? class_decl (WS class_decl)* WS?
class_decl      = "class" WS class_name WS "{" field_decl_list? "}"
class_name      = ~"[A-Z][a-z]*"
field_decl_list = WS? field_decl (WS field_decl)* WS?
field_decl      = field_type WS field_name ";"
field_type      = "bool" / "int" / "string" / class_name
field_name      = ~"[a-z]+(_[a-z]+)*"

WS = ~"[ \\t\\r\\n]+"
"""

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

GRAMMAR = parsimonious.grammar.Grammar(DATA_GRAMMAR)
