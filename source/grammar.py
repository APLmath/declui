import parsimonious

COMMON_GRAMMAR_TEXT = """
class_name      = ~"[A-Z][a-z]*"
field_name      = ~"[a-z]+(_[a-z]+)*"

int_literal     = ~"-?\\d+"
atom            = field_ref / int_literal / paren_expr
field_ref       = "this" ("." field_name)+
paren_expr      = "(" expr ")"
expr            = and_test ("||" and_test)*
and_test        = not_test ("&&" not_test)*
not_test        = comparison / ("!" not_test)
comparison      = a_expr (("<" / "<=" / ">" / ">=" / "==" / "!=") a_expr)*
a_expr          = m_expr (("+" / "-") m_expr)*
m_expr          = atom ("*" atom)*

WS = ~"[ \\t\\r\\n]+"
"""

DATA_GRAMMAR_TEXT = """
class_decl_list = WS? (class_decl WS?)*
class_decl      = "class " class_name " {" field_decl_list? "}"
field_decl_list = WS? (field_decl WS?)*
field_decl      = field_type " " field_name ";"
field_type      = "bool" / "int" / "string" / class_name
""" + COMMON_GRAMMAR_TEXT

TEMPLATE_GRAMMAR_TEXT = """
template_decl_list = WS? (template_decl WS?)*
template_decl      = "{template " class_name "." template_name "}" element_list "{/template}"
template_name      = ~"[a-z]+([A-Z][a-z]*)*"
element_list       = (div_element / if_element / val_element / text_element / WS)*
div_element        = "<div>" element_list "</div>"
if_element         = "{if " expr "}" element_list ("{else}" element_list)? "{/if}"
val_element        = "{{" expr "}}"
text_element       = ~"[A-Z 0-9]+"i
""" + COMMON_GRAMMAR_TEXT

INITIAL_GRAMMAR_TEXT = """
class_instance   = WS? class_name WS? "{" (field_instance)* WS? "}" WS?
field_instance   = WS? field_name WS? ":" WS? field_value
field_value      = class_instance / int_literal / bool_literal / string_literal
int_literal      = ~"-?\\d+"
bool_literal     = ~"(true|false)"
string_literal   = ~r'"[^"]*"'
class_name       = ~"[A-Z][a-z]*"
field_name       = ~"[a-z]+(_[a-z]+)*"

WS = ~"[ \\t\\r\\n]+"
"""

DATA_GRAMMAR = parsimonious.grammar.Grammar(DATA_GRAMMAR_TEXT)
TEMPLATE_GRAMMAR = parsimonious.grammar.Grammar(TEMPLATE_GRAMMAR_TEXT)
INITIAL_GRAMMAR = parsimonious.grammar.Grammar(INITIAL_GRAMMAR_TEXT)
