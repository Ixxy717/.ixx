# Contact list searcher

contacts = "Alice Johnson", "Bob Smith", "Carol Williams", "David Brown", "Eve Anderson", "Frank Miller", "Grace Wilson", "Henry Taylor", "Iris Thompson", "Jack Robinson"

function search_contacts list, term
- found = 0
- say "Searching for '" + term + "':"
- loop each c in list
-- if c contains term
--- say "  Found: " + c
--- found = found + 1
- say "  Total matches: " + found + " / " + count(list)
- return found

m1 = search_contacts(contacts, "son")
say "---"
m2 = search_contacts(contacts, "li")
say "---"
m3 = search_contacts(contacts, "XYZ")
say "---"
say "Totals: " + m1 + " + " + m2 + " + " + m3 + " matches"
say "Sorted contacts, first: " + first(sort(contacts))
