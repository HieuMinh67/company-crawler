import argparse
from dataclasses import dataclass

import pandas as pd
import requests
import unidecode
from bs4 import BeautifulSoup

TAX_URL = "https://masothue.com"


@dataclass
class Company:
    tax_code: str
    name: str
    address_number: str
    street: str
    ward: str
    district: str
    province: str
    website: str
    facebook: str
    linkedin: str
    email: str
    phone_number: str
    other_contact_info: str

    @property
    def hyphenated_name(self):
        hyphenated = self.name.lower().replace(' ', '-').replace('.', '-')
        return unidecode.unidecode(hyphenated)  # remove Vietnamese accent

    def scrape(self):
        # Get data from tax page
        url = f'{TAX_URL}/{self.tax_code}-{self.hyphenated_name}'
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        phone_element = soup.find('td', {'itemprop': 'telephone'})
        if phone_element:
            self.phone_number = phone_element.text.strip()
            print(f'Phone number: {self.phone_number}')
        else:
            print('Phone number not found on page')

        presenter_element = soup.find('td', {'itemprop': 'name'})
        if presenter_element:
            self.other_contact_info = presenter_element.text.strip()
            print(f'presenter element: {self.other_contact_info}')
        else:
            print('presenter element not found on page')


def to_csv(companies: list[Company]) -> None:
    df = pd.DataFrame([vars(c) for c in companies])
    df.to_csv("companies.csv", index=True)


def importFromCSV(path: str, delimiter: str) -> list[Company]:
    df = pd.read_csv(path, delimiter=delimiter)
    for _, row in df.iterrows():
        print(row)
    df.columns = [c.strip() for c in df.columns]
    return [Company(
        tax_code=row['Tax code'],
        name=row['Company name'],
        address_number=row['Address number'],
        street=row['Street'],
        ward=row['Ward'],
        district=row['District'],
        province=row['Province'],
        website=row['Website'],
        facebook=row['Facebook'],
        linkedin=row['Linkedin'],
        email=row['Email'],
        phone_number=row['Phone number'],
        other_contact_info=row['Thông tin liên lạc khác'],
    ) for _, row in df.iterrows()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default='resource/data.csv', type=str)
    parser.add_argument("--delimiter", default=',', type=str)
    args = parser.parse_args()
    companies = importFromCSV(
        path=args.data,
        delimiter=args.delimiter
    )
    for cmp in companies:
        cmp.scrape()

    to_csv(companies)
