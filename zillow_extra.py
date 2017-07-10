

import pandas as pd
import zillow_functions as zl
import time

def get_tax(TRA, tax_df):

    tax = "NA"

    try:
        # col 1 is TRA
        tra_cats = tax_df.loc[tax_df[1] == TRA]

        tax = tra_cats[3].sum()

    except:
        pass

    return tax

def check_offmarket(soup_obj):
    try:

        tip_txt = soup_obj.find(
                "span", {"data-target-id" : "nfs-tip-hdp"}).get_text().strip()

        if tip_txt == "Off Market":
            print "got an offmarket property"
            return True
    except:
        # didn't find offmarket
        return False

scraped_csv = '2017-06-24_102359.csv'

property_df = pd.read_csv(scraped_csv)


# read tax rate csv
tax_csv = 'TRA-2016-2017.csv'
tax_df = pd.read_csv(tax_csv, header=None)


# add some more columns
new_cols = ['parcel',
            'tax_rate',
            'zestimate',
            'rent_zestimate',
            'units']

for col in new_cols:
    property_df[col] = property_df.index


# create new df with filtered results
new_df = pd.DataFrame(columns = property_df.columns.values)


start_time = time.time()
for n in range(len(property_df)):

    # skip foreclosures for now (price is NA)
    if property_df.loc[n]['price'] == 'NA':
        property_df.loc[n, new_cols] = ['NA']*len(new_cols)
        continue

    soup = zl.get_soup(property_df.loc[n]['url'])

    # skip properties which are now off market
    if check_offmarket(soup):
        property_df.loc[n, new_cols] = ['OM']*len(new_cols)
        continue

    extra_data = []

    parcel_num = zl.get_parcel(soup)
    if parcel_num == "NA":
        continue

    extra_data.append(parcel_num)

    TRA = zl.get_TRA(parcel_num)

    # now lookup full tax rate using TRA code

    full_tax = get_tax(TRA, tax_df)
    extra_data.append(full_tax)


    zestimate, rent_zestimate = zl.get_zestimates(soup)
    extra_data.append(zestimate)
    extra_data.append(rent_zestimate)


    extra_data.append(zl.get_units(soup))

    property_df.loc[n, new_cols] = extra_data

    
    property_df.loc[n, 'sqft'] = zl.get_sqft2(soup)

    # todo: add bed/baths

    # Append valid obs to new df
    new_df.loc[len(new_df.index)] = property_df.loc[n]


    print n

end_time = time.time()
new_df.to_csv('extra.csv', index = False)

print "total time", end_time - start_time






