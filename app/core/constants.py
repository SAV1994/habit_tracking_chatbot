USER_STATES = {
    'UN'
}

transitions = [
    {'trigger': 'select_pizza', 'source': 'start', 'dest': 'choosing_pizza'},
    {'trigger': 'add_topping', 'source': 'choosing_pizza', 'dest': 'choosing_toppings'},
    {'trigger': 'remove_topping', 'source': 'choosing_toppings', 'dest': 'choosing_pizza'},
    {'trigger': 'checkout', 'source': 'choosing_toppings', 'dest': 'checkout'},
    {'trigger': 'cancel', 'source': '*', 'dest': 'start'},
]