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

SAMPLE_INITIAL = """
Employee {
  name: "Andrew Lee"
  years_of_experience: 2
  is_intern: false
  home_address: Address{
    number: 271
    street: "Euler Street"
    city: "Berkeley"
  }
}
"""

g = generator.Generator(SAMPLE_DATA, SAMPLE_TEMPLATE)
print g.initializeWith('Employee.businessCard', SAMPLE_INITIAL)