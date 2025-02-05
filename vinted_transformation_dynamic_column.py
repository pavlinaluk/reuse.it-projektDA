'''Vinted Apify scraper dataset - Keboola transformation, solving the dynamical columns
with PL origin, which exist only if the product is from Poland
UNUSED at last due to Keboola limitations'''

import pandas as pd
import uuid

input_path = 'in/tables/Vinted_mango_kalhoty_zeny.csv'
output_path = 'out/tables/Vinted_Mango_kalhoty_zeny_test_PL_kod.csv'

# Define the expected data types
dtype = {
	"brand_name": str,
	"favourite_count": str,
	"id": str,  # Original column "id" to be renamed as "product_id"
	"size_title": str,
	"status": str,
	"title": str,
	"url": str
}

df = pd.read_csv(input_path, dtype=dtype)

# Rename columns
df = df.rename(columns={
	"brand_name": "brand_title",
	"id": "product_id",
	"size_title": "size",
	"status": "condition",
	"title": "name"
})

# Create the "price" column based on the availability of "total_item_price" or "conversion_seller_price"
if "total_item_price" in df.columns:
	df['price'] = df['total_item_price']
elif "total_item_price_amount" in df.columns:
	df['price'] = df['total_item_price_amount']
else:
	df['price'] = None  # Create an empty "price" column if neither source column is present

# Drop "total_item_price" and "conversion_seller_price" as they're now redundant
df = df.drop(columns=["total_item_price", "total_item_price_amount"], errors='ignore')

# Adding new columns
df['category'] = 'Ženy'
df['product'] = 'Kalhoty'
df['e_shop'] = 'Vinted'

# Adding the "delivery_from" column based on the presence of "PLN" in "conversion_seller_currency"
if 'conversion_seller_currency' in df.columns:
    df['delivery_from'] = df['conversion_seller_currency'].apply(lambda x: 'PL' if x == 'PLN' else 'CZ')
else:
    df['delivery_from'] = 'CZ'

# Generating a unique UUID for each row in a new column "database_id"
df['database_id'] = [str(uuid.uuid4()) for _ in range(len(df))]

# Define the final columns to retain
final_columns = [
	"brand_title", "favourite_count", "product_id",
	"price", "size", "condition", "name", "url", "category", "product",
	"e_shop", "delivery_from", "database_id"
]

# Select only columns that exist in the DataFrame
existing_columns = [col for col in final_columns if col in df.columns]
df = df[existing_columns]

# Final output
df.to_csv(output_path, index=False)
