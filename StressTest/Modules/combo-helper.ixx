use "helpers.ixx"
use "do-helper.ixx"

function combo_report name
- greeting = greet(name)
- ram = get_ram_info()
- return greeting + " | " + ram
