from decimal import Decimal
input_tokens = 100
output_tokens = 50
user_price_input_usd_pm = 0.150
user_price_output_usd_pm = 0.600
                                                                                                                                                          
input_cost = Decimal(str(input_tokens)) * Decimal(str(user_price_input_usd_pm)) / Decimal('1000000')
output_cost = Decimal(str(output_tokens)) * Decimal(str(user_price_output_usd_pm)) / Decimal('1000000')
total_cost = float(input_cost + output_cost)

print(f'Input tokens: {input_tokens}')
print(f'Output tokens: {output_tokens}')
print(f'Input cost: ${input_cost:.8f}')
print(f'Output cost: ${output_cost:.8f}')
print(f'Total cost: ${total_cost:.8f}')