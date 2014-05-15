import grammar
import generator

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
  </div>
  <div>
    {if this.years_of_experience>4}
      Senior 
    {/if}
    {if this.is_intern}
      Engineering Intern
    {else}
      Engineer from {{this.home_address.city}}
    {/if}
  </div>
</div>
{/template}
"""

a = grammar.DATA_GRAMMAR.parse(SAMPLE_DATA)
b = grammar.TEMPLATE_GRAMMAR.parse(SAMPLE_TEMPLATE)

g = generator.Generator(SAMPLE_DATA, SAMPLE_TEMPLATE)

for c in g.classes:
  print g.classes[c].emitJS()