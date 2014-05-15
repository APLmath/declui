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
    {{this.home_address.city}}
    {{!this.is_intern>this.is_intern}}
    {if}
      Blah
    {else}
      {if}
        Deep
      {/if}
    {/if}
  </div>
</div>
{/template}
"""

a = grammar.DATA_GRAMMAR.parse(SAMPLE_DATA)
b = grammar.TEMPLATE_GRAMMAR.parse(SAMPLE_TEMPLATE)

g = generator.Generator(SAMPLE_DATA, SAMPLE_TEMPLATE)