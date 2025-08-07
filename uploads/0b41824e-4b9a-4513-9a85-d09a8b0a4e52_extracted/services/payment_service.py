
# Business logic patterns
def calculate_invoice_total(items, tax_rate):
    subtotal = sum(item['price'] for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax

def process_customer_payment(customer_id, amount):
    print(f"Processing payment of {amount} for customer {customer_id}")
    return {"status": "success"}
