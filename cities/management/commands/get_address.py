from django.core.management.base import BaseCommand
from cities.models import State, City
import requests
import bs4


class Command(BaseCommand):
    help = 'Populate the database with states and cities from the external API'

    def handle(self, *args, **kwargs):
        url = "https://amib.ir/weblog/wp-content/uploads/amib/iran-provinces-cities/"

        parser = "html.parser"

        data = requests.get(url).text

        soap = bs4.BeautifulSoup(data, parser)

        rows = soap.find_all("tr")
        result = []
        for i in rows:
            inner_list = []
            all_rows = i.find_all("td")
            for index, j in enumerate(all_rows):

                if "\n\n" not in j.text:
                    inner_list.append(j.text)

                if index == 1 and inner_list != []:
                    result.append(inner_list)

        result = sorted(result)

        ostan = set()
        for list_item in result:
            ostan.add(list_item[0])

        for item in sorted(ostan):
            State.objects.get_or_create(name=item)

        for city in result:
            this_city = city[1]
            this_ostan = city[0]
            ostan_in_db = State.objects.get(name=this_ostan)
            City.objects.get_or_create(name=this_city, state=ostan_in_db)

        self.stdout.write(self.style.SUCCESS('Successfully populated the database'))
