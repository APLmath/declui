import parsimonious

COMMON_GRAMMAR_TEXT = """
class_name      = ~"[A-Z][a-z]*"
field_name      = ~"[a-z]+(_[a-z]+)*"

int_literal     = ~"-?\\d+"
atom            = "this" / int_literal / ("(" expr ")")
expr            = or_test
or_test         = and_test / (or_test "||" and_test)
and_test        = not_test / (and_test "&&" not_test)
not_test        = comparison / ("!" not_test)
comparison      = a_expr / (a_expr ("<" / "<=" / ">" / ">=" / "==" / "!=") a_expr)
a_expr          = m_expr / (a_expr ("+" / "-") m_expr)
m_expr          = primary / (m_expr "*" primary)
primary         = atom / attribute_ref
attribute_ref   = primary "." field_name

WS = ~"[ \\t\\r\\n]+"
"""

DATA_GRAMMAR_TEXT = """
class_decl_list = WS? (class_decl WS?)*
class_decl      = "class " class_name " {" field_decl_list? "}"
field_decl_list = WS? field_decl (WS field_decl)* WS?
field_decl      = field_type WS field_name ";"
field_type      = "bool" / "int" / "string" / class_name
""" + COMMON_GRAMMAR_TEXT

TEMPLATE_GRAMMAR_TEXT = """
template_decl_list = WS? (template_decl WS?)*
template_decl      = "{template " class_name "." template_name "}" element_list "{/template}"
template_name      = ~"[a-z]+([A-Z][a-z]*)*"
element_list       = (div_element / if_element / val_element / text_element / WS)*
div_element        = "<div>" element_list "</div>"
if_element         = "{if}" element_list ("{else}" element_list)? "{/if}"
val_element        = "{{" expr "}}"
text_element       = ~"[A-Z 0-9]+"i
""" + COMMON_GRAMMAR_TEXT

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
<div>
  <div>
    {{this.name}}
    {if}
      Blah   
    {/if}
  </div>
</div>
{/template}
"""

DATA_GRAMMAR = parsimonious.grammar.Grammar(DATA_GRAMMAR_TEXT)
TEMPLATE_GRAMMAR = parsimonious.grammar.Grammar(TEMPLATE_GRAMMAR_TEXT)
